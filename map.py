import pandas as pd
import numpy as np
import matplotlib.pyplot as plt, mpld3
from mpl_toolkits.basemap import Basemap
from matplotlib import cm
from matplotlib.colors import rgb2hex
from matplotlib.patches import Polygon
from io import BytesIO
import os


# Download 2018 shapefiles:
# https://www.census.gov/geographies/mapping-files/time-series/geo/carto-boundary-file.html

URL = ('https://gist.githubusercontent.com/a8dx/2340f9527af64f8ef'
        + '8439366de981168/raw/81d876daea10eab5c2675811c39bcd18a79a9212'
        + '/US_State_Bounding_Boxes.csv')
ZIP_SHAPEFILE = 'cb_2018_us_zcta510_500k'
STATE_SHAPEFILE = 'st99_d00'
STATE_ABBREV = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Palau': 'PW',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY',
}



def plot_kvars(df):
    '''
    Creates a color coded map according to a state's zip codes' k_var.
    Inputs:
        df: dataframe with zip codes and their corresponding k_var
    Returns: SVG figure
    '''

    fig, ax = plt.subplots()
    bound_df = pd.read_csv(URL)

    state = df['state_id'].iloc[0]
    row = bound_df[bound_df['STUSPS'] == state]
    min_lon = row['xmin'].item()
    min_lat = row['ymin'].item() 
    max_lon = row['xmax'].item()
    max_lat = row['ymax'].item()
    
    # Create map
    m = Basemap(llcrnrlon=min_lon, llcrnrlat=min_lat, urcrnrlon=max_lon,
                urcrnrlat=max_lat, projection="lcc", resolution=None,
                lat_0=min_lat, lat_1=max_lat, lon_0=min_lon, lon_1=max_lon)

    # Draw zip code area boundaries using zcta shapefile
    m.readshapefile(ZIP_SHAPEFILE, 'states')
    
    colors = {}
    zip_list = []
    cmap = cm.get_cmap('Blues')
    
    # Find the k_var and color for each zip code in the state
    for d in m.states_info: #m.states_info is a list of dictionaries
        found_zip = d['ZCTA5CE10']
        zip_list.append(found_zip)
        if found_zip in df['zip'].values:
            k_var = df[df['zip']==found_zip]['K_var'].item()
            colors[found_zip] = cmap(k_var)[:3]

    # Color the zip codes
    for index, seg in enumerate(m.states):
        if zip_list[index] in df['zip'].values:
            color = rgb2hex(colors[zip_list[index]])
            poly = Polygon(seg,facecolor=color,edgecolor='#000000')
            ax.add_patch(poly)
        
    # Show colorbar
    mm = cm.ScalarMappable(cmap=cmap)
    mm.set_array([0,1])
    cb = plt.colorbar(mm, ticks=np.arange(0, 1.2, 0.2), orientation="vertical")
    cb.set_label('Eco Variable')


    svg_file = BytesIO()
    plt.savefig(svg_file, format='svg')
    svg_file.seek(0)
    svg_data = svg_file.getvalue().decode()
    svg_data = '<svg' + svg_data.split('<svg')[1]

    return svg_data

def find_us_map(df):
    '''
    Creates a color coded map according to a state's average k_var.
    Inputs:
        df: dataframe with states and their corresponding k_var
    Returns: SVG figure
    '''
    fig, ax = plt.subplots()

    # For the continental US
    min_lon = -119
    min_lat = 20
    max_lon = -64
    max_lat = 49

    m = Basemap(llcrnrlon=min_lon, llcrnrlat=min_lat, urcrnrlon=max_lon,
                urcrnrlat=max_lat, projection="lcc", resolution=None,
                lat_1=33, lat_2=45, lon_0=-95)
    m.readshapefile(STATE_SHAPEFILE, 'country', linewidth=0.1)
    
    
    # For Alaska and Hawaii
    min_lon2 = -190
    min_lat2 = 20
    max_lon2 = -143
    max_lat2 = 46

    m2 = Basemap(llcrnrlon=min_lon2, llcrnrlat=min_lat2, urcrnrlon=max_lon2,
                 urcrnrlat=max_lat2, projection="merc", lat_ts=20)
    m2.readshapefile(STATE_SHAPEFILE, 'country', linewidth=0.1, drawbounds=False)
    

    # Plotting for the continental US
    colors = {}
    state_list = []
    cmap = cm.get_cmap('Blues')

    for d in m.country_info:
        found_state = d['NAME']
        found_state = STATE_ABBREV[found_state]
        if found_state not in ('PR'):
            k_var = df[df['state_id']==found_state]['K_var'].item()
            colors[found_state] = cmap(k_var)[:3]
        state_list.append(found_state) 

    for index, seg in enumerate(m.country):
        if state_list[index] not in ('PR'):
            color = rgb2hex(colors[state_list[index]])
            poly = Polygon(seg,facecolor=color,edgecolor='#000000')
            ax.add_patch(poly)
    
    # Plotting for Alaska and Hawaii
    colors2 = {}
    state_list2 = []

    for index, d in enumerate(m2.country_info):
        found_state2 = d['NAME']
        found_state2 = STATE_ABBREV[found_state2]
        if found_state2 in ('Alaska', 'Hawaii'):
            seg = m_.states[int(shapedict['SHAPENUM'] - 1)]
            k_var2 = df[df['state_id']==found_state2]['K_var'].item()
            color = cmap(k_var2)[:3]
            if found_state2 == 'Alaska':
                seg = [(x - 1900000, y + 250000) for x, y in seg]
            elif found_state2 == 'Hawaii':
                seg = [(x * 0.19 - 250000, y * 0.19 - 750000) for x, y in seg]
            poly = Polygon(seg, facecolor=color, edgecolor='#000000')
            ax.add_patch(poly)
            
    # Show colorbar
    mm = cm.ScalarMappable(cmap=cmap)
    mm.set_array([0,1])
    cb = plt.colorbar(mm, ticks=np.arange(0, 1.2, 0.2), orientation="vertical")
    cb.set_label('Eco Variable')
    

    svg_file = BytesIO()
    plt.savefig(svg_file, format='svg')
    svg_file.seek(0)
    svg_data = svg_file.getvalue().decode()
    svg_data = '<svg' + svg_data.split('<svg')[1]

    return svg_data




