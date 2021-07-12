
"""
Name: CASEY HEALEY
CS602: Section 1
Data: NYC Collison Data
URL: Link to your web application online (see extra credit)
Description:
The program is broken into two parts - "MAP" and "BREAKDOWN"

"MAP"
This program takes NYC Collison data and creates a map that can be filtered by date.
The program also outputs the average number of deaths and injuries per accident in the specified timeframe
and outputs a chart with the injuries and death breakdown for each borough, sorted by injuries

"BREAKDOWN"
The program's second page uses matplotlib and seaborn to create two visualizations - users select a factor,
borough and "injured or killed" and the output is a pie chart of 3 injured or killed groups
(pedestrians, motorist and cyclists)

At the bottom, using seaborn, the program uses the same filtered data to generate
a boxplot of the vehicle type & persons injured/killed

"""
import numpy as np
import streamlit as st
import pydeck as pdk
import pandas as pd
import datetime
from matplotlib import pyplot as plt
import seaborn as sns


MAPKEY = "pk.eyJ1IjoiY2FzZXloZWFsZXkiLCJhIjoiY2txd2J5aWQ1MG12YzJwdDl5anNmcTlmYiJ9.47eYp-VmVF0AGRM2bCHS6g"

@st.cache
def loaddata():
    df = pd.read_csv('/Users/caseyhealey/PycharmProjects/Practice_Problems/database.csv')
    # The dataset contains a few values that are outside the range of NYC
    # The code below deletes the rows with errors
    df = df[df['LATITUDE'].values > 39]
    df = df[(df['LONGITUDE'].values > -75) & (df['LONGITUDE'].values < -72)]
    df['DATE'] = pd.to_datetime(df['DATE'])
    df = df[df['LATITUDE'].notna()]
    df = df[df['LONGITUDE'].notna()]
    df = df[df['BOROUGH'].notna()]
    # creates a dataframe with Date, Latitude and Longitude
    # drops null values for mapping
    return df

df = loaddata()



def accidents_map(df):
    locations = tuple(zip(df['DATE'], df['LATITUDE'], df['LONGITUDE']))
    location = pd.DataFrame(locations, columns=["Date", "lat", "lon"])

    st.title("Accidents in 5 Boroughs")
    min_date = min(location['Date'].dt.date)
    max_date = max(location['Date'].dt.date)
    start_date = st.sidebar.date_input('Start date', datetime.date(2015,1,1), min_value = min_date, max_value = max_date)
    end_date = st.sidebar.date_input('End date', datetime.date(2017,1,1), min_value =  min_date, max_value=max_date)
    if start_date > end_date:
        st.error('Error: End date must fall after start date.')
    filtered_data = location[(location['Date'].dt.date >= start_date) & (location['Date'].dt.date <= end_date)]
    filtered_df = df[(df['DATE'].dt.date >= start_date) & (df['DATE'].dt.date <= end_date)]
    summary = filtered_df.groupby(["BOROUGH"])[["PERSONS INJURED", "PERSONS KILLED"]].sum()
    summary.sort_values(('PERSONS KILLED'), ascending=True)
    st.sidebar.text(f'Average number of injuries per accident \n for the time period selected: {round(filtered_df["PERSONS INJURED"].mean(),3)}')
    st.sidebar.text(f'Average number of deaths per accident \n for the time period selected: {round(filtered_df["PERSONS KILLED"].mean(),3)}')
    st.sidebar.text(f"Number of People Injured or Killed \n From {start_date} to {end_date}.")
    st.sidebar.dataframe(summary)
    st.subheader(f'Map of all accidents on {start_date} to {end_date}')
    st.map(filtered_data)

factors = []
boroughs = []
for i in df["VEHICLE 1 FACTOR"]:
    if i not in factors:
        factors.append(i)
for j in df["BOROUGH"]:
    if j not in boroughs:
        boroughs.append(j)


def accidents_pivot(df, factors, boroughs):
    st.title("Accident Factor Breakdown by Injury and Borough")
    col1, col2, col3 = st.beta_columns(3)
    which_factor = st.sidebar.selectbox("Factor", factors)
    which_borough = st.sidebar.radio("Borough", boroughs)
    which_result = st.sidebar.selectbox("Injured or Killed", ["Injured", "Killed"])
    filtered = df[(df["VEHICLE 1 FACTOR"] == which_factor) & (df["BOROUGH"] == which_borough)]
    pivot_injured = pd.pivot_table(filtered, index=["VEHICLE 1 FACTOR"],
                                   values=["PEDESTRIANS INJURED", "CYCLISTS INJURED", "MOTORISTS INJURED"],
                                   aggfunc=np.sum)
    pivot_killed = pd.pivot_table(filtered, index=["VEHICLE 1 FACTOR"],
                                  values=["PEDESTRIANS KILLED", "CYCLISTS KILLED", "MOTORISTS KILLED"],
                                  aggfunc=np.sum)

    pivot_killed_df = pd.DataFrame(pivot_killed)
    pivot_injured_df = pd.DataFrame(pivot_injured)

    explode = []
    count = []
    if which_result == "Injured":
        dataframe = pivot_injured_df
    elif which_result == "Killed":
        dataframe = pivot_killed_df
    for i in range(0, 3):
        count.append(dataframe.iloc[0,i])
    for i in range(0, 3):
        if count[i] == max(count):
            explode.append(.1)
        else:
            explode.append(0)
    if sum(count) == 0:
        "No Accidents with that Criteria "
    else:
        fig, ax = plt.subplots()
        plt.rcParams['font.sans-serif'] = 'Arial'
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['text.color'] = 'black'
        plt.rcParams['axes.labelcolor'] = 'slategrey'
        plt.rcParams['xtick.color'] = 'slategrey'
        plt.rcParams['ytick.color'] = 'slategrey'
        plt.rcParams['font.size'] = 12
        color_palette_list = ['teal', 'yellow', 'blue']
        labels = ["CYCLISTS INJURED", "MOTORISTS INJURED", "PEDESTRIANS INJURED"]
        ax.pie(count, explode=explode, labels=None,
           colors=color_palette_list, autopct='%1.0f%%',
           shadow=False, startangle=0,
           pctdistance=1.2, labeldistance=1.5)
        ax.axis('equal')
        ax.set_title(f"Breakdown of Accident Victims by Type ({which_result})")
        ax.legend(frameon=False, bbox_to_anchor=(2, 0.8), labels = labels)
        st.set_option('deprecation.showPyplotGlobalUse', False)
        st.pyplot()

    if which_result == "Injured":
        st.dataframe(pivot_injured)
        label = "PERSONS INJURED"
    elif which_result == "Killed":
        st.dataframe(pivot_killed)
        label = "PERSONS KILLED"

    boxplot = sns.boxplot(y=filtered["VEHICLE 1 TYPE"], x=filtered[label])
    boxplot.axes.set_title(f"Breakdown of {which_result} by Vehicle Type", fontsize=16)
    boxplot.set_ylabel("Vehicle Type")
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot()
def main():
    st.title("Welcome to the NYC Accidents Breakdown Interactive Webpage")

    first_option = st.selectbox("Would you like to see a map or a breakdown of accidents in NYC?", ["Map", "Breakdown"])

    if first_option == "Map":
        accidents_map(df)
    elif first_option == "Breakdown":
        accidents_pivot(df, factors, boroughs)

main()




##DOCUMENTED CODE:
#Error ' Map Date Input Code
#https://newbedev.com/streamlit-date-input-format-code-example
#Streamlit Form :https://blog.streamlit.io/introducing-submit-button-and-forms/
#Plotting help: https://towardsdatascience.com/python-plotting-basics-simple-charts-with-matplotlib-seaborn-and-plotly-e36346952a3a
