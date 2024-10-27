import pandas as pd 
import datetime
import yfinance as yf
import streamlit as st
from statsmodels.tsa.statespace.sarimax import SARIMAX
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.arima.model import ARIMA

from model import ValueExpression
from new_fetcher import NewAnalyzer
from open_ai_client import OpenAIClient
from sentiment_analyzer import SentimentAnalyzer
from tavily_client import TavilyClientApi
companies_registered = ['BTC-USD', 'MSFT', 'SPY', 'HOC.L', 'AMD', 'NVDA', '^IXIC', 'GC=F', 'AAPL']
st.title('Stock Price Prediction')
st.divider()  # 👈 Draws a horizontal rule
# .strftime('%Y-%m-%d')
def get_sentiment_analyzer():
    openai_client = OpenAIClient()
    return SentimentAnalyzer(openai_client)


def get_new_analyzer():
    openai_client = TavilyClientApi()
    return NewAnalyzer(openai_client)


def get_prediction(one_week_ago, btc):
    btc.index = btc.index = btc.index.tz_convert(None)
        # Display first few rows to confirm
    train = btc[btc.index <= pd.to_datetime(one_week_ago.strftime('%Y-%m-%d'), format='%Y-%m-%d')]
    test = btc[btc.index >= pd.to_datetime(one_week_ago.strftime('%Y-%m-%d'), format='%Y-%m-%d')]
    y = train['Close']
    SARIMAXmodel = SARIMAX(y, order = (5, 4, 2), seasonal_order=(2,2,2,12))
    SARIMAXmodel = SARIMAXmodel.fit()
    y_pred = SARIMAXmodel.get_forecast(len(test.index)+3)
    y_pred_df = y_pred.conf_int(alpha = 0.05) 
    y_pred_df["Predictions"] = SARIMAXmodel.predict(start = y_pred_df.index[0], end = y_pred_df.index[-1])
    y_pred_df.index = test.index.union(pd.date_range(test.index[-1] + pd.Timedelta(days=1), periods=3, freq='D'))
    y_pred_out = y_pred_df["Predictions"] 
    result = pd.DataFrame(y_pred_out.tail(3))
    return train,test,y_pred_out,result


async def main():
    with st.form("form_company"):
        st.write("Do you need a recommendation?")
        option_company_selected = st.selectbox(
            "Select",
            (companies_registered),
        )

        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.write("SELECTED OPTION: " + option_company_selected)

            one_week_ago, btc = search_yf_method(option_company_selected)

            train, test, y_pred_out, result = get_prediction(one_week_ago, btc)
            st.divider()
            # Display first few rows to confirm
            st.dataframe(btc.tail())
            await news_and_sentimental_analyzer_exec(option_company_selected)
            st.divider()
            draw_plot(option_company_selected, train, test, y_pred_out)
            st.divider()
            prediction_result_drawer(btc, result)

def search_yf_method(option_company_selected):
    current_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    one_year_ago = current_date - datetime.timedelta(days=365)
    one_week_ago = current_date - datetime.timedelta(days=3)
    btc = yf.download(option_company_selected, start=one_year_ago, end=current_date)

            # Flatten the multi-level columns
    btc.columns = [col[0] for col in btc.columns]

            # Reset index to make 'Date' a column and rename index to 'Date'
    btc.reset_index(inplace=True)
    btc.rename(columns={'index': 'Date'}, inplace=True)

            # Format the 'Date' column as '%Y-%m-%d'


            # Select only the 'Date' and 'Close' columns
    btc = btc[['Date', 'Close']]
            # Drop any rows with NaN values, if present
    btc.dropna(subset=['Date', 'Close'], inplace=True)
    btc.index = pd.to_datetime(btc['Date'], format='%Y-%m-%d')
    del btc['Date']
    return one_week_ago,btc

def prediction_result_drawer(btc, result):
    st.write('Prediction for the next 3 days')
    st.dataframe(result)
            # Calcular la diferencia entre el primer y el último valor de 'Close'
    pred_first = result['Predictions'].iloc[0]
    last_close = btc['Close'].iloc[-1]
    difference = pred_first - last_close

            # Mostrar la diferencia
    st.write(f"The return if you buy this action is: {difference}")

def draw_plot(option_company_selected, train, test, y_pred_out):
    fig, ax = plt.subplots()
    ax.plot(train, color = "black", label = 'Training')
    ax.plot(test, color = "red", label = 'Testing')
    ax.plot(y_pred_out, color = "orange", label = 'Predictions')

    ax.set_ylabel(option_company_selected)
    ax.set_xlabel('Date')
    ax.tick_params(axis='x', rotation=45)
    ax.set_title(f'Train/Test split for {option_company_selected} Data')
    st.pyplot(fig)

async def news_and_sentimental_analyzer_exec(option_company_selected):
    value_expression_instance = ValueExpression(content=option_company_selected)
    fetch_news = await get_new_analyzer().analyze(value_expression_instance)
    st.dataframe(fetch_news)
    concatenated_content = " ".join(item["content"] for item in fetch_news if "content" in item)
    value_expression_fetch_api = ValueExpression(content=concatenated_content)
    sentyment_analysis_result = await get_sentiment_analyzer().analyze(value_expression_fetch_api)
    st.write('Sentiment analysis result')
    st.write(sentyment_analysis_result)

import asyncio

asyncio.run(main())