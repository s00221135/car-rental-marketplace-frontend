import json, random, boto3
from datetime import datetime

dynamodb       = boto3.resource('dynamodb')
bookings_table = dynamodb.Table('Bookings')
sqs            = boto3.client('sqs')

SQS_QUEUE_URL  = "https://sqs.us-east-1.amazonaws.com/474242622840/RentalNotificationQueue"

def process_booking(user_id: str, car_id: str, qty: int) -> dict:
    """Creates the booking record and pushes a message to SQS."""
    booking_id = str(random.randint(100000, 999999))
    now        = datetime.utcnow().isoformat()

    bookings_table.put_item(Item={
        "BookingId"    : booking_id,
        "UserId"       : user_id,
        "CarId"        : car_id,
        "Quantity"     : qty,
        "PaymentStatus": "confirmed",
        "Timestamp"    : now
    })

    sqs.send_message(
        QueueUrl    = SQS_QUEUE_URL,
        MessageBody = json.dumps({
            "bookingId": booking_id,
            "userId"   : user_id,
            "carId"    : car_id,
            "quantity" : qty
        })
    )

    return {
        "bookingId": booking_id,
        "userId"   : user_id,
        "carId"    : car_id,
        "quantity" : qty,
        "status"   : "APPROVED"     # <── what the Choice state checks
    }

def lambda_handler(event, context):
    """
    • If invoked by API Gateway  → event contains "body" (string JSON).
    • If invoked by Step Functions → event **is already** the JSON object.
    """
    print("🛈 RAW EVENT:", json.dumps(event))

    # ------- Determine invocation source ----------------------------------
    if isinstance(event, dict) and "body" in event:         # ⇦ API Gateway
        try:
            payload = json.loads(event["body"] or "{}")
        except Exception:
            return {"statusCode":400, "body": "Invalid JSON"}
        api_gateway = True
    else:                                                   # ⇦ Step Functions
        payload      = event
        api_gateway  = False

    # ------- Extract fields -----------------------------------------------
    user_id = payload.get("UserId") or payload.get("userId")
    car_id  = payload.get("CarId")  or payload.get("carId")
    qty     = int(payload.get("Quantity", 1))

    if not (user_id and car_id):
        msg = {"message": "Missing UserId or CarId"}
        return {"statusCode":400, "body": json.dumps(msg)} if api_gateway else msg

    # ------- “Process payment”  (dummy) -----------------------------------
    # Here you could call Stripe, etc.  We’ll approve everything ≤ 30 days.
    if qty > 30:
        result = {"status": "DECLINED", "reason": "Limit 30 days"}
    else:
        result = process_booking(user_id, car_id, qty)

    # ------- Return --------------------------------------------------------
    if api_gateway:
        # Keep the envelope so your React front‑end works
        return {
            "statusCode": 200 if result["status"] == "APPROVED" else 402,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(result)
        }
    else:
        # Step Functions gets the plain object → $.status exists!
        return result