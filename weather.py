import csv
import json
import requests
import numpy as np
import pandas as pd
from pandas.io.json import json_normalize
from json import JSONDecodeError

API_KEY = '&key=HrOY6aVn'
URL = 'https://api.meteostat.net/v1'
DROP = ['temperature_mean_max', 'temperature_mean_min', 'temperature_min', 
'temperature_max', 'precipitation', 'raindays', 'pressure', 'sunshine']

df = pd.read_csv('uszips.csv', converters = {'zip': lambda x: str(x)})

def zip_to_place(zip_code):
    '''
    From our zip_code(str) file, given a zip code find the logitude and latitude
    '''

    if zip_code not in df.zip.values:
        return "Zip not in uszips.csv"

    lat = df[df['zip'] == zip_code]['lat'].to_list()[0]
    lon = df[df['zip'] == zip_code]['lng'].to_list()[0]

    return str(lat), str(lon)

def zips_weather(zip_code, max_dist=25):
    '''
    Given a certain zip code, and a set distance away from recorded area of this 
    zip code, find the nearest site point with monthely data and get that data
    '''
    if type(zip_to_place(zip_code)) == str:
        return "Zip not in uszips.csv"

    lat, lon = zip_to_place(zip_code)
    weather_id_lst = []
    d = {}

    id_url = URL + "/stations/nearby?lat=" + lat + "&lon=" + lon + "&limit=10" + \
    API_KEY

    try:
        weather_data = requests.get(id_url).json()["data"]
    except JSONDecodeError:
        return "SERVER_TIME OUT"

    for station in weather_data:
        weather_id = station['id']
        if float(station['distance']) <= max_dist:
            weather_id_lst.append(weather_id)

    for w_id in weather_id_lst:
        df = pd.DataFrame(columns = ['month', 'temperature_mean'])
        temp_url = [URL + "/history/monthly?station=" + w_id \
        + "&start=1980-01&end=2009-12"+ API_KEY]
        temp_url.extend([URL + "/history/monthly?station=" + w_id \
            + "&start=2010-01&end=2017-12"+ API_KEY])

        for url in temp_url:
            try:
                lstofdic = requests.get(url).json()["data"]
            except JSONDecodeError:
                return "SERVER_TIME_OUT"
            df1 = pd.DataFrame.from_dict(json_normalize(lstofdic), orient = \
                'columns')
            if len(df1) > 90:
                df1 = df1.drop(DROP, axis = 1)
                df = pd.concat([df, df1], ignore_index = True)
                if len(df) > 396:
                    df2 = df.month.str.split("-", expand=True)
                    df = pd.concat([df, df2], axis = 1, ignore_index = True)
                    df = df.drop(0, axis = 1)
                    df.columns = ["temperature", "year", "month"]
                    df = df[["year", "month", "temperature"]]
                    break

    if df.empty:
        return "No Data"
    else:
        return df


