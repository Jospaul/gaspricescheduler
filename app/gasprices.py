#!/bin/usr/python

import requests
import json
import psycopg2
from datetime import datetime
import pytz


GASBUDDY_URL="https://www.gasbuddy.com/graphql"

COSTCO_FRISCO = {
    "storeid": "10301",
    "warehouseno": "1097"
}


def fetch_gasprice_gasbuddy(url: str, storeid: str):
    data = {
        "operationName": "GetStation",
        "variables": {
            "id": storeid
        },
        "query": "query GetStation($id: ID!) { station(id: $id) { fuels prices { cash { postedTime price } credit { postedTime price } } } }"
    }

    headers={
        "Content-Type": "application/json",
        "User-Agent": "Python Gasbuddy"
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        gasbuddy_data = json.loads(response.text)

        gasdata = {}
        for fueltypes in gasbuddy_data.get('data').get('station').get('fuels'):
            index = gasbuddy_data.get('data').get('station').get('fuels').index(fueltypes)
            if gasbuddy_data.get('data').get('station').get('prices')[index].get('credit').get('price'):
                price = gasbuddy_data.get('data').get('station').get('prices')[index].get('credit').get('price')
            elif gasbuddy_data.get('data').get('station').get('prices')[index].get('cash').get('price'):
                price = gasbuddy_data.get('data').get('station').get('prices')[index].get('cash').get('price')
            else:
                price="0.0"
            gasdata[fueltypes] = price
        return gasdata
    else:
        print("Gas buddy request failed")
        print(response.text)

def fetch_gasprice_costco(storeid: str, warehouse: str):
    url = f"https://www.costco.com/AjaxWarehouseBrowseLookupView?langId=-1&storeId={storeid}&populateWarehouseDetails=true&warehouseNumber={warehouse}"
    headers={
        "User-Agent": "Python Costco Gas",
        "Connection": "keep-alive",
        "Accept": "*/*"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    if response.status_code == 200:
        costcodata = json.loads(response.text)
        gasdata = {
            "regular_gas": costcodata[1].get("gasPrices").get("regular"),
            "premium_gas": costcodata[1].get("gasPrices").get("premium")
        }

        return gasdata
    else:
        print("Costco gas request failed")
        print(response.text)

def fetch_gasprice(storeid: str, gastype: str, source: str):
    if source.lower() == 'costco':
        prices = fetch_gasprice_costco(COSTCO_FRISCO.get("storeid"), COSTCO_FRISCO.get("warehouseno"))
    else:
        if gastype.lower() not in ['r', 'p']:
            return {
                "Status": "Failure",
                "Description": "Gas type needs to be 'r' for regular and 'p' for premium."
            }
        
        prices = fetch_gasprice_gasbuddy(GASBUDDY_URL, storeid)

    if prices and gastype.lower() == 'r':
        return prices.get("regular_gas")
    else:
        return prices.get("premium_gas")

    

def write_topg_gasprice(regular: float, premium: float):
    conn = psycopg2.connect(
        dbname="teslamate",
        user="teslamate",
        password="password",
        host="database",
        port="5432"
    )

    cur = conn.cursor()

    table_name = "gasprice"
    central_tz = pytz.timezone('America/Chicago')
    timestamp = datetime.now(central_tz)
    
    insert_query = f"""
    INSERT INTO {table_name} (date, regular, premium)    
    VALUES (%s, %s, %s)
    """

    cur.execute(insert_query, (timestamp, regular, premium))

    conn.commit()

    cur.close()
    conn.close()

def insert_gasprice(storeid: str):

    regular = fetch_gasprice(storeid, 'r', 'costco')
    premium = fetch_gasprice(storeid, 'p', 'costco')

    write_topg_gasprice(float(regular), float(premium))





