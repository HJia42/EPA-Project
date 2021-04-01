import numpy as np
import pandas as pd
import energy
import math
import weather
import US_zips
import AQI_EPA as air
import energy
import weather



class K_eco:
    """ Float value representing the relative ecological damage per state"""

    def __init__(self, zip_code, block_on_city = True):
        super(K_eco, self).__init__()

        # info on  the input zip_code #
        self.input_zip = zip_code
        self.input_info = self.zip_data()
        self.zip_info = self.input_info[0]
        self.state_info = self.input_info[1]
        self.zip_geography = self.input_info[3]
        self.city = self.zip_info.iloc[0]['city']
        self.state = self.zip_info.iloc[0]['state_id']

        # info for zip_codes in state #

        self.state_df = self.zip_info.append(self.state_info,
                                                ignore_index=True)
        self.state_zips = [i for i in self.state_df['zip'].values]

        # associates K_values for empty data for zip_codes which have no data #

        self.block_on_city = block_on_city
        self.city_to_zips = self.K_blocks()

        # all the nessasary metrics #
        self.air_k = self.eval_air_quality()
        self.energy_k = self.eval_energy()
        self.climate_k = self.eval_local_climate()

        # the processor #
        self.state_k_unprocessed = self.metrics_df()
        self.k_df = standardize_to_mean(self.state_k_unprocessed)
        self.all_states = US_zips.random_sample_df()            # randomized df

    def zip_data(self):
        '''
        All relevant info from US_zips
        Input:
            self: K_eco (object) our model
        Returns:
            location_data , df_user : (tuple of pandas df's)
            values for each k_air metric  used to derive K_eco score
        '''

        zip_data = US_zips.go(self.input_zip)
        location_data = zip_data[0][:4]
        state_df = zip_data[1]
        training = zip_data[2]
        zip_geography = zip_data[3]
        geo_zips = zip_data[4]

        return location_data, state_df , training , zip_geography, geo_zips

    def K_blocks(self):     # returns dictionary of mapped zip codes
        d = {}
        df_city_zips = self.state_df[['zip', 'city']]
        cities = df_city_zips['city'].unique().tolist()
        for city in cities:
            zips = [i for i in df_city_zips.loc[df_city_zips['city'] == city]['zip']]
            d[city] = zips
        return d

    def eval_air_quality(self):
        # relevant zip-codes #
        all_zips = self.state_zips
        # num_pollutants_listed for zip-codes #
        PM_10_states = [get_num_pollutants(i) for i in all_zips]
        PM_10_user = get_num_pollutants(self.input_zip)
        # insert into attribute df's #
        self.state_df['PM10'] = PM_10_states
        self.zip_info['PM10'] = PM_10_user
        # Format df's of state and input zips #
        df_air = self.state_df[['zip','PM10','city','state_id']]
        df_user = self.zip_info[['zip','PM10','city','state_id']]

        return df_air ,df_user

    def eval_energy(self):
        '''
        evaluates energy consumption of fossil fuels
        for inputed zip_code and for all zip_codes in the state
        Input:
            self: K_eco (object) our model
        Returns:
            df_energy, df_user : (tuple of pandas df's)
            values for each k_energy metric  used to derive K_eco score
        '''
        # relevant zip-codes #
        all_zips = self.state_zips
        # avg fuel usage for zip-codes #
        fuel_use = [get_avg_energy(i) for i in all_zips]
        fuel_use_user = get_avg_energy(self.input_zip)
        # insert into attribute df's #
        self.state_df['fuel'] = fuel_use
        self.zip_info['fuel'] = fuel_use_user
        # Format df's of state and input zips #
        df_energy = self.state_df[['zip','fuel','city','state_id']]
        df_user = self.zip_info[['zip','fuel','city','state_id']]

        return df_energy , df_user

    def eval_local_climate(self):
        '''
        evaluates climate variation for inputed zip_code and for all zip_codes
        in the state
        Input:
            self: K_eco (object) our model
        Returns:
            df_climate, df_user : (tuple of pandas df's)
            values for each k_climate metric  used to derive K_eco score
        '''
        all_zips = self.state_zips
        variation_state = [get_variation(i) for i in all_zips]
        variation_user = get_variation(self.input_zip)
        self.state_df['temp_variation'] = variation_state
        self.zip_info['temp_variation'] = variation_user
        df_climate = self.state_df[['zip','temp_variation','city','state_id']]
        df_user = self.zip_info[['zip','temp_variation','city','state_id']]

        return df_climate, df_user

    def metrics_df(self):
        '''
        Raw metrics for each zip_code in state for inputed zip_code
        Input:
            self: K_eco (object) our model
        Returns:
            df_rank: (df) values for each sub_k metric used to derive K_eco
            score
        '''
        ### initalize df ##
        df_rank = pd.DataFrame(columns = ['zip', 'state_id', 'K_energy',
                                            'K_air','K_climate'])
        df_rank['zip'] = self.state_zips # self.state_zips
        df_rank['state_id'] = self.state

        ## set to the values we have ##
        df_rank['K_energy'] = [i for i in self.state_df['fuel'].values]
        df_rank['K_air'] = [i for i in self.state_df['PM10'].values]
        df_rank['K_climate'] = [i for i in self.state_df['temp_variation'].values]

        return df_rank

def get_avg_energy(zip_code):
    '''
    Returns the avergage energy consumption from fossil fuels per year for
    inputed zip_code
    Input:
        zip_code: (str) zip_code
    Returns:
        city_fuel_use: (int) mean energy_usage derived from fossil fuels
        per year
    '''
    cite_data = energy.get_energy_data(zip_code)
    if type(cite_data) == str:
        city_fuel_use = 'NaN'
    else:
        cite = cite_data.transpose()
        city_fuel_use = cite.values[0][40]
    return city_fuel_use


def get_num_pollutants(zip_code):
    '''
    Returns the mean ppm of particles of large diameter (2.5 - 10 nm)
    in the input zip
    Input:
        zip_code: (str) zip_code
    Returns:
        particles_PM10: (float) mean particles per million of diameter (2.5 -
        10nm) in zip_code
    '''
    r = air.get_data(zip_code)
    if type(r) == str:
        particles_PM10 = 'NaN'
    elif len(r[0]) < 9:
        particles_PM10 = 'NaN'
    else:
        particles_PM10 = r[0][8]
    return particles_PM10


def get_variation(zip_code):
    '''
    Returns the sum of total temprature variation over winter and summer months
    Input:
        zip_code: (str) zip_code
    Returns:
        total_var: (float) combined temprature variation over summer and winter
        over the last 30 to 40 years
    '''
    weather_cycle = weather.zips_weather(zip_code)
    if type(weather_cycle) == str:
        return 'NaN'
    if 'temprature' not in weather_cycle.columns:
        return 'NaN'
    data_yearly = weather_cycle[['month','temperature']]
    data_winter = data_yearly.loc[lambda data_yearly: data_yearly['month'] == '12']
    data_summer = data_yearly.loc[lambda data_yearly: data_yearly['month'] == '06']
    i , j = data_summer.shape[0] , data_winter.shape[0]
    if i == 0 or j == 0:
        if i != 0:
            var_summer = data_summer['temperature'].describe().std()
            approx_var = var_summer * 2
        elif j != 0:
            var_winter = data_winter['temperature'].describe().std()
            approx_var = var_winter * 2
        else:
            return 'NaN'
        return approx_var

    else:
        stats_w = data_winter['temperature'].describe()
        var_winter = stats_w.std()
        stats_s = data_summer['temperature'].describe()
        var_summer = stats_s.std()
        total_var = var_summer + var_winter

        return total_var

def standardize_to_mean(df_k):
    '''
    Standardizes and normalizes K_var columns to find aggregate K_var
    Input:
        df_k: (df) unprocessed states_df
    Returns:
        df_k: (df) states_df with K_var column
    '''
    num_k = 0
    if df_k['K_energy'][0] != 'NaN':
        num_k += 1
    if df_k['K_climate'][0] != 'NaN':
        num_k += 1
    if df_k['K_air'][0] != 'NaN':
        num_k += 1
    df_k = df_k.replace('NaN', 0)


    # standardize df  #
    df_k['K_air'] = standardize_col(df_k['K_air'])
    df_k['K_energy'] = standardize_col(df_k['K_energy'])
    df_k['K_climate'] = standardize_col(df_k['K_climate'])

    # normalize df
    df_k['K_energy'] = normalize_col(df_k['K_energy'])
    df_k['K_air'] = normalize_col(df_k['K_air'])
    df_k['K_climate'] = normalize_col(df_k['K_climate'])

    # make the agrregate value #
    df_k['K_var'] = (df_k['K_air'] + df_k['K_energy'] + df_k['K_climate']) / num_k

    return df_k


def normalize_col(df_col):
    '''
    Normalizes df column
    Input:
        df_col: (series) pandas df column
    Returns:
        norm_col: (series) normalized pandas df column
    '''
    min_k = df_col.min()
    max_k = df_col.max()
    range_k = max_k - min_k
    if range_k == 0:
        return df_col
    norm_col = (df_col - min_k) / (max_k - min_k)

    return norm_col


def standardize_col(df_col):
    '''
    Standardizes df column
    Input:
        df_col: (series) pandas df column
    Returns:
        stand_col: (series) pandas df column divided by its mean
    '''
    if df_col.mean() == 0:
        return df_col
    stand_col = df_col / df_col.mean()

    return stand_col

def get_k_eco_states():
    '''
    Returns K_eco by state given random samples of zip_codes from each state
    Input:
        self: K_eco (object) our model
    Returns:
        df_states_k: (df) df of k_eco scores for each state given one random
        zip code fed into our model from each state
    '''
    # three samples of randomly generated zip_codes in each state #

    sample_1 = US_zips.random_sample_df()
    sample_2 = US_zips.random_sample_df()
    sample_3 = US_zips.random_sample_df()

    df_1 = get_df_k_for_sample(sample_1)
    df_2 = get_df_k_for_sample(sample_2)
    df_3 = get_df_k_for_sample(sample_3)

    df_mean =  pd.DataFrame(columns = ['state_id', 'K_energy', 'K_air' , 'K_climate'])
    df_mean['state_id'] = list(sample_1.axes[0])
    df_mean['K_energy'] = (df_1['K_energy'] + df_2['K_energy'] + df_3['K_energy'])/ 3
    df_mean['K_air'] = (df_1['K_air'] + df_2['K_air'] + df_3['K_air'])/ 3
    df_mean['K_climate'] = (df_1['K_climate'] + df_2['K_climate'] + df_3['K_climate'])/ 3
    df_states = standardize_to_mean(df_mean)

    return df_states




def get_df_k_for_sample(sample):
    test_zips = [i for i in sample['zip'].values]
    states = list(sample.axes[0])
    energy = [get_avg_energy(i) for i in test_zips]
    air = [get_num_pollutants(i) for i in test_zips]
    climate = [get_variation(i) for i in test_zips]
    df_states = pd.DataFrame(columns = ['state_id', 'K_energy', 'K_air' , 'K_climate'])
    df_states['state_id'] = states
    df_states['K_energy'] = energy
    df_states['K_air'] = air
    df_states['K_climate'] = climate
    df_states_k = standardize_to_mean(df_states)
    return df_states_k
