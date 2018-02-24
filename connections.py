import argparse
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_html(args):
    url1, url2, url3 = create_links(args)
    s = requests.Session()
    s.get(url1)
    s.get(url2)
    r = s.get(url3)
    return r.content

#    s.get("https://bustickets.regiojet.com/")
#    s.get('https://bustickets.regiojet.com/Booking/from/10202002/to/10202003/tarif/REGULAR/departure/20180224/retdep/20180224/return/false')
#    r = s.get("https://bustickets.regiojet.com/Booking/from/10202002/to/10202003/tarif/REGULAR/departure/20180224/retdep/20180224/return/false?1-1.IBehaviorListener.0-mainPanel-routesPanel&_=1519469955659")

def create_links(args):
    url1 = "https://bustickets.regiojet.com/"
    url2 = (
            f"https://bustickets.regiojet.com/Booking/"
            f"from/{args['from']}/"
            f"to/{args['to']}/"
            f"tarif/REGULAR/"
            f"departure/{args['date']}/"
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Find and book some flights")
    parser.add_argument('--date', default=datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument('--from')
    parser.add_argument('--to')
    args = parser.parse_args()

    args = vars(args)
    args['date'] = datetime.strptime(args['date'], "%Y-%m-%d").strftime("%Y%m%d")
    args['from'] = get_destinations_id(args['from'])
    args['to'] = get_destinations_id(args['to'])
    print(args)
    print(create_links(args))
    print(get_html(args))


#print('8.10' in r.text)

#soup = BeautifulSoup(r.content, 'html.parser')
#print(soup.prettify())
    #with open("result.html",mode="w") as f:
     #   f.write(get_html)
#print(soup.select("div.routeSummary"))
#routes = soup.findall('div',class_ = "routeDetail")


#print(destinations)