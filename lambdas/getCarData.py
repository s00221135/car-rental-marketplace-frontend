import json
import time
import boto3
from boto3.dynamodb.conditions import Key
import decimal

# Initialize DynamoDB resources for both Cars and car_cache tables
dynamodb = boto3.resource('dynamodb')
cars_table = dynamodb.Table('Cars')
cache_table = dynamodb.Table('car_cache')

# Custom JSON encoder to handle DynamoDB Decimal objects
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

def lambda_handler(event, context):
    # Expecting input with a JSON body containing "CarId"
    try:
        data = json.loads(event.get("body", "{}"))
    except Exception:
        data = event

    car_id = data.get("CarId")
    if not car_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "CarId must be provided."}),
            "headers": {"Content-Type": "application/json"}
        }

    current_time = int(time.time())
    
    # Check if the car data exists in cache and has not expired
    try:
        cache_response = cache_table.get_item(Key={"CarId": car_id})
        cache_item = cache_response.get("Item")
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
            "headers": {"Content-Type": "application/json"}
        }
    
    if cache_item and cache_item.get("expiry", 0) > current_time:
        # Cache hit: return cached car data
        result = {"source": "cache", "data": cache_item["data"]}
        print("Cache hit:", result)
    else:
        # Cache miss: retrieve car data from the Cars table
        try:
            car_response = cars_table.get_item(Key={"CarId": car_id})
            car_data = car_response.get("Item")
            if not car_data:
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": "Car not found."}),
                    "headers": {"Content-Type": "application/json"}
                }
        except Exception as e:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"}
            }
        
        # Cache the data with a TTL of 5 minutes (300 seconds)
        expiry_time = current_time + 300  
        try:
            cache_table.put_item(Item={
                "CarId": car_id,
                "data": car_data,
                "expiry": expiry_time
            })
        except Exception as e:
            print("Error writing to cache:", e)
        
        result = {"source": "api", "data": car_data}
        print("Cache miss. Data from Cars table:", result)
    
    return {
        "statusCode": 200,
        "body": json.dumps(result, cls=DecimalEncoder),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        }
    }
