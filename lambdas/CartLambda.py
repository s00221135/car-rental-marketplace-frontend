import json
import boto3
import decimal
from boto3.dynamodb.conditions import Key

# Initialize DynamoDB resources
dynamodb = boto3.resource('dynamodb')
cart_table = dynamodb.Table('ShoppingCart')
cars_table = dynamodb.Table('Cars')  # New: Reference the Cars table for enrichment

# Custom JSON encoder to handle Decimal objects from DynamoDB
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

def lambda_handler(event, context):
    try:
        method = event.get("httpMethod", "GET")
        
        if method == "POST":
            # Add item to cart
            data = json.loads(event["body"])
            user_id = data["UserId"]
            car_id = data["CarId"]
            quantity = data.get("Quantity", 1)
            cart_table.put_item(Item={"UserId": user_id, "CarId": car_id, "Quantity": quantity})
            response = {"message": "Item added to cart."}
        
        elif method == "DELETE":
            # Remove item from cart: expects UserId and CarId in query string
            params = event.get("queryStringParameters", {})
            user_id = params.get("UserId")
            car_id = params.get("CarId")
            if not user_id or not car_id:
                response = {"error": "UserId and CarId must be provided."}
            else:
                cart_table.delete_item(
                    Key={
                        "UserId": user_id,
                        "CarId": car_id
                    }
                )
                response = {"message": "Item removed from cart."}
        
        else:
            # GET: Retrieve cart items for the given user and enrich with car details
            user_id = event.get("queryStringParameters", {}).get("UserId", "")
            if user_id:
                # Query for cart items using the user ID as the partition key
                response_data = cart_table.query(KeyConditionExpression=Key('UserId').eq(user_id))
                items = response_data.get("Items", [])
                
                # Enrich each cart item with car details from the Cars table
                enriched_items = []
                for item in items:
                    car_id = item.get("CarId")
                    car_response = cars_table.get_item(Key={"CarId": car_id})
                    car_details = car_response.get("Item", {})
                    # Merge cart item with car details
                    enriched_item = { **item, **car_details }
                    enriched_items.append(enriched_item)
            else:
                enriched_items = []
            response = {"message": "Cart retrieved.", "cartItems": enriched_items}
        
        return {
            "statusCode": 200,
            "body": json.dumps(response, cls=DecimalEncoder),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true"
            }
        }
    
    except Exception as e:
        print("Error in CartLambda:", e)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}, cls=DecimalEncoder),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true"
            }
        }
