import json

def lambda_handler(event, context):
    a=10
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!....... (Modified v0.2')
    }
