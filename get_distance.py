import json
import boto3
import ast
from decimal import Decimal


dynamodb_table = 'city-distance'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodb_table)


def lambda_handler(event, context):
    try:
        data = json.loads(event['body']) if event.get('body', 0) else event
    
        city_distance = get_city_distance(data['currentIntent']['slots'])
        
        result = {
            "dialogAction": {
                "type": "Close",
                "fulfillmentState": "Fulfilled",
                "message": {
                  "contentType": "SSML",
                  "content": "{}".format(city_distance['distance'])
                },
            }
        }

    except Exception as error:
        result = {
            'status': 'error',
            'message': "Something wrong, {}".format(error)
        }

    return result


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


def get_city_distance(data=None):
    try:
        distance = table.get_item(Key={
            'source': data['Source'],
            'destination': data['Destination']
        })

        return ast.literal_eval(
            (json.dumps(
                distance.get('Item', {}), cls=DecimalEncoder)))

    except Exception as E:
        return {'error': str(E)}


if __name__ == '__main__':
    result = lambda_handler({
        "source": "Chicago", 
        "destination": "Lafayette"
    }, {})

    print(result)
