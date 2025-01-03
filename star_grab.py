from skyfield.api import Star, load
from skyfield.data import stellarium
from pprint import pprint
import numpy as np
# ============================== Grab to JSON ============================== #
# Get 
import json

def create_json():
    url = ('https://raw.githubusercontent.com/Stellarium/stellarium/master'
        '/skycultures/modern_st/constellationship.fab')

    with load.open(url) as f:
        constellations = stellarium.parse_constellations(f)
    # print(type(constellations))
    constellation_dict: dict = {}
    for star in constellations:
        unique_stars: set = set()
        name = star[0]
        stars_list = star[1]
        for connection in stars_list:
            unique_stars = unique_stars | {connection[0], connection[1]}
        constellation_dict.update({
            name: {
                'connections': stars_list,
                'stars': list(unique_stars) 
            }
        })
    pprint(constellation_dict, indent=4)

    with open('constellations.txt', 'w') as cns:
        json.dump(constellation_dict, cns, indent=4)

# ============================== Plot Gemini TEST ============================== #

import matplotlib.pyplot as plt

# Load the star catalog and ephemeris
from skyfield.data import hipparcos

def get_gemini_stars():
    with load.open(hipparcos.URL) as f:
        stars = hipparcos.load_dataframe(f)

    with open('Stars/constellations.txt', 'r') as cns:
        constellation_dict = json.load(cns)

    # ts = load.timescale()

    # List of Gemini stars (Hipparcos numbers for Pollux, Castor, etc.)
    gemini_hipparcos_ids = constellation_dict['Gem']['stars']

    # Get star data
    gemini_stars = stars.loc[gemini_hipparcos_ids]

    print(type(gemini_stars))

    print(gemini_stars.head())

    # Print star data (right ascension and declination)
    print(gemini_stars[['ra_degrees', 'dec_degrees']])

    # Extract right ascension (RA) and declination (DEC)
    ra = gemini_stars['ra_degrees']
    dec = gemini_stars['dec_degrees']

    # Plot the stars
    plt.figure(figsize=(8, 6))
    plt.scatter(ra, dec, color='blue')

    # Annotate the stars with their names
    # star_names = ['Pollux', 'Castor', 'Alhena', 'Wasat', 'Mebsuta']
    # for i, name in enumerate(star_names):
    #     plt.text(ra.iloc[i], dec.iloc[i], name, fontsize=12, ha='right')

    plt.title('Gemini Constellation')
    plt.xlabel('Right Ascension (degrees)')
    plt.ylabel('Declination (degrees)')
    plt.gca().invert_xaxis()  # Invert x-axis for standard sky appearance
    plt.grid(True)
    plt.show()

#Finding the names of the stars
from astroquery.simbad import Simbad
def get_star_names(id_number):
    # Configure Simbad to include names
    Simbad.add_votable_fields('ids')

    # Query by Hipparcos ID
    result = Simbad.query_object(f"HIP {id_number}")
    print(result['IDS'][0])

# ============================== Making my own reference dataframe ============================== #
    
import pandas as pd

def make_reference_dataframe():
    with load.open(hipparcos.URL) as f:
        stars = hipparcos.load_dataframe(f)
    
    with open('Stars/constellations.txt', 'r') as cns:
        constellation_dict = json.load(cns)

    star_list = set()
    for key in constellation_dict.keys():
        for star in constellation_dict[key]['stars']:
            star_list.add(star)
    star_list = list(star_list)
    star_list.sort()

    all_stars = stars.loc[star_list]

    star_df = all_stars[['ra_degrees', 'dec_degrees']]

    # star_df.to_csv('star_data.csv')
    return star_df

def count_consts():
    with open('Stars/constellations.txt', 'r') as cns:
        constellation_dict = json.load(cns)
    print(len(constellation_dict.keys()))

# ============================== Calculating the constellations ============================== #
def make_constellation_tikz(star_df):
    with open('Stars/constellations.txt', 'r') as cns:
        constellation_dict = json.load(cns)

    # star_df = pd.read_csv('Stars/star_data.csv')

    tikz_text = ''
    for key in constellation_dict.keys():
        stars = constellation_dict[key]['stars']
        connections = constellation_dict[key]['connections']

        const_df = star_df.loc[stars]
        ras = const_df['ra_degrees'].to_numpy()
        decs = const_df['dec_degrees'].to_numpy()

        ras = -1 * ras # Invert x-axis for standard sky appearance

        # Convert to radians mostly just to make the units smaller
        ras = ras * np.pi / 180 
        decs = decs * np.pi / 180

        # Make the (0, 0) point of the tikz at the bottom left corner of the constellation
        ras = ras - np.min(ras)
        decs = decs -  np.min(decs)

        if np.max(decs) > np.max(ras):
            scale = 5 / np.max(decs)
        else:
            scale = 5 / np.max(ras)

        # Round the numbers to make the output more legible
        ras = np.round(ras * scale, decimals=2)
        decs = np.round(decs * scale, decimals=2)

        star_dict = {}
        for star, ra, dec in zip(stars, ras, decs):
            star_dict.update({
                star: {
                    'ra': ra,
                    'dec': dec
                    }
            })

        # Make the tikz
        tikz_text += f'\\newcommand{{\\{key}}}{{\n\t\\constellation{{'

        for ra, dec in zip(ras, decs):
            tikz_text += f'\n\t\t\\starAt{{{ra}, {dec}}}{{0.1cm}}'
        
        tikz_text += '\n\t'

        for connection in connections:
            tikz_text += f'\n\t\t\\connectStars{{{star_dict[connection[0]]['ra']}, {star_dict[connection[0]]['dec']}}}{{{star_dict[connection[1]]['ra']}, {star_dict[connection[1]]['dec']}}}'
        
        tikz_text += '\n\t}\n}\n\n'
    
    with open('const_commands.tex', 'w') as cc:
        cc.write(tikz_text)

if __name__ == '__main__':
    # create_json()
    # get_gemini_stars()
    # get_star_names(116805)
    # star_df = make_reference_dataframe()
    # make_constellation_tikz(star_df)
    count_consts()
    pass