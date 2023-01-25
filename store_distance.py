import json
import boto3
from collections import deque

# from decimal import Decimal
# from opencage.geocoder import OpenCageGeocode
# from geopy import distance


# geocoder = OpenCageGeocode('4f3e4113e1a147dc97a4ebf6f598c67a')

# dynamodb_table = 'city-distance'
# dynamodb = boto3.resource('dynamodb')
# table = dynamodb.Table(dynamodb_table)


def unroll_shortest_path(current, optimal_parent_map, path=()):
    if current is None:  # Reached the start node
        return path
    else:
        return unroll_shortest_path(optimal_parent_map[current], optimal_parent_map, (current,) + path)


def breadth_first_search(from_city, to_city, city_data):
    to_visit = deque([from_city])
    visited = set([from_city])
    parent_map = {from_city: None}

    while to_visit != []:
        current = to_visit.popleft()  # Treat to_visit as queue
        print("Visiting:", current)
        neighbors = city_data[current]

        for n in neighbors:
            if n == to_city:
                parent_map[n] = current
                return unroll_shortest_path(to_city, parent_map)

            elif n not in visited:
                parent_map[n] = current
                visited.add(n)
                to_visit.append(n)

    return None


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

        graph_map = {}
        
        for edge in city:
            source, destination = edge.split('->')

            if source in graph_map:
                graph_map[source].append(destination)
            else:
                graph_map[source] = [destination]

        searched = breadth_first_search('Chicago', 'Chicago', graph_map)

        result['data'] = graph_map

            # source_info = geocoder.geocode(source)
            # destination_info = geocoder.geocode(destination)

            # source_lat, source_long = source_info[0]['geometry']['lat'], \
            #                                 source_info[0]['geometry']['lat']

            # destination_lat, destination_long = destination_info[0]['geometry']['lat'], \
            #                                 destination_info[0]['geometry']['lat']

            # source_to_destination = (distance.distance(
            #             (source_lat, source_long), 
            #             (destination_lat, destination_long)
            #         ).kilometers)

            # result['data'] = save_city_distance({
            #     'source': source,
            #     'destination': destination,
            #     'distance': source_to_destination
            # })

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
