import json
import boto3
from decimal import Decimal
from opencage.geocoder import OpenCageGeocode
from geopy import distance


geocoder = OpenCageGeocode('4f3e4113e1a147dc97a4ebf6f598c67a')

dynamodb_table = 'city-distance'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodb_table)


def lambda_handler(event, context):
    statusCode = 200
    result = {
        'status': 'success',
        'data': {}
    }

    try:
        data = json.loads(event['body']) if event.get('body', 0) else event
        
        graph = event['graph']
        city = graph.split(',')
        
        for edge in city:
            source, destination = edge.split('->')

            source_info = geocoder.geocode(source)
            destination_info = geocoder.geocode(destination)

            source_lat, source_long = source_info[0]['geometry']['lat'], \
                                            source_info[0]['geometry']['lat']

            destination_lat, destination_long = destination_info[0]['geometry']['lat'], \
                                            destination_info[0]['geometry']['lat']

            source_to_destination = (distance.distance(
                        (source_lat, source_long), 
                        (destination_lat, destination_long)
                    ).kilometers)

            result['data'] = save_city_distance({
                'source': source,
                'destination': destination,
                'distance': source_to_destination
            })

    except Exception as error:
        statusCode = 403
        result = {
            'status': 'error',
            'message': "Something wrong, {}".format(error)
        }

    return {
        'statusCode': statusCode,
        'body': json.dumps(result)
    }


def save_city_distance(body=None):
    try:
        body = json.loads(json.dumps(body), parse_float=Decimal)
        result = table.put_item(Item=body)
        return {'success': True}
    except Exception as E:
        return {'error': str(E)}


if __name__ == '__main__':
    result = lambda_handler({
        "graph": "Chicago->Urbana,Urbana->Springfield,Chicago->Lafayette"
    }, {})

    print(result)
