import json
from decimal import Decimal
import boto3

# AWS clients/resources
sns        = boto3.client('sns')
dynamodb   = boto3.resource('dynamodb')
cars_table = dynamodb.Table('Cars')
cart_table = dynamodb.Table('ShoppingCart')

# Your SNS Topic ARN
SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:474242622840:BookingNotifications"

def lambda_handler(event, context):
    for record in event["Records"]:
        msg = json.loads(record["body"])
        booking_id = msg.get("bookingId", "UNKNOWN")
        user_id    = msg.get("userId")
        car_id     = msg.get("carId")
        
        if not (user_id and car_id):
            print("⚠️  Missing userId/carId, skipping:", msg)
            continue

        # 🔍 ALWAYS pull the real Quantity (rental days) from the ShoppingCart table:
        try:
            cart_resp = cart_table.get_item(
                Key={"UserId": user_id, "CarId": car_id}
            )
            qty = int(cart_resp["Item"]["Quantity"])
            print(f"🎯 True qty from ShoppingCart: {qty}")
        except Exception as e:
            print("❌ Failed to load Quantity from ShoppingCart, defaulting to 1:", e)
            qty = 1

        # Fetch the car details
        try:
            car = cars_table.get_item(Key={"CarId": car_id})["Item"]
        except Exception as e:
            print("❌ Failed to fetch car details:", e)
            car = {}

        make  = car.get("make",  "Unknown")
        model = car.get("model", "")
        year  = car.get("year",  "N/A")
        rate  = float(car.get("price", 0))
        total = rate * qty

        # Build the email
        email_body = (
            f"{make} {model} ({year})\n"
            f"Rental Days: {qty} — Daily Rate: ${rate:.2f}/day — Total: ${total:.2f}\n"
            f"Booking ID: {booking_id}"
        )
        print("✉️  Publishing to SNS:", email_body.replace("\n", " | "))

        # Send it
        sns.publish(
            TopicArn = SNS_TOPIC_ARN,
            Message  = email_body,
            Subject  = "Your Car Rental Booking"
        )

    return {"statusCode": 200}
