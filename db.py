from datetime import datetime
from pprint import pprint
import psycopg2  
from psycopg2.extras import RealDictCursor
from connections import search_for_connections
import argparse

pg_config = {  
    'host': 'python-weekend.cikhbyfn2gm8.eu-west-1.rds.amazonaws.com',  
    'database': 'pythonweekend',  
    'user': 'weekenduser',  
    'password': 'ovikendusechlasta'
}

  

def insert_connections_to_sql(values):
    print('insert')
    sql_insert = """
    INSERT INTO connections (source, destination, departure_time, arrival_time, price, vehicle_type)
    VALUES (%(src)s,
            %(dst)s,
            %(dep)s,  
            %(arr)s,
            %(price)s,
            %(type)s);
    """
    conn = psycopg2.connect(**pg_config)
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:  
        for line in values:

            line['arr'] = datetime.strptime(line.get('arr',''),"%Y-%m-%d %H:%m:%S").utcfromtimestamp()
            line['dep'] = datetime.strptime(line.get('dep',''),"%Y-%m-%d %H:%m:%S").utcfromtimestamp()

            cursor.execute(sql_insert, line)  
        conn.commit()
    conn.close()

def select_connections_from_sql():
    sql_select = "SELECT * FROM connections"
    conn = psycopg2.connect(**pg_config)
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:  
        cursor.execute(sql_select)  
        results_dict = cursor.fetchall()
    conn.close()
    return results_dict


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="abc")
    parser.add_argument('--insert', action='store_true' )
    args = parser.parse_args()
    print(args)

    src = 'Praha'
    dst = 'Brno'
    date = '2018-03-16'

    values = search_for_connections(src, dst, date)
    pprint(values[1])

    if vars(args)['insert']:
        insert_connections_to_sql(values)
    else:
        pass #pprint(select_connections_from_sql())





