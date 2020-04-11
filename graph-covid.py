import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import sys
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Graph country curves.')
    parser.add_argument('--country', action='store',
                        default='Mexico',
                        help='Which country to plot, defaul Mexico')
    parser.add_argument('--file', action='store',
                        help='Preprocessed csv dataset file',
                        required=True)
    parser.add_argument('--log', action='store_true',
                        help='Use logarithmic scale',
                        default=False)
    args = parser.parse_args()

    print("Reading file: " + args.file)
    try:
        covid_df = pd.read_csv(args.file)
    except pd.errors.ParserError:
        print("Error reading file")

    data_cols = ['Deaths', 'Recovered', 'Confirmed']
    model_cols = ['Infected','Deaths', 'Recovered']
    # covid_df.set_index('Date',inplace=True)
    covid_df['Infected'] = covid_df['Confirmed'] - \
        covid_df['Deaths'] - covid_df['Recovered']
    country_df = covid_df.loc[covid_df['Country'] == args.country]
    # Some countries have more than one region so use groupby
    coalesced_df = country_df.groupby('Date').sum()
    coalesced_diff = coalesced_df.diff()
    
    #plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
    #plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    coalesced_df[model_cols].plot(logy=args.log)
    plt.gcf().autofmt_xdate()
    plt.title(args.country)
    coalesced_diff[data_cols].plot(logy=args.log)
    plt.gcf().autofmt_xdate()
    plt.title(args.country)
    plt.show()
