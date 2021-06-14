import datetime
import math

import pandas as pd
import requests
import json

API_BASE_URL = 'https://u50g7n0cbj.execute-api.us-east-1.amazonaws.com/v2/'
RAW_DATA_PATH = '../../data/raw/'


def get_countries(limit=200, order_by='country', sort='asc'):
    query_params = {'limit': limit, 'order_by': order_by, 'sort': sort}
    response = requests.get(url=API_BASE_URL + 'countries', params=query_params, timeout=20)
    return response.json()


def get_parameters(limit=100, sort='asc'):
    query_params = {'limit': limit, 'sort': sort}
    response = requests.get(url=API_BASE_URL + 'parameters', params=query_params, timeout=20)
    return response.json()


# TODO: add list of parameters
def get_average_measurements(limit=100000, page=1, sort='desc', country_id='ES',
                             spatial='country',
                             temporal='day', date_from=datetime.date(2020, 1, 1), date_to=datetime.date(2020, 12, 31)):
    query_params = {'limit': 1, 'sort': sort, 'page': page, 'country_id': country_id,
                    'date_from': date_from,
                    'date_to': date_to, 'spatial': spatial, 'temporal': temporal}

    found = int(requests.get(url=API_BASE_URL + 'averages', params=query_params, timeout=20).json()['meta']['found'])
    pages = math.ceil(found / limit)

    for i in range(pages):
        query_params = {'limit': limit, 'sort': sort, 'page': i + 1, 'country_id': country_id,
                        'date_from': date_from,
                        'date_to': date_to, 'spatial': spatial, 'temporal': temporal}
        response = requests.get(url=API_BASE_URL + 'averages', params=query_params, timeout=30)

        save_json('measurements_%s_%s.json' % (temporal, i), response.json())


def save_json(input_name, data, type='w'):
    with open(RAW_DATA_PATH + input_name, type) as file:
        json.dump(data, file, indent=4, sort_keys=True)


if __name__ == '__main__':
    # Get and save countries
    countries = get_countries()
    save_json('countries.json', countries)

    # Get and save parameters
    parameters = get_parameters()
    save_json('parameters.json', parameters)
    get_average_measurements()
