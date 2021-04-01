import json
import requests
import numpy
import pandas as pd
from pandas.io.json import json_normalize

API_KEY = "gVr18OXpCt7uyZ43HDPlznxlDPhp7Pqsh21fsBcr"

URL = "https://developer.nrel.gov/api/cleap/v1/"

def get_energy_data(zip_code):
    '''
    Given a zip code (str) returns a dataframe of avg energy consumption
    of many types
    '''
    city_url = URL + "cities?zip=" + zip_code + "&api_key=" + API_KEY
    city_json = requests.get(city_url).json()

    if len(city_json["errors"]) > 0:
        for errors in city_json["errors"]:
            if errors["code"] == "NOT_FOUND":
                return "No data available"

    city_name = city_json["result"][0]["name"]

    energy_url = URL + "energy_cohort_data?zip=" + zip_code + "&api_key=" + \
    API_KEY
    energy_json = requests.get(energy_url).json()
    energy_dic = energy_json["result"][city_name]["similar_places"]["table"]
    energy_df = pd.DataFrame.from_dict({(i, j): energy_dic[i][j] \
        for i in energy_dic.keys() for j in energy_dic[i].keys()}, \
        orient = 'index')

    return energy_df