import json
import boto3
from boto3.dynamodb.conditions import Attr
import decimal

dynamodb = boto3.resource('dynamodb')
cars_table = dynamodb.Table('Cars')

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super().default(o)

def lambda_handler(event, context):
    q = event.get("queryStringParameters", {}).get("q", "").strip().lower()
    
    if q:
        # filter on make or model containing the query
        resp = cars_table.scan(
            FilterExpression=Attr("make").contains(q) | Attr("model").contains(q)
        )
    else:
        # no query → return *all*
        resp = cars_table.scan()
    
    items = resp.get("Items", [])
    
    return {
        "statusCode": 200,
        "body": json.dumps({"cars": items}, cls=DecimalEncoder),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        }
    }
