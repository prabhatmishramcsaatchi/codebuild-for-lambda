import json

def lambda_handler(event, context):
    a=10
    b=20
    c=30
    d=30
    print("new code part")
    print(a+b)
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!....... (Modified v0.2')
    }
