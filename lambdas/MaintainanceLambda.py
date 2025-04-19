import json
import boto3
import datetime
import decimal

# Initialize resources for DynamoDB and S3
dynamodb = boto3.resource('dynamodb')
bookings_table = dynamodb.Table('Bookings')
s3 = boto3.client('s3')

# Set your archive bucket name
BUCKET_NAME = "car-rental-archive"

# Define a custom JSON encoder to handle Decimal objects from DynamoDB
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

def lambda_handler(event, context):
    try:
        # Scan all items in the Bookings table
        response = bookings_table.scan()
        items = response.get("Items", [])
        
        if items:
            # Generate a timestamp to use in the S3 key
            now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")
            key = f"archive/bookings_archive_{now}.json"
            archive_body = json.dumps(items, cls=DecimalEncoder)
            
            # Write the archived data to S3
            s3.put_object(Bucket=BUCKET_NAME, Key=key, Body=archive_body)
            print(f"Archived {len(items)} bookings to s3://{BUCKET_NAME}/{key}")
        else:
            print("No bookings to archive.")
            
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Maintenance task completed"})
        }
    except Exception as e:
        print("Error in MaintenanceLambda:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
