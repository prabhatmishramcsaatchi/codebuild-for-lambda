import json
import pandas
from IPython.core.display import display, HTML

from tqdm import tqdm

from apify_client import ApifyClient

from sqlalchemy import create_engine, text

import openai

!
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
 