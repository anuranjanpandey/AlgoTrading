import numpy as np
import pandas as pd
import requests
import math
from scipy import stats
import xlsxwriter
from statistics import mean
from algorithms.secrets import IEX_CLOUD_API_TOKEN
import streamlit as st
import io

def main():
        
    stocks = pd.read_csv('algorithms/sp_500_stocks.csv')


    def chunks(lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]   
            
    symbol_groups = list(chunks(stocks['Ticker'], 100))
    symbol_strings = []
    for i in range(0, len(symbol_groups)):
        symbol_strings.append(','.join(symbol_groups[i]))

    my_columns = ['Ticker', 'Price', 'One-Year Price Return', 'Number of Shares to Buy']



    final_dataframe = pd.DataFrame(columns = my_columns)

    for symbol_string in symbol_strings:
        batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=stats,quote&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}'
        data = requests.get(batch_api_call_url).json()
        for symbol in symbol_string.split(','):
            try:
                final_dataframe = final_dataframe.append(
                                                pd.Series([symbol, 
                                                        data[symbol]['quote']['latestPrice'],
                                                        data[symbol]['stats']['year1ChangePercent'],
                                                        'N/A'
                                                        ], 
                                                        index = my_columns), 
                                                ignore_index = True)
            except KeyError:
                pass
            



    final_dataframe.sort_values('One-Year Price Return', ascending=False, inplace=True)
    final_dataframe = final_dataframe[:50]
    final_dataframe.reset_index(inplace=True)

    # take input from website
    def portfolio_input():
        global portfolio_size
        portfolio_size = input('Enter the size of the portfolio:')
        try:
            val = float(portfolio_size)
        except ValueError:
            print('Please enter an Interger:')
            portfolio_size = input('Enter the portfolio size:')
    portfolio_size = st.number_input('Enter the portfolio size')


    position_size = float(portfolio_size)/len(final_dataframe.index)
    for i in range(len(final_dataframe)):
        final_dataframe.loc[i, "Number of Shares to Buy"] = math.floor(position_size / final_dataframe.loc[i, "Price"])


    hqm_columns = [
                    'Ticker', 
                    'Price', 
                    'Number of Shares to Buy', 
                    'One-Year Price Return', 
                    'One-Year Return Percentile',
                    'Six-Month Price Return',
                    'Six-Month Return Percentile',
                    'Three-Month Price Return',
                    'Three-Month Return Percentile',
                    'One-Month Price Return',
                    'One-Month Return Percentile',
                    'HQM Score'
                    ]

    hqm_dataframe = pd.DataFrame(columns = hqm_columns)

    for symbol_string in symbol_strings:
        batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=stats,quote&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}'
        data = requests.get(batch_api_call_url).json()
        for symbol in symbol_string.split(','):
            try:
                hqm_dataframe = hqm_dataframe.append(
                                                pd.Series([symbol, 
                                                        data[symbol]['quote']['latestPrice'],
                                                        'N/A',
                                                        data[symbol]['stats']['year1ChangePercent'],
                                                        'N/A',
                                                        data[symbol]['stats']['month6ChangePercent'],
                                                        'N/A',
                                                        data[symbol]['stats']['month3ChangePercent'],
                                                        'N/A',
                                                        data[symbol]['stats']['month1ChangePercent'],
                                                        'N/A',
                                                        'N/A'
                                                        ], 
                                                        index = hqm_columns), 
                                                ignore_index = True)
            except KeyError:
                pass


    time_periods = [
                    'One-Year',
                    'Six-Month',
                    'Three-Month',
                    'One-Month'
                    ]
    for row in hqm_dataframe.index:
        for time_period in time_periods:
        
            change_col = f'{time_period} Price Return'
            percentile_col = f'{time_period} Return Percentile'
            if hqm_dataframe.loc[row, change_col] == None:
                hqm_dataframe.loc[row, change_col] = 0.0

    for row in hqm_dataframe.index:
        for time_period in time_periods:
            if hqm_dataframe.loc[row, f'{time_period} Price Return'] == None:
                hqm_dataframe.loc[row, f'{time_period} Price Return'] = 0
            hqm_dataframe.loc[row, f'{time_period} Return Percentile'] = stats.percentileofscore(hqm_dataframe[f'{time_period} Price Return'], hqm_dataframe.loc[row, f'{time_period} Price Return'])/100





    for row in hqm_dataframe.index:
        momentum_percentile = []
        for time_period in time_periods:
            momentum_percentile.append(hqm_dataframe.loc[row, f'{time_period} Return Percentile'])
        hqm_dataframe.loc[row, 'HQM Score'] = mean(momentum_percentile)


    hqm_dataframe.sort_values(by='HQM Score', ascending=False, inplace=True)
    hqm_dataframe = hqm_dataframe[:50]
    hqm_dataframe.reset_index(inplace=True, drop=True)

    # input bhai log
    # portfolio_input()


    portfolio_size = float(portfolio_size) / len(hqm_dataframe.index)
    for i in hqm_dataframe.index:
        hqm_dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(position_size / hqm_dataframe.loc[i, 'Price'])


    # display dataframe
    st.dataframe(hqm_dataframe)

    # downloadeable excel sheet
    @st.cache
    def to_excel(df):
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, 'Momentum Strategy', index=False)



        background_color = '#0a0a23'
        font_color = '#ffffff'

        string_template = writer.book.add_format(
                {
                    'font_color': font_color,
                    'bg_color': background_color,
                    'border': 1
                }
            )

        dollar_template = writer.book.add_format(
                {
                    'num_format':'$0.00',
                    'font_color': font_color,
                    'bg_color': background_color,
                    'border': 1
                }
            )

        integer_template = writer.book.add_format(
                {
                    'num_format':'0',
                    'font_color': font_color,
                    'bg_color': background_color,
                    'border': 1
                }
            )

        percent_template = writer.book.add_format(
                {
                    'num_format':'0.0%',
                    'font_color': font_color,
                    'bg_color': background_color,
                    'border': 1
                }
            )


        column_formats = { 
                            'A': ['Ticker', string_template],
                            'B': ['Price', dollar_template],
                            'C': ['Number of Shares to Buy', integer_template],
                            'D': ['One-Year Price Return', percent_template],
                            'E': ['One-Year Return Percentile', percent_template],
                            'F': ['Six-Month Price Return', percent_template],
                            'G': ['Six-Month Return Percentile', percent_template],
                            'H': ['Three-Month Price Return', percent_template],
                            'I': ['Three-Month Return Percentile', percent_template],
                            'J': ['One-Month Price Return', percent_template],
                            'K': ['One-Month Return Percentile', percent_template],
                            'L': ['HQM Score', integer_template]
                            }

        for column in column_formats.keys():
            writer.sheets['Momentum Strategy'].set_column(f'{column}:{column}', 20, column_formats[column][1])
            writer.sheets['Momentum Strategy'].write(f'{column}1', column_formats[column][0], string_template)


        writer.save()
        processed_data = output.getvalue()
        return processed_data

    df_xlsx = to_excel(hqm_dataframe)
    st.download_button(label='📥 Download Results',
                                data=df_xlsx ,
                                file_name= 'momentum.xlsx')

if __name__ == "__main__":
    main()
