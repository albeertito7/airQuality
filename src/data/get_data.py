#!/usr/bin/env python

import datetime
import json
import math
import argparse
import os
from shutil import rmtree

import pandas as pd
import requests

# global vars
API_BASE_URL = 'https://u50g7n0cbj.execute-api.us-east-1.amazonaws.com/v2/'
RAW_DATA_PATH = '../../data/raw/'

VERBOSE = False


def get_countries(limit=200, order_by='country', sort='asc'):
    try:
        payload = {
            'limit': limit,
            'order_by': order_by,
            'sort': sort
        }

        response = requests.get(url=API_BASE_URL + 'countries', params=payload, timeout=20)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    else:
        return response.json()


def get_parameters(limit=100, sort='asc'):
    try:
        payload = {
            'limit': limit,
            'sort': sort
        }

        response = requests.get(url=API_BASE_URL + 'parameters', params=payload, timeout=20)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    else:
        return response.json()


def get_locations(limit=1000, page=1, country_id='ES', city='Lleida'):
    try:
        payload = {
            'limit': limit,
            'page': page,
            'country_id': country_id,
            'city': city
        }

        response = requests.get(url=API_BASE_URL + 'locations', params=payload, timeout=30)
        response.raise_for_status()
        save_json('locations_%s_%s.json' % (country_id, city), response.json())

    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def get_measurements(limit=100000, page=1, country_id='ES', city='Lleida',
                     date_from=datetime.date(2020, 1, 1), date_to=datetime.date(2020, 12, 31)):
    try:
        payload = {
            'limit': limit,
            'page': page,
            'country_id': country_id,
            'date_from': date_from,
            'date_to': date_to,
            'city': city
        }

        response = requests.get(url=API_BASE_URL + 'averages', params=payload, timeout=30)
        response.raise_for_status()
        save_json('measurements_%s.json' % country_id, response.json())

    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def save_json(input_name, data, type='w'):
    with open(RAW_DATA_PATH + input_name, type) as file:
        json.dump(data, file, indent=4, sort_keys=True)


def checkPath():
    if os.path.exists(RAW_DATA_PATH):
        rmtree(RAW_DATA_PATH, ignore_errors=True)
    os.makedirs(RAW_DATA_PATH, exist_ok=True)


def parse_arguments():
    parser = argparse.ArgumentParser(prog="Get data script",
                                     description="Script to get the data about air quality using OpenAQ.")
    parser.add_argument('-p', '--path', dest='path', type=str, default=RAW_DATA_PATH, required=False,
                        help='Custom save data path directory.')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False, required=False,
                        help='Display monitoring details.')
    return parser.parse_intermixed_args()


def main():
    global RAW_DATA_PATH, VERBOSE

    args = parse_arguments()

    RAW_DATA_PATH = args.path
    VERBOSE = args.verbose

    print("Starting...") if VERBOSE else 'Python inline if...'

    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    checkPath()

    print("Path checked.") if VERBOSE else 'Python inline if...'

    # Get and save countries
    countries = get_countries()
    save_json('countries.json', countries)

    print("Countries got.") if VERBOSE else 'Python inline if...'

    # Get and save parameters
    parameters = get_parameters()
    save_json('parameters.json', parameters)

    print("Sensor parameters got.") if VERBOSE else 'Python inline if...'

    # Get and save locations
    get_locations()

    # Get average measurements
    #get_measurements()

    print("Average measurements got.") if VERBOSE else 'Python inline if...'
    print("Completed.") if VERBOSE else 'Python inline if...'


if __name__ == '__main__':
    main()
