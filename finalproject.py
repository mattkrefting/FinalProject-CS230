'''
Coder: Matt Krefting
Date: May 5 2023
Project Description: Final project that takes airport data and performs analytics. 
                     Eg) Finding Countries with most airports
                     I have performed a lambda function on line 115 to determine if an
                     airport is high altiude or not
'''
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import pydeck as pdk


# Function for calculating stats, returns more than one value
def stats_on_elevation(data):
    elevations = data['elevation_ft']
    mean = elevations.mean()
    minimum = elevations.min()
    maximum = elevations.max()
    return mean, minimum, maximum

#Creates a line graph with top countries with most airports (Chart #1)
def graph_top_countries_airports(top = 25):
    # Create a new series that counts all instances of a country in the data
    airport_count = data['iso_country'].value_counts()
    # Sorting data by descending order ()
    airport_count = airport_count.sort_values(ascending=False)
    top_countries = airport_count.head(top)
    plt.figure(figsize=(10,10))
    plt.plot(top_countries.index, top_countries.values)
    plt.xlabel('Country')
    plt.ylabel('Number of Airports')
    plt.title(f'Top {top} countries with the Most Airports')
    return plt

# Creates a bar graph of individual regions with all airport types (Chart #2)
def graph_region_airports_by_types(continent, country, region):
    plt.clf()
    #Filtering Data based on continent, country and region user selected (two or more conditions using AND - Data Analytics Capabilities #1)
    airport_count = data[(data['continent'] == continent) & (data['iso_country'] == country) & (data['iso_region'] == region)]
    #Frequency Count of 'Type' Column
    counts = airport_count['type'].value_counts()
    #Creating bar graph with x, y and title labels
    plt.bar(counts.index, counts.values)
    plt.title(f'Airport Types in {region}')
    plt.xlabel('Airport Types')
    plt.ylabel('Airport Count')
    return plt


# A function that graphs the countries that have the greatest amount of airports of a user-selected type
# Function has two or more parameters, one of which has a default value (Python Feature #1)
# Creates a pie chart of countries with most airports of a particular type (Chart #3)
def graph_countries_with_greatest_airport_of_type(airport_type, top = 25):
    plt.clf()
    #Filtering data by one condition, which is type (Data analytics capabilities #2)
    airport_count = data[(data['type'] == airport_type)]
    counts = airport_count['iso_country'].value_counts()
    top_countries = counts.head(top)
    plt.title(f"Top {top} countries with most {airport_type}")
    plt.pie(top_countries.values, labels = top_countries.index, autopct='%.1f%%')
    return plt


def obtain_data(data):
    data['continent'] = data['continent'].fillna('NA')
    # List comprehension to create a list of all unique airport types (Python feature #2)
    continents = [continent for continent in data['continent'].unique()]
    airport_types = [airport_type for airport_type in data['type'].unique()]
    countries = [country for country in data['iso_country'].unique()]
    regions = [region for region in data['iso_region'].unique()]
    # Returning multiple values (Python feature #3)
    return continents, countries, regions, airport_types

# Creates a map of airports with greatest elevation according to user input (Map)
def create_map_of_altitude_airports(data, altitude):
    # Sorting data in descending order by elevation_ft column (Data Analytics Capabilities #3)
    sorted_altitude_data = data.sort_values(by='elevation_ft', ascending=False)
    sorted_altitude_data[['Latitude', 'Longitude']] = data['coordinates'].str.split(',', expand=True).apply(pd.to_numeric)
    # Dropping coordinates column so we can separate into Latitude and Longitude Columns (Data Analytics Capablities #4)
    sorted_altitude_data = sorted_altitude_data.drop(columns=['coordinates'])
    altitude_airports = sorted_altitude_data[sorted_altitude_data['elevation_ft'] < altitude]
    altitude_airports = altitude_airports.sort_values('elevation_ft', ascending=False)
    top_airports = altitude_airports.head(10)[['type', 'name', 'elevation_ft', 'iso_region', 'municipality', 'Latitude', 'Longitude', "is_high_altitude"]]
    
    top_airports_locations = top_airports[['name', 'Latitude', 'Longitude']]
    st.write(top_airports)
    view_state = pdk.ViewState(
    latitude=0,
    longitude=25,
    zoom = 1,
    pitch = 0)

    layer1 = pdk.Layer('ScatterplotLayer',
                    data = top_airports_locations,
                    get_position = '[Latitude, Longitude]',
                    get_radius = 100000,
                    get_color = [209,61,61],
                    pickable = True)

    tool_tip = {"html": "Airport Name:<br/> <b>{name}</b> ",
                "style": { "backgroundColor": "steelblue",
                            "color": "white"}}
                            
    map = pdk.Deck(
        map_style='mapbox://styles/mapbox/streets-v12',
        initial_view_state=view_state,
        layers=[layer1],
        tooltip= tool_tip
    )
    st.write("Map:")
    return map

data = pd.read_csv("Data/airport-codes_csv.csv")
data['is_high_altitude'] = data['elevation_ft'].apply(lambda x: True if x >= 9000 else False)
continents, countries, regions, airport_types = obtain_data(data)
st.title('Below are the following data points about airport statistics around the world')
#Creating sidebar header (page design feature)
st.sidebar.header('Inputs')
#Creating radio button widget that is part of sidebar (Widget #1)
st.header("This graph contains the countries with the most airports")
st.write("You can modify this graph by choosing the top 10 or 25 countries on the sidebar.")
top_country = st.sidebar.radio("Top 10 Countries or Top 25 Countries with greatest # of airports", [10, 25])
st.pyplot(graph_top_countries_airports(top_country))

#Creating multiple selectboxes that is part of sidebar (Widget #2)
st.sidebar.write("Please select continent, country and region:")
continent = st.sidebar.selectbox('Continent: ', continents)
#Filtering based on continent input and retrieving all unique countries in that continent
country = st.sidebar.selectbox('Country: ', countries)
#Filtering based on country input and retrieving all unique regions in that country
region = st.sidebar.selectbox('Region: ', regions)

st.sidebar.write("Please Select Options for the piechart:")

airport_type = st.sidebar.selectbox('Airport type:', airport_types)

#Creating a slider that is part of sidebar (Widget #3)
x = st.sidebar.slider(f'Number of Countries for Most Airports Of Type {airport_type}',0,15,7)
st.sidebar.write('Please select an altitude for the map:')
altitude = st.sidebar.slider(f'Select Altitude for Map',0,29000,14500)
st.subheader(f"Bar Graph of Each Type of Airport in {region}")
st.pyplot(graph_region_airports_by_types(continent, country, region))
st.subheader(f"Pie Chart of Top {x} countries with the most {airport_type} type")
st.pyplot(graph_countries_with_greatest_airport_of_type(airport_type, x))

st.subheader(f"10 Highest Airports that are less than or equal to {altitude} ft in elevation")

st.pydeck_chart(create_map_of_altitude_airports(data, altitude))

st.subheader('Some statistics on the Elevations')

mean, minimum, maximum = stats_on_elevation(data)
stats_rows = [
    ["Minimum:", f"{minimum:5.2f} ft"],
    ["Maximum:", f"{maximum:5.2f} ft"],
    ["Average Elevation:", f"{mean:5.2f} ft"]]

for row in stats_rows:
    row_words = []
    for word in row:
        row_words.append(str(word).ljust(15))
    st.text("".join(row_words))