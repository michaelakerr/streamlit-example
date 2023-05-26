

import datetime
import math

import pandas as pd
import streamlit as st

from streamlit_app import solar_data, update_number

TOTAL_ENERGY_USAGE = 'Total Electricty Usage'


def get_solar_filename(date):
    day = date.day
    month = date.month
    year = date.year
    string = str(year)
    if month < 10:
        string = string + "" + str(month)
    else:
        string = string + str(month)
    if day < 10:
        string = string + "" + str(day)
    else:
        string = string + str(day)
    return string


def get_energy_filename(date):
    day = date.day
    month = date.month
    year = date.year
    string = str(year) + "/"
    if month < 10:
        string = string + "0" + str(month)
    else:
        string = string + str(month)
    if day < 10:
        string = string + "0" + str(day) + "0000"
    else:
        string = string + str(day) + "0000"
    return string


def energy_usage_data(date):
    filename = get_energy_filename(date)
    df = pd.read_csv('./data/{}.CSV'.format(filename), skipfooter=1, skiprows=16,
                     parse_dates=True, usecols=['Date', 'P_Avg[W]'])

    df['Date'] = pd.to_datetime(df['Date'])
    return df


def solar_gen_data(date):
    filename = get_solar_filename(date)
    dfsolar = pd.read_csv('./solardata/{}.csv'.format(filename),
                          parse_dates=True, usecols=['Date', ' data'])

    dfsolar['Date'] = pd.to_datetime(dfsolar['Date'], unit='ms', utc=True)
    dfsolar['Date'] = dfsolar['Date'].dt.tz_convert('Pacific/Auckland')
    dfsolar['Date'] = dfsolar['Date'].dt.tz_localize(None)
    return dfsolar


def update_chart_CSV(dataframe):
    # get normal data
    list_of_files = []
    for date in dataframe:
        df = energy_usage_data(date)
        list_of_files.append(df)

    list_of_solar_files = []
    # get solar data
    for date in dataframe:
        df = solar_gen_data(date)
        list_of_solar_files.append(df)

    df_energy = pd.concat(list_of_files, axis=0, ignore_index=True)
    df_solar = pd.concat(list_of_solar_files, axis=0, ignore_index=True)

    New_df = pd.DataFrame(pd.date_range(
        pd.to_datetime(df_energy['Date'][0]),
        pd.to_datetime(df_energy['Date'][len(df['Date'])-1]),
        freq='300S',), columns=['Date']).merge(
        df_solar, on=['Date'], how='outer').fillna(0)

    overall_df = pd.DataFrame(New_df.merge(
        df_energy, on=['Date'], how='outer'))

    overall_df[TOTAL_ENERGY_USAGE] = overall_df[' data'] + \
        overall_df['P_Avg[W]']
    st.line_chart(overall_df[['Date', 'P_Avg[W]', ' data',
                              TOTAL_ENERGY_USAGE]], x='Date')

    col1, col2, col3, col4 = st.columns(4)
    col1Metric = round((overall_df[TOTAL_ENERGY_USAGE].sum()/1000)*(5/60), 2)
    col2Metric = round(((overall_df[' data'].sum())*(5/60))/1000, 2)
    col3Metric = round(col2Metric / col1Metric * 100, 2)
    col4Metric = round((col1Metric * 0.2899) - (col2Metric * 0.12), 2)
    col1.metric(label="kWh Usage",
                value=col1Metric, delta="")
    col2.metric(label="Solar kWh Generation",
                value=col2Metric, delta="")
    col3.metric(label="% Solar",
                value=col3Metric, delta="")
    col4.metric(label="Total Cost ",
                value=('$' + str(col4Metric)))
    col4.write("Cost: 28.99c")
    col4.write("Solar: 12c")
    st.write(overall_df)


def update_first_numbers():
    # write all dates between
    d1 = st.session_state.start_date
    d2 = st.session_state.end_date
    d = pd.date_range(d1, d2)
    update_chart_CSV(d)


if "start_date" not in st.session_state and "end_date" not in st.session_state:
    st.session_state.start_date = datetime.datetime(2023, 1, 7).date()
    st.session_state.end_date = datetime.datetime(2023, 1, 8).date()
    st.session_state.file_date = datetime.datetime(2023, 1, 7).date()
    update_first_numbers()


def runApp():
    update_number(st.session_state.date_input)
    datea = solar_data(st.session_state.date)
    st.line_chart(datea[['Date', 'P_Avg[W]', ' data',
                         TOTAL_ENERGY_USAGE]], x='Date')
    col1, col2, col3 = st.columns(3)
    col1Metric = round((datea[TOTAL_ENERGY_USAGE].sum()/1000)*(5/60), 2)
    col2Metric = round(((datea[' data'].sum())*(5/60))/1000, 2)
    col3Metric = round(col2Metric / col1Metric * 100, 2)
    col1.metric(label="kWh Usage",
                value=col1Metric, delta="")
    col2.metric(label="Solar kWh Generation",
                value=col2Metric, delta="")
    col3.metric(label="% Solar",
                value=col3Metric, delta="")


col1, col2, col3 = st.columns(3)

with col1:
    st.date_input(
        'Selected Date', st.session_state.start_date, key="start_date", on_change=update_first_numbers)

with col2:
    st.date_input(
        'Selected Date', st.session_state.end_date, key="end_date", on_change=update_first_numbers)
