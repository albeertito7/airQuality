import pandas as pd
import requests
import json

API_BASE_URL = 'https://u50g7n0cbj.execute-api.us-east-1.amazonaws.com/v2/'
RAW_DATA_PATH = '../../data/raw/'


def get_countries(limit=200, order_by='country', sort='asc'):
    query_params = {'limit': limit, 'order_by': order_by, 'sort': sort}
    response = requests.get(url=API_BASE_URL + 'countries', params=query_params, timeout=20)
    return response.json()


def get_parameters():
    pass


def save_json(input_name, data):
    with open(RAW_DATA_PATH + input_name, 'w') as file:
        json.dump(data, file, indent=4, sort_keys=True)


if __name__ == '__main__':
    # Get countries
    countries = get_countries()
    save_json('countries.json', countries)
    # Save countries
