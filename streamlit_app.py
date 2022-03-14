from collections import namedtuple
import altair as alt 
import pandas as pd
import streamlit as st
from pytrends import *
from pytrends.request import TrendReq
import socket, math, datetime
from prophet import Prophet
from requests import get

def _max_width_():
    max_width_str = f"max-width: 1500px;"
    st.markdown(
        f"""
    <style>
    .reportview-container .main .block-container{{
        {max_width_str}
    }}
    </style>
    """,
        unsafe_allow_html=True, 
    ) 
_max_width_()

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            .viewerBadge_container__1QSob {display: none !important;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# This code is different for each deployed app.
#CURRENT_THEME = "blue"
#IS_DARK_THEME = True
# EXPANDER_TEXT = """
#     This is a custom theme. You can enable it by copying the following code
#     to `.streamlit/config.toml`:
#     ```python
#     [theme]
#     primaryColor = "#E694FF"
#     backgroundColor = "#00172B"
#     secondaryBackgroundColor = "#0083B8"
#     textColor = "#C6CDD4"
#     font = "sans-serif"
#     ```
#     """


#st.title('Predict Google Trends')
#st.text('Get Google Trends data for keywords')


period = 52
#ip = get('https://api.ipify.org').text
#ip

def main():
    user_input = st.text_input('enter the keyword and press "Make request"')
    if st.button('Make request'):
        with st.spinner("Training ongoing"):
            pytrend = TrendReq(hl='it-IT', tz=360)
            pytrend.build_payload([f'{user_input}'], cat=0, timeframe='today 5-y', geo='IT', gprop='')
            data = pytrend.interest_over_time()
            data = data[data.isPartial != "True"]

            data = data.drop('isPartial', 1)
            #st.text('data_graph')
            data_graph = data.copy()
            data_graph.reset_index(inplace=True)
            #data_graph
            #print(data_graph.info())
            #st.line_chart(data_graph)
            chart_trend = alt.Chart(data_graph).mark_line().encode(
                x=alt.X('date:T'),
                y=alt.Y(f'{user_input}')
            ).properties(title="Google Trends")
            st.altair_chart(chart_trend, use_container_width=True)


            related_queries_dict = pytrend.related_queries()
            # for rising related queries
            related_queries_rising = related_queries_dict.get(f'{user_input}').get('rising')
            # for top related queries
            related_queries_top = related_queries_dict.get(f'{user_input}').get('top')
            col1, col2 = st.columns(2)
            col1.header('Keyword correlate in crescita')
            col1.write(related_queries_rising, use_column_width=True)
            col2.header('Top Keyword correlate')
            col2.write(related_queries_top, use_column_width=True)


            data_predict = data.copy()
            data_predict.reset_index(inplace=True)
            #st.text('data_predict')
            #data_predict
            

            data_predict = data_predict.rename(columns={'date': 'ds'})
            data_predict = data_predict.rename(columns={f'{user_input}': 'y'})
            #data_predict.columns = ['ds', 'y']
            #data_predict

            m = Prophet(weekly_seasonality=True)
            m.fit(data_predict)

            future = m.make_future_dataframe(periods=period, freq='W')
            future.tail()
            forecast = m.predict(future)
            forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()
            df_prophet = forecast[['ds', 'yhat']]


            #st.text('data_prophet')
            df_prophet = df_prophet.rename(columns={'ds': 'date'})
            df_prophet = df_prophet.rename(columns={'yhat': f'{user_input}'})
            #df_prophet
            print(df_prophet.info())

            chart_prophet = alt.Chart(df_prophet).mark_line().encode(
                x=alt.X('date'),
                y=alt.Y(f'{user_input}')
            ).properties(title="Trend Forecast")
            #st.altair_chart(chart_prophet, use_container_width=True)

            full_df = pd.merge(df_prophet, data_graph, left_on='date', right_on='date', how='left')#.drop('id1', axis=1)
            full_df
            full_df = full_df.rename(columns={full_df.columns[1]: 'forecast'})
            full_df = full_df.rename(columns={full_df.columns[2]: 'training_data'})
            full_df

            a = alt.Chart(full_df).mark_area(opacity=0.5, color='#fe2c55').encode(x='date', y='forecast')
            b = alt.Chart(full_df).mark_area(opacity=0.6, color='#25f4ee').encode(x='date', y='training_data')
            c = alt.layer(a, b).properties(title="Forecast and Trend Comparison")
            st.write('Legenda: azzurro Google Trends, rosso Previsionale')
            st.altair_chart(c, use_container_width=True)
            
            def convert_df(full_df):
               return full_df.to_csv(sep=';',decimal=',',index=False).encode('utf-8')
            csv = convert_df(full_df)
            st.download_button(
               "Press to Download",
               csv,
               "file.csv",
               "text/csv",
               key='download-csv'
            )

            # #
            # #
            # #
            # #Data test
            # data_predict = data.copy()
            # data_predict.reset_index(inplace=True)
            # #st.text('data_predict_1')
            # data_predict.drop(index=data_predict.index[-period:], axis=0, inplace=True)
            # #st.text('data_predict_2')
            # #data_predict

            # data_predict = data_predict.rename(columns={'date': 'ds'})
            # data_predict = data_predict.rename(columns={f'{user_input}': 'y'})
            # #data_predict.columns = ['ds', 'y']
            # #data_predict

            # m = Prophet(weekly_seasonality=True)
            # m.fit(data_predict)

            # future = m.make_future_dataframe(periods=period, freq='W')
            # future.tail()
            # forecast = m.predict(future)
            # forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()
            # df_prophet = forecast[['ds', 'yhat']]


            # #st.text('data_prophet')
            # df_prophet = df_prophet.rename(columns={'ds': 'date'})
            # df_prophet = df_prophet.rename(columns={'yhat': f'{user_input}'})
            # #st.text('data_predict_3')
            # #df_prophet
            # print(df_prophet.info())

            # chart_prophet = alt.Chart(df_prophet).mark_line(opacity=0.3).encode(
            #     x=alt.X('date'),
            #     y=alt.Y(f'{user_input}')
            # ).properties(title="Trend Forecast")
            # #st.altair_chart(chart_prophet, use_container_width=True)

            # full_df = pd.merge(df_prophet, data_graph, left_on='date', right_on='date', how='left')#.drop('id1', axis=1)
            # #full_df

            # a = alt.Chart(full_df).mark_area(opacity=0.5, color='#fe2c55').encode(x='date', y='forecast')
            # b = alt.Chart(full_df).mark_area(opacity=0.6, color='#25f4ee').encode(x='date', y='training_data')
            # c = alt.layer(a, b).properties(title="Forecast and Trend test")
            # st.text('-----PREDICTION TEST-----')
            # st.write('Legenda: azzurro Google Trends, rosso Previsionale')
            # st.altair_chart(c, use_container_width=True)



if __name__ == "__main__":
    main()
