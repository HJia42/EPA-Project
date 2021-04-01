import numpy as np
import math
import pandas as pd
pd.options.mode.chained_assignment = None 


## Mater Df with every zip-code ##
df_raw = pd.read_csv('uszips.csv', converters = {'zip': lambda x: str(x)}, usecols = ['zip', 'state_id', 'city', 'population','density','imprecise'])

# UI functions #
def is_true_zip(zipcode, df=df_raw):
    all_zips = df[df['state_id'] != 'PR']['zip']
    if zipcode in all_zips.values:
        return True
    else:
        return False


def random_sample_df(df=df_raw):
    us_df = df[df['state_id'] != 'PR']
    us_df = us_df[['state_id', 'zip']].groupby('state_id').agg(np.random.choice)
    return us_df


def testing_US_df(df=df_raw):
    us_df = df[df['state_id'] != 'PR']
    us_df['K_var'] = np.random.uniform(size=(us_df.shape[0]))
    #print(us_df)
    us_df = us_df[['state_id','K_var','zip']].groupby('state_id').agg({'K_var': 'mean', 'zip':'min'})
    return us_df


## Main fn ##
def go (zip_code):
    # unique per input #
    data_zip = df_raw.loc[df_raw.zip == zip_code]

    # Local: In same state #
    state_df = return_all_in_state(zip_code)
    same_state_df = make_clean_df(state_df)

    i = same_state_df.shape[0]
    rural , suburban , urban = sort_to_area_type(same_state_df)
    geo_zips = [i for i in rural['zip'].values ], [i for i in suburban['zip'].values], [i for i in urban['zip'].values] 

    all_state_comparison =  make_clean_df(df_raw.sample(n = math.ceil(i/4)))

    random_national_comp = sort_to_area_type(all_state_comparison)

    if zip_code in geo_zips[0]:
        _type = 'Rural'

    if zip_code in geo_zips[1]:
        _type = 'Suburban'

    if zip_code in geo_zips[2]:
        _type = 'Urban'

    '''
    ### FOR TESTING PLS DON'T DELETE TYYY
    data_zip['K_var'] = np.random.uniform(size=(data_zip.shape[0]))
    state_df['K_var'] = np.random.uniform(size=(state_df.shape[0]))
    '''
    return data_zip , state_df, random_national_comp , _type , geo_zips


## functions to make the df_zips ##
def get_identifiers(df):
    cols = df.columns.format()
    return cols

def group_id_dict_by_pop(df):
    d = {}
    df_union = df[df['state_id'] != 'PR']  # exclude Puerto Rico
    N  = df_union.shape[0]
    id_types = get_identifiers(df)
    for i in range(N-1):
        d_id = {}
        zip_code = df_union['zip'].array[i]
        d[zip_code] = d_id
        for id_type in id_types:
            if id_type != 'zip':
                vals = df_union[df_union.zip == zip_code][id_type].values[0]
                if id_type in ('population','density'):
                    pop_val = int(df_union[df_union.zip == zip_code]['population'])
                    density_val = int(df_union[df_union.zip == zip_code]['density'])
                    if density_val != 0:
                        Area = pop_val/ density_val
                    else:
                        Area = None
                    d_id['population'] = pop_val
                    d_id['density'] = density_val
                    d_id['Area'] = Area
                else:
                    d_id[id_type] = vals
    return d


def make_clean_df(df):
    d = group_id_dict_by_pop(df)
    df_n = pd.DataFrame.from_dict(d, columns= ['zip', 'city', 'state_id', 'population','density', 'Area', 'imprecise'] , orient= 'index')
    df_n['zip'] = [i for i in df_n.index]
    df_n['metric'] = (df_n['population'] * df_n['density']) / df_n['Area']
    return df_n


### here i'm defining the constraining variables in general population & population density ###
def sort_to_area_type(zip_df, rural_thresh = 0.27, suburban_thresh = 0.52, urban_thresh = 0.21):
    i = zip_df.shape[0]
    ub_rural = math.ceil(i * rural_thresh)
    ub_suburban = math.ceil(suburban_thresh * i)

    df_metric = zip_df.sort_values(by = ['metric'])
    df_rural = df_metric[0: ub_rural]
    df_suburban = df_metric[ub_rural:ub_suburban]
    df_urban = df_metric[ub_suburban: (i- 1)]

    return df_rural , df_suburban, df_urban


def return_all_in_state(zip_code):
    input_zip = df_raw.loc[df_raw.zip == zip_code]
    state = input_zip.state_id.values[0]
    df_state = df_raw[df_raw.state_id == state]
    df_state.columns = ['zip', 'city', 'state_id', 'population','density','imprecise']
    
    return df_state
