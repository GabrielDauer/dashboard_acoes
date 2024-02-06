import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from datetime import datetime
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.grid import grid

def side_bar():
    st.image('images/udata.png')
    ticker_list = pd.read_csv('tickers_ibra.csv', index_col= 0)
    tickers = st.multiselect(label= 'Selecione as empresas:', options= ticker_list, placeholder= 'Códigos')
    tickers = [acao + '.SA' for acao in tickers]
    start_date = st.date_input('De', format= 'DD/MM/YYYY', value= datetime(2023, 1, 2))
    end_date = st.date_input('Até', format= 'DD/MM/YYYY', value= 'today')

    if tickers:
        prices = yf.download(tickers, start= start_date, end= end_date)['Adj Close']
        if len(tickers) == 1:
            prices = prices.to_frame()
            prices.columns = [tickers[0].rstrip('SA')]

        prices.columns = prices.columns.str.rstrip('.SA')
        prices['IBOV'] = yf.download('^BSVP', start= start_date, end= end_date)['Adj Close']

        return tickers, prices
    return None, None
    
def main(tickers, prices):
    weights = np.ones(len(tickers)) / len(tickers)
    prices['Portfólio'] = prices.drop('IBOV', axis= 1) @ weights
    norm_prices = 100 * prices / prices.iloc[0]
    retornos = prices.pct_change()[1:]
    volatilidade = retornos.std() * np.sqrt(252) #anualizada
    retorno = (norm_prices.iloc[-1] - 100) / 100

    mygrid = grid(5, 5, 5, 5, 5, 5, vertical_align= 'top')

    for acao in prices.columns:
        c = mygrid.container(border= True)
        c.subheader(acao, divider= 'red')
        col_a, col_b, col_c = c.columns(3)

        if acao == 'Portfólio':
            col_a.image('images/pie-chart-dollar-svgrepo-com.svg')

        elif acao == 'IBOV':
            col_a.image('images/pie-chart-svgrepo-com.svg')

        else:
            col_a.image(f'https://raw.githubusercontent.com/thefintz/icones-b3/main/icones/{acao}.png', width=85)
        col_b.metric(label= 'retorno', value= f'{retorno[acao]:.0%}')
        col_c.metric(label= 'volatilidade', value= f'{volatilidade[acao]:.0%}')
        style_metric_cards(background_color= 'rgba(255, 255, 255, 0)')

    col_1, col_2 = st.columns(2, gap= 'large')

    with col_1:
        st.subheader('Desempenho Relativo')
        st.line_chart(norm_prices, height= 600)
               
    with col_2:
        st.subheader('Risco-Retorno')
        fig = px.scatter(
            x= volatilidade,
            y= retorno,
            text= volatilidade.index,
            color= retorno / volatilidade,
            color_continuous_scale= px.colors.sequential.Bluered_r
        )

        fig.update_traces(
            textfont_color = 'white',
            marker= dict(size= 45),
            textfont_size = 10
        )

        fig.layout.yaxis.title = 'Retorno Total'
        fig.layout.xaxis.title = 'Volatilidade Anualizada'
        fig.layout.height = 600
        fig.layout.yaxis.tickformat = '.0%'
        fig.layout.xaxis.tickformat = '.0%'
        fig.layout.coloraxis.colorbar.title = 'Sharpe'
        st.plotly_chart(fig, use_container_width= True)

st.set_page_config(layout= 'wide')

with st.sidebar:
    tickers, prices = side_bar()

st.title("Dashboard para Análise de Ações")

if tickers:
    main(tickers, prices)
