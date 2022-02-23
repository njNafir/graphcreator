import json
import boto3
from collections import deque
from decimal import Decimal


dynamodb_table = 'city-distance'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodb_table)


def unroll_shortest_path(current, optimal_parent_map, path=()):
    if current is None:  # Reached the start node
        return path
    else:
        return unroll_shortest_path(optimal_parent_map[current], optimal_parent_map, (current,) + path)


def breadth_first_search(from_city, to_city, city_data):
    if from_city == to_city:
        return 0

    to_visit = deque([from_city])
    visited = set([from_city])
    parent_map = {from_city: None}

    while to_visit != []:
        current = to_visit.popleft()  # Treat to_visit as queue
        # print("Visiting:", current)
        neighbors = city_data[current]

        for n in neighbors:
            if n == to_city:
                parent_map[n] = current
                return len(unroll_shortest_path(to_city, parent_map)) - 1

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

        for city_key in graph_map.keys():
            for neighbor in graph_map[city_key]:
                result['data']['{}->{}'.format(city_key, neighbor)] = save_city_distance({
                    'source': city_key,
                    'destination': neighbor,
                    'distance': breadth_first_search(city_key, neighbor, graph_map)
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
        return body
    except Exception as E:
        return {'error': str(E)}


if __name__ == '__main__':
    result = lambda_handler({
        "graph": "Chicago->Urbana,Urbana->Springfield,Chicago->Lafayette"
    }, {})

    print(result)
