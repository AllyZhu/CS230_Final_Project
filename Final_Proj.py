'''
Your Name: Ally Choo
Final Project
This program creates a website that finds the easily displays and processes data about vehicle collisions in NY. This program allows the user to find the likelihood of a collision based, sort data, display graphs/tables based on specifications.
'''

import time
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
from datetime import date, time
import plotly
import plotly.express as px


SOURCE_PATH = ".\\"
CSV_FILE = "nyc_crashes_sample.csv"
CSV_WITH_PATH = SOURCE_PATH+CSV_FILE

BANNER = "Statue_of_liberty_banner.jpg"

def read_csv(file_path: str):
    """
    read csv into dataframe
    :param file_path: file that's read and info is taken from
    :return df: dataframe 
    """
    
    df = pd.read_csv("nyc_crashes_sample.csv", header=0, usecols=['UNIQUE KEY', 'DATE', 'TIME', 'BOROUGH', 'LATITUDE', 'LONGITUDE',])

    # drop records with missing data
    df = df.dropna()
    
    # make date into date format and time into time format
    df['DATE'] = pd.to_datetime(df['DATE']).dt.date
    df['TIME'] = pd.to_datetime(df['TIME']).dt.time

    return df


def collision_prob(df, t, b):
    """
    find probability of a crash occuring based on time and borough
    :param t: time
    :param b: borough
    :return: proability as a percent 
    """

    # denominator is all the accidents
    denominator = len(df.index)

    # create dataframe with specified borough and time
    crashes = df[(df['BOROUGH'] == b) & (df['TIME'] == t)]

    # numerator is all accidents that meet specifications
    numerator = len(crashes.index)

    # calc prob
    prob = (numerator/denominator) * 100

    return round(prob, 2)


def create_map(df):
    """
    Creates map with locations of crashes
    :param df: dataframe
    :return: map with points
    """

    # change column names
    df = df.rename(columns={'LATITUDE': 'lat', 'LONGITUDE': 'lon'})
    
    st.map(df)


def pie_chart(df, b_list, table=False):

    """
    Writes pie chart that shows that amount of crashes in each borough
    :param df: dataframe
    :param b_list: list of boroughs
    :param table: True if you want to only return table
    :return: prints bar chart or returns table
    """

    # compared with user list to see what was not chosen
    all_b_list = ['QUEENS', 'BROOKLYN', 'BRONX', 'STATEN ISLAND', 'MANHATTAN']  
    
    # list of boroughs that weren't chosen
    not_b_list = []

    # rename unique key to number of accidents
    df1 = df.rename(columns={'UNIQUE KEY': 'Number of Accidents'})

    # create list of boroughs not in user selected borough list and drop those columns
    for i in all_b_list:
        if i not in b_list:
            df1 = df1.drop(df1[df1.BOROUGH == i].index)
        
    # find number of accidents by borough
    df1 = df1.groupby('BOROUGH').count()['Number of Accidents']

    # reset index
    df1 = df1.reset_index()
    
    # rename columns
    df1.columns = ['Borough', 'Number of Accidents']

    if table:
        return df1

    fig = px.pie(df1, values='Number of Accidents', names='Borough')
    st.write(fig)

def bar_graph(df, type='b', table=False):
    # rename unique key to number of accidents
    df2 = df.rename(columns={'UNIQUE KEY': 'Number of Accidents'})

    if type == 'b':
        df2 = df2.groupby('BOROUGH').count()['Number of Accidents']
        df2 = df2.reset_index()

        df2.columns = ['Borough', 'Number of Accidents']
        fig = px.bar(df2, x='Borough', y='Number of Accidents')

    if type == 't':
        df2 = df2.groupby('TIME').count()['Number of Accidents']
        df2 = df2.reset_index()
        df2.columns = ['Time', 'Number of Accidents']
        fig = px.bar(df2, x='Time', y='Number of Accidents')

    if type == 'd':
        df2 = df2.groupby('DATE').count()['Number of Accidents']
        df2 = df2.groupby('DATE').count()['Number of Accidents']
        df2 = df2.reset_index()
        df2.columns = ['Date', 'Number of Accidents']
        fig = px.bar(df2, x='Date', y='Number of Accidents')

    if table:
        return df2

    st.write(fig)

def line_chart(df, table=False, x_axis='Year'):

    df1 = df.rename(columns={'UNIQUE KEY': 'Number of Accidents'})

    df1['Year'] = pd.DatetimeIndex(df['DATE']).year
    df1['Month'] = pd.DatetimeIndex(df['DATE']).month

    df1 = df1.groupby(['BOROUGH', x_axis]).count()['Number of Accidents']

    df1 = df1.reset_index()

    fig = px.line(df1, x=x_axis, y='Number of Accidents', color='BOROUGH')

    if table:
        df1 = df1.set_index(x_axis)
        return df1

    st.write(fig)


def page0(df):

    image = Image.open(BANNER)
    st.image(image)

    st.header("About")
    st.subheader("The purpose of this webite is to display information about vehicle crashes in New York")
    st.caption("It's mostly for people who don't want to be hit by cars")

    st.markdown(
        """
        What's here:

        - **Chance of Vehicle Accident**: Shows chance accident occurs at [time] on [borough]
        - **Map**: Shows map of accidents based on specifications
        - **Find out More**: Displays table with filters as well as graphs
        - **Charts**: Displays some data about when and where crashes happen the most
        """
    )

def page1(df):

    st.title("Chance of Vehicle Accident")
    st.write("This will show you the likihood that an accident will occur at [time] in [borough]")

    # Pick time and borough
    time = st.time_input("Time")
    option = st.selectbox(
    'Borough',
    ('QUEENS', 'BROOKLYN', 'BRONX', 'STATEN ISLAND', 'MANHATTAN'))

    # Find probability
    prob = collision_prob(df, time, option)

    # Write message with probability
    st.write("The percent chace of an accident occuring at", time, "in", option, "is...")

    st.header(prob)


def page2(df):

    st.title("Map")
    st.write("This will show you whre accidents occued on [date] at [time] in [borough]")

    col1, col2 = st.columns(2)

    # Select date form, date to, time from, time to, and boroughs
    with col1:
        d_from = st.date_input("From Date:")
        d_to = st.date_input("To Date:")

        t_from = st.slider(
            "From Time:",
            value=(time(23, 00)))

        t_to = st.slider(
            "To Time:",
            value=(time(23, 00))
                )

        option = st.selectbox(
        'Borough',
        ('QUEENS', 'BROOKLYN', 'BRONX', 'STATEN ISLAND', 'MANHATTAN'))

        # create filtered dataframe
        df1 = df[(df.DATE >= d_from) & (df.DATE <= d_to) & (df.TIME >= t_from) & (df.TIME <= t_to) & (df.BOROUGH == option)]

    with col2:
        create_map(df1)

    
    # Before and after pandemic section
    st.header("Changes before and after 2020")

    # didn't go past 2017
    start_date = date(2016, 3, 1)

    # dataframe from before pandemic
    df_before = df[(df.DATE <= start_date) & (df.TIME >= t_from) & (df.TIME <= t_to) & (df.BOROUGH == option)]

    # dataframe after pandeic
    df_after = df[(df.DATE >= start_date) & (df.TIME >= t_from) & (df.TIME <= t_to) & (df.BOROUGH == option)]

    col3, col4, = st.columns(2)

    # write maps
    with col3:
        st.subheader("Before")
        create_map(df_before)

    with col4:
        st.subheader("After")
        create_map(df_after)
    

def page3(df):
    st.title("Find Out More")
    st.write("This page allows you to filter and sort data as well as display data in graphs.")

    # Select date form, date to, time from, time to, and boroughs
    st.header("Filters")

    col1, col2 = st.columns(2)
    
    # create checkboxes for user to pick how they want to filter the data
    with col1: 
        st.caption("What filters would you like to use")
        date_checkbox = st.checkbox("Date")
        time_checkbox = st.checkbox("Time")
        borough_checkbox = st.checkbox("Borough")

        apply_button = st.button("Apply")

    
    # display input widgets if user clicks corresponding checkbox
    with col2:
        if date_checkbox:
            d_from = st.date_input("From Date:")
            d_to = st.date_input("To Date:")

        if time_checkbox:
            t_from = st.slider(
                "From Time:",
                value=(time(23, 00)))

            t_to = st.slider(
                "To Time:",
                value=(time(23, 00))
            )

        if borough_checkbox:
            options = st.multiselect(
            'Borough(s)',
            ['QUEENS', 'BROOKLYN', 'BRONX', 'STATEN ISLAND', 'MANHATTAN'])
        else:
            options = ['QUEENS', 'BROOKLYN', 'BRONX', 'STATEN ISLAND', 'MANHATTAN']

    df1 = df.rename(columns={'UNIQUE KEY': 'Number of Accidents'})

    # filter after user clicks apply
    if apply_button:
        # Create dataframe with filter
        if date_checkbox:
            df1 = df1[(df1.DATE >= d_from) & (df1.DATE <= d_to)]
        if time_checkbox:
            df1 = df1[(df1.TIME >= t_from) & (df1.TIME <= t_to)]
        if borough_checkbox:
            df1 = df1[df1['BOROUGH'].isin(options)]

        # create tabs
        tab1, tab2, tab3 = st.tabs(["Table", "Bar Chart", "Pie Chart"])

        # data table 
        with tab1: 
            st.header("Data Table")
            st.write(df1)

        # bar graph
        with tab2:
            # write bar graph
            st.header("Crashes by Borough")
            bar_graph(df1, 'b')

            with st.expander("See Table"):
                st.write(bar_graph(df1, table=True))

        # pie chart
        with tab3:
            st.header("Crashes by Borough")
            pie_chart(df1, options)

            with st.expander("See Table"):
                st.write(pie_chart(df1, options, table=True))


def page4(df):
    st.title("Charts")
    st.subheader("See more stats to help you avoid getting hit")

    # write line chart by year
    st.header("Crashes by year")
    line_chart(df)
    with st.expander("See Table"):
        st.write(line_chart(df, table=True))

    # write line chart by month
    st.header("Crashes by month")
    line_chart(df, x_axis='Month')
    with st.expander("See Table"):
        st.write(line_chart(df, table=True, x_axis='Month'))

    # write bar chart
    st.header("Crashes by time")
    bar_graph(df, 't')
    with st.expander("See Table"):
        st.write(bar_graph(df, True, 'TIME'))


def main():

    # read in file
    file = read_csv(CSV_WITH_PATH)
    print(file)

    # create nav bar
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", ["Home", "Chance of Vehicle Accident", "Map", "Find out More","Charts"])
    
    if selection == "Home":
        page0(file)
    if selection == "Chance of Vehicle Accident":
        page1(file)
    if selection == "Map":
        page2(file)
    if selection == "Find out More":
        page3(file)
    if selection == "Charts":
        page4(file)


if __name__ == "__main__":
    main()
