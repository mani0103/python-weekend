import re
import json
import argparse
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from redis import StrictRedis
from pprint import pprint

def get_html(args):
    url1, url2, url3 = create_links(args)
    s = requests.Session()
    s.get(url1)
    s.get(url2)
    r = s.get(url3)
    return r.text

def get_cached_data(args):
    connection_name = f"connection_{args['from_id']}_{args['to_id']}_{args['date']}"
    return get_from_redis(connection_name)

def set_cached_data(args, data):
    connection_name = f"connection_{args['from_id']}_{args['to_id']}_{args['date']}"
    write_to_redis(connection_name, data)

#    s.get("https://bustickets.regiojet.com/")
#    s.get('https://bustickets.regiojet.com/Booking/from/10202002/to/10202003/tarif/REGULAR/departure/20180224/retdep/20180224/return/false')
#    r = s.get("https://bustickets.regiojet.com/Booking/from/10202002/to/10202003/tarif/REGULAR/departure/20180224/retdep/20180224/return/false?1-1.IBehaviorListener.0-mainPanel-routesPanel&_=1519469955659")

def create_links(args):
    url1 = "https://bustickets.regiojet.com/"
    url2 = (
            f"https://bustickets.regiojet.com/Booking/"
            f"from/{args['from_id']}/"
            f"to/{args['to_id']}/"
            f"tarif/REGULAR/"
            f"departure/{args['date_formatted']}/"
            f"retdep/20180224/return/false"
            )
    url3 = f'{url2}?1-1.IBehaviorListener.0-mainPanel-routesPanel&_=1519469955659'
    return (url1, url2, url3)   


def get_destinations_id(dest):
    url = "https://www.studentagency.cz/data/wc/ybus-form/destinations-cs.json"
    r = requests.get(url)
    destinations = r.json()
    for destination in destinations['destinations']:
        for city in destination['cities']:
            if city['name'] == dest:
                return city['id']

def get_data(html, args):
    soup = BeautifulSoup(html, 'html.parser')
    routes = soup.findAll('div',{'class': 'item_blue blue_gradient_our routeSummary free'})
    result = []
    for route in routes:
        free_space = int(route.find('div',{'class': 'col_space gray_gradient'}).text.strip())
        price = route.find('div',{'class': 'col_price'})
        price_value = ""
        if price is not None:
            price_value = price.find('span').text
            price_value = re.match(r"^\d+\.\d+",price_value).group(0)
        dep_time = route.find('div',{'class': 'col_depart gray_gradient'}).text
        arr_time = route.find('div',{'class': 'col_arival gray_gradient'}).text

        route_type = route.find('img')['title']
        #print(free_space, price_value, dep_time, arr_time, route_type)
        if free_space < args['passengers']:  # happy path
            continue   

        result.append( {
            "departure": f"{args['date']} {dep_time}:00",
            "arrival": f"{args['date']} {arr_time}:00",
            "from": args['from'],
            "to": args['to'],
            "free_seats": free_space,
            "price": price_value,
            "type": "train" if route_type == "train" else "bus" , # optional (train/bus)
            "from_id": args['from_id'], # optional (student agency id)
            "to_id": args['to_id'] # optional (student agency id)
        })
    return result


def connect_to_redis():
    redis_config = {
        'host': '188.166.60.144',
        'password': 'akd89DSk23Kldl0ram29',
        'port': 6379
        }
    return StrictRedis(**redis_config) 

def write_to_redis(key, value):
    redis = connect_to_redis()
    if redis.get(key):
        return
    else:
        redis.setex(key, 1000, json.dumps(value))

def get_from_redis(key):
    redis = connect_to_redis()
    return redis.get(key)

def search_for_connections(src, dst, date, passengers=1):
    args = {
        'date': date,
        'from': src,
        'to': dst,
        'date_formatted': datetime.strptime(date, "%Y-%m-%d").strftime("%Y%m%d"),
        'from_id': get_destinations_id(src),
        'to_id': get_destinations_id(dst),
        'passengers': passengers
    }
    #return args
    cached_data = get_cached_data(args)
    if cached_data is not None:
        return json.loads(cached_data.decode())
    else:
        html = get_html(args)
        data = get_data(html, args)
        set_cached_data(args, data)
        return data

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Find and book some flights")
    parser.add_argument('--date', default=datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument('--from', default="Praha")
    parser.add_argument('--to', default="Brno")
    parser.add_argument('--passengers', default=1)
    args = parser.parse_args()

    args = vars(args)
    args['date_formatted'] = datetime.strptime(args['date'], "%Y-%m-%d").strftime("%Y%m%d")
    args['from_id'] = get_destinations_id(args['from'])
    args['to_id'] = get_destinations_id(args['to'])
    
    cached_data = get_cached_data(args)
    if cached_data is not None:
        pprint(json.loads(cached_data.decode()))
    else:
        html = get_html(args)
        data = get_data(html, args)
        set_cached_data(args, data)
        pprint(data)


    #get_data(html, args)

    #write_to_redis("city_id_brno",get_destinations_id('Brno'))

    #print(args)
    #print(create_links(args))

#    with open("result.html",mode="w") as f:
#        f.write(get_html(args))


#print('8.10' in r.text)

#soup = BeautifulSoup(r.content, 'html.parser')
#print(soup.prettify())
#print(soup.select("div.routeSummary"))
#routes = soup.findall('div',class_ = "routeDetail")


#print(destinations)
