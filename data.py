import csv
import numpy as np
import pandas as pd
import requests
import json
from pandas.io.json import json_normalize
from pprint import pprint
from . import AQI_sorting

# --- Scraping The Air Quality System (AQS) API Database  --- #

# ____put your email & key here ______#

EMAIL = 'lukas.elsrode@gmail.com'
API_KEY = 'greyheron61'
ADD = "?email=" + EMAIL + "&key=" + API_KEY

##____ Hard Coded Filters Dict ___________ ##

DF = pd.read_csv('uszips.csv')
DF_CLEAN = DF[['zip','city','state_id','state_name', 'population','density']]


### TODO: We need to automate this for all our filters
'''
BENCH_KEYS = {'states':'states', 'Core_Based_Statistical_Areas': 'cbsas', 
'Parameter_Classes':'classes'}

PARAM_KEYS = {'all_counties_in_state': ['state','county'], 'params_in_class':['pc', 'parametersByClass']}
'''
'''
Filtering by benchmark (non list filters)
'''
class AQI:
    def __init__(self):
        self.bench_keys = {'states':'states', 'Core_Based_Statistical_Areas': 
                           'cbsas', 'Parameter_Classes':'classes'}
        self.param_keys = {'all_counties_in_state': ['state','county'], 
                           'params_in_class':['pc', 'parametersByClass']}
        self.param_filters = self.find_param_filters(self.bench_keys, 
                                                     self.param_keys)
        self.aqi_data = AQI_sorting.aqi_df() #master df of all 2019 aqi data for all locations


    def filter_benchmark(self, filters):
        website = 'https://aqs.epa.gov/data/api/list/'
        benchmark_lst = []
        d = {}
        for _, val in filters.items():
            benchmark_lst.append(val)

        for benchmark in benchmark_lst:
            new_web = website + benchmark + ADD
            JSONContent = requests.get(new_web).json()
            d[benchmark] = JSONContent["Data"]
        return d

    #Dictionary Outer Key = "Data"
    #Inner structure: "code": (int), "value_represented": (full name of state string)

    def find_param_filters(self, bench_filters, param_filters):
        d = self.filter_benchmark(bench_filters)
        d1 = {}
        website = 'https://aqs.epa.gov/data/api/list/'

        for key, val in d.items():
            if key == 'classes':
                for dic in d[key]:
                    if dic['code'] == 'AQI POLLUTANTS':
                        append = 'parametersByClass' + ADD + "&pc=" + dic['code']
                        new_web = website + append
                        JSONContent = requests.get(new_web).json()
                        d1[dic['code']] = JSONContent['Data']
        return d1


def find_AQI_data(data_want, date_start, date_end, location):
    ## returns possible values associated with any given recorded variable
    website = 'https://aqs.epa.gov/data/api/annualData/byCBSA' + ADD
    dic1, dic2 = self.find_param_filters(self.bench_keys, self.param_keys)

    df = pd.DataFrame()
    d = {}

    for area_dic in dic1['cbsas']:
        if area_dic['value_represented'] == location:
            url_add2 = '&bdate=' + str(date_start) + '&edate=' + str(date_end) + '&cbsa=' + area_dic['code']

    for parameter in data_want:
        for filt in dic2['AQI POLLUTANTS']:
            if parameter == filt['value_represented']:
                url_add1 = '&param=' + filt['code']
                url = website + url_add1 + url_add2
                #pprint(url)
                JSONContent = requests.get(url).json()
                d[parameter] = JSONContent["Data"]
                #df_data = pd.DataFrame.from_dict(json_normalize(JSONContent['Data']), orient='columns')
    return d

        

    ### TODO: ok so some magic happens here and back me up

    #raw = query_example.x  ### TODO:  ^^ def magic(starting_url) ---> x

    def make_id_for_one(var,raw_data):
        d = {}  # make dict associating each variable with each possible code
        vals = []
        table = raw_data['Data']
        for i in table:
            kv = {i['value_represented']:i['code']}
            vals.append(kv)
        d[var] = vals
        return d

    ### # TODO: use selinium to send in that post
