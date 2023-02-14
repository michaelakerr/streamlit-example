import datetime
import math

import pandas as pd
import streamlit as st

TOTAL_ENERGY_USAGE = 'Total Electricty Usage'


def update_first_number():
    day = st.session_state.date.day
    month = st.session_state.date.month
    year = st.session_state.date.year
    st.session_state.year = year
    if day < 10:
        if month < 10:
            st.session_state.file_date = '{}/0{}0{}0000'.format(
                year, month, day)
        else:
            st.session_state.file_date = '{}/{}0{}0000'.format(
                year, month, day)
    else:
        st.session_state.file_date = '{}/{}{}0000'.format(year, month, day)


def update_number(date):
    st.session_state.date = date
    st.session_state.file_date = date
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
    st.session_state.file_date = string
    st.session_state.year = year


if "date" not in st.session_state:
    st.session_state.date = datetime.datetime(2023, 1, 7).date()
    st.session_state.file_date = datetime.datetime(2023, 1, 7).date()
    update_first_number()

# Usage Data


def usage_data():
    df = pd.read_csv('./data/{}.CSV'.format(st.session_state.file_date), skipfooter=1, skiprows=16,
                     parse_dates=True, usecols=['Date', 'P_Avg[W]'])

    df['Date'] = pd.to_datetime(df['Date'])
    return df


def getSolarFileNumber(date):
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

# Solar Data


def solar_data(date):
    df = usage_data()
    solar = getSolarFileNumber(date)
    dfsolar = pd.read_csv('./solardata/{}.CSV'.format(solar),
                          parse_dates=True, usecols=['Date', ' data'])
    dfsolar['Date'] = pd.to_datetime(dfsolar['Date'], unit='ms', utc=True)
    dfsolar['Date'] = dfsolar['Date'].dt.tz_convert('Pacific/Auckland')
    dfsolar['Date'] = dfsolar['Date'].dt.tz_localize(None)

    New_df = pd.DataFrame(pd.date_range(
        pd.to_datetime(df['Date'][0]),
        pd.to_datetime(df['Date'][len(df['Date'])-1]),
        freq='300S',), columns=['Date']).merge(
        dfsolar, on=['Date'], how='outer').fillna(0)

    overall_df = pd.DataFrame(New_df.merge(
        df, on=['Date'], how='outer'))

    overall_df[TOTAL_ENERGY_USAGE] = overall_df[' data'] + \
        overall_df['P_Avg[W]']
    st.session_state.overall_df = overall_df
    selectedDate = overall_df['Date'][1].date()
    st.session_state.date = overall_df['Date'][1].date()
    update_number(selectedDate)
    return overall_df

# APP


def runApp():
    update_number(st.session_state.date_input)
    datea = solar_data(st.session_state.date_input)
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


def runChartLoader():
    st.title('Chia Solar Monitoring App', anchor=None)
    st.subheader('Usage for {}'.format(st.session_state.date_input))
    placeholder = st.empty()
    with placeholder.container():
        runApp()


st.date_input(
    'Selected Date', st.session_state.date, key="date_input", on_change=runChartLoader)
