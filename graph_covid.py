import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from scipy.signal import savgol_filter

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
    parser.add_argument('--infected', action='store_true', default=False,
                        help='Plot infected, instead of confirmed cases ')
    parser.add_argument('--no_plot', action='store_true', default=False,
                        help='Do not plot anything')
    args = parser.parse_args()

    print("Reading file: " + args.file)
    try:
        covid_df = pd.read_csv(args.file)
    except pd.errors.ParserError:
        print("Error reading file")
        exit(1)
    except  FileNotFoundError:
        print("Error file "+ args.file + " Not found")
        exit(1)

    data_cols = ['Confirmed', 'Deaths', 'Recovered']
    model_cols = ['Infected', 'Deaths', 'Recovered']
    if args.infected:
        plot_cols = model_cols
    else:
        plot_cols = data_cols

    # covid_df.set_index('Date',inplace=True)
    covid_df['Infected'] = covid_df['Confirmed'] - \
        covid_df['Deaths'] - covid_df['Recovered']
    country_df = covid_df.loc[covid_df['Country'] == args.country]
    country_df = country_df.loc[country_df['Confirmed'] > 0]
    # Some countries have more than one region so use groupby
    coalesced_df = country_df.groupby('Date').sum()
    coalesced_diff = coalesced_df.diff()
    # First difference is noisy, use Savitzky–Golay to smooth it out
    data_np = coalesced_diff[plot_cols[0]].to_numpy()
    # print(data_np)
    filt_data = savgol_filter(data_np, 13, 2, axis=0)
    coalesced_diff['Smoothed'] = filt_data

    # plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
    coalesced_df[plot_cols].plot(logy=args.log)
    cases_fig = plt.gcf()
    cases_fig.autofmt_xdate()
    plt.title(args.country + " cases")

    ext_cols = plot_cols + ['Smoothed']
    coalesced_diff[ext_cols].plot(logy=args.log)
    diff_fig = plt.gcf()
    diff_fig.autofmt_xdate()
    plt.title(args.country + " new cases")

    if not args.no_plot:
        plt.show()
    else:
        cases_fig.savefig(args.country + '_cases.png')
        diff_fig.savefig(args.country + '_new_cases.png')
