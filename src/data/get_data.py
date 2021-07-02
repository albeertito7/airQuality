#!/usr/bin/env python

import os
from shutil import rmtree

import requests
import datetime, json

import argparse
import coloredlogs, logging as log

# global vars
API_BASE_URL = 'https://u50g7n0cbj.execute-api.us-east-1.amazonaws.com/v2/'
RAW_DATA_PATH = '../../data/raw/'

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
        log.error(e)
        raise SystemExit(e)
    else:
        log.info("Countries got.")
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
        log.error(e)
        raise SystemExit(e)
    else:
        log.info("Parameters got.")
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

        lst = []
        for location in response.json()['results']: lst.append(location['name'])
        return lst

    except requests.exceptions.RequestException as e:
        log.error(e)
        raise SystemExit(e)


def get_measurements(limit=100000, page=1, country_id='ES', city='Lleida',
                     location=None,
                     date_from=datetime.date(2019, 1, 1), date_to=datetime.date(2020, 12, 31)):
    try:
        payload = {
            'limit': limit,
            'page': page,
            'country_id': country_id,
            'date_from': date_from,
            'date_to': date_to,
            'city': city,
            'location': location
        }

        response = requests.get(url=API_BASE_URL + 'measurements', params=payload, timeout=30)
        response.raise_for_status()
        save_json('measurements_%s_%s.json' % (country_id, location), response.json())

    except requests.exceptions.RequestException as e:
        log.error(e)
        raise SystemExit(e)


def save_json(input_name, data, type='w'):
    with open(RAW_DATA_PATH + input_name, type) as file:
        json.dump(data, file, indent=4, sort_keys=True)
        log.info("%s saved." % input_name)

def checkPath():
    if os.path.exists(RAW_DATA_PATH):
        rmtree(RAW_DATA_PATH, ignore_errors=True)
    os.makedirs(RAW_DATA_PATH, exist_ok=True)
    log.info("Path checked.")


def parse_arguments():
    parser = argparse.ArgumentParser(prog="Get data script",
                                     description="Script to get the data about air quality using OpenAQ.")
    parser.add_argument('-p', '--path', dest='path', type=str, default=RAW_DATA_PATH, required=False,
                        help='Custom save data path directory.')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False, required=False,
                        help='Display monitoring details and create a logging file.')
    return parser.parse_intermixed_args()


def main():
    global RAW_DATA_PATH
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    args = parse_arguments()

    RAW_DATA_PATH = args.path
    if args.verbose:
        file_handler = log.FileHandler('getData_%s.log' % datetime.datetime.now().strftime("%d-%H-%M-%S")) # day - hour - minute - second
        file_handler.setLevel(log.DEBUG)

        formatter = log.Formatter("%(asctime)s %(levelname)s %(message)s")
        file_handler.setFormatter(formatter)
        log.getLogger().addHandler(file_handler)
        
        coloredlogs.install(fmt="%(asctime)s %(levelname)s %(message)s", level=log.DEBUG)

    log.info("Starting...")

    log.info("Checking path...")
    checkPath()

    # Get and save countries
    log.info("Getting countries...")
    countries = get_countries()
    save_json('countries.json', countries)

    # Get and save parameters
    log.info("Getting parameters...")
    parameters = get_parameters()
    save_json('parameters.json', parameters)

    # Get and save locations
    log.info("Getting locations...")
    locations = get_locations()

    # Get measurements
    #locations = ['ES1348A', 'ES1225A', 'ES1588A', 'ES1982A', 'ES2034A', 'ES0014R', 'ES1248A'] # sensors (name)
    for i in locations:
        log.info("Getting [%s] measuraments..." % i)
        get_measurements(location=i)

    log.info("Completed.")

if __name__ == '__main__':
    main()