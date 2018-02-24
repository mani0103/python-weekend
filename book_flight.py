import argparse
import pprint as pp
from datetime import datetime
from functools import reduce
import json
import requests


def find_flight(args):
    """
    returns the reservation token for a flight based on the passed arguments coming from command line
    """
    
    date = datetime.strftime(datetime.strptime(args['date'], "%Y-%m-%d"), "%d/%m/%Y") #do this outside of find flight method!!!!
    typefligh = "round" if args['return'] else "oneway"
    days_in_destination = args['return'] if args['return'] else 0

    params = {
        'v':'3',
        'daysInDestinationFrom': days_in_destination,
        'daysInDestinationTo': days_in_destination,
        'flyFrom': args['from'],
        'to': args['to'],
        'dateFrom': date,
        'dateTo': date,
        'typeFlight': typefligh,
        'adults':'1',
        'limit':'200'
    }

    url = 'https://api.skypicker.com/flights'
    r = requests.get(url, params=params)
    json_result = r.json()
    data = json_result['data']

    if len(data) == 0:
        return 0

    if args['bags'] != 0:
        data = [x for x in data if args['bags'] in x['bags_price']]

    if args['fastest']:
        result = reduce(lowest_duration, data)
    else:
        result = reduce(lambda x, y: lowest_price(x, y, args['bags']), data)

    return result['booking_token']

def get_price(flight, bags):
    """
    returns the price of the flight from JSON data coming 
    from the API based on how many bags we have
    """
    bags_price = flight['bags_price'][bags] if bags != 0 else  0
    return flight['price'] + bags_price

def lowest_duration(x, y):
    """
    compares the JSON data of a flight based on its duration and returns the fastest
    """
    return x if x['duration']['total'] < y['duration']['total'] else y

def lowest_price(x, y, bags):
    """
    compares the JSON data of a flight based on its price and returns the cheapest
    """
    return x if get_price(x, bags) < get_price(y, bags) else y

def book_flight(token, args):
    """
    creates a post request for a given flight token 
    and based on the given command line arguments then returns 
    the reservation number if reservation is confirmed otherwise returns 0
    """

    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        "bags": args['bags'],
        "booking_token": token,
        "currency":"EUR",
        "passengers":[
            {
                "firstName": "Friedrich",
                "lastName": "Riemann",
                "birthday": "1826-09-17",
                "email": "Friedrich.Riemann@gmail.com",
                "title": "Mr",
                "documentID": "179424691"
            }
        ]

    }
    url = 'http://128.199.48.38:8080/booking'
    r = requests.post(url, data=json.dumps(data), headers=headers)
    if r.status_code != 200:
        return 0

    json_result = r.json()

    if 'status' in json_result and json_result['status'] == "confirmed":
        return json_result['pnr']
    else:
        return 0




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Find and book some flights")
    parser.add_argument('--date', default=datetime.strftime(datetime.now(), "%Y-%m-%d"))
    parser.add_argument('--from')
    parser.add_argument('--to')
    parser.add_argument('--one-way', action='store_true', default=False)
    parser.add_argument('--return', default=False)
    parser.add_argument('--cheapest', action='store_true', default=False)
    parser.add_argument('--fastest', action='store_true', default=False)
    parser.add_argument('--bags', default=0)
    args = parser.parse_args()

    token = find_flight(vars(args))

    print(book_flight(token, vars(args)))
