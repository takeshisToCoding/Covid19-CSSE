import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from scipy.optimize import curve_fit

import sys
import argparse


def logistic_model(x, L, x0, k):
    """First derivative of sigmoid function"""
    exponent = -k * (x-x0)
    denominator = np.square(1 + np.exp(exponent))
    numerator = L * k * np.exp(exponent)
    return numerator/denominator


def gauss_model(x, amp, mean, dev):
    """Simple gaussian model, not meant as a probability distribution"""
    exponent = np.square((x-mean) / (dev))
    return amp*np.exp(-1/2 * exponent)


def gauss_fit(x, y, mean_ini, amp_ini, dev_ini):
    """ Model x,y as gaussian"""
    params, covar = curve_fit(gauss_model, x, y,
                              p0=[amp_ini, mean_ini, dev_ini],
                              bounds=(0, [np.inf, np.inf, np.inf]),
                              maxfev=1500,
                              ftol=0.00001)
    print(covar)
    return params


def logistic_fit(x, y, x0_ini,L_ini,k_ini):
    """ Model x,y as gaussian"""
    params, covar = curve_fit(logistic_model, x, y,
                              p0=[ L_ini, x0_ini, k_ini],
                              bounds=(0, [np.inf, np.inf, np.inf]),
                              maxfev=1500,
                              ftol=0.00001)
    print(covar)
    return params


def coalesce_df(df, country):
    """ Convert on a daily time model per country coalesced 
         by date across all provinces 
    """
    country_df = df.loc[covid_df['Country'] == country]
    country_df = country_df.loc[country_df['Confirmed'] > 0]
    country_df['Date'] = pd.to_datetime(country_df['Date'])
    # Some countries have more than one region so use groupby
    coalesced_df = country_df.groupby('Date').sum()
    first_case_date = coalesced_df.index[0]
    # Calculate days from first case
    coalesced_df['Days'] = (coalesced_df.index -
                            first_case_date) / pd.Timedelta(days=1)
    coalesced_df.reset_index(inplace=True)
    coalesced_df.set_index('Days', inplace=True)
    coalesced_diff = coalesced_df.diff()
    return coalesced_df, coalesced_diff


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Covid-19 gaussian modelling.')
    parser.add_argument('--country', action='store',
                        default='Mexico',
                        help='Which country to model, defaul Mexico')
    parser.add_argument('--file', action='store',
                        help='Preprocessed csv dataset file',
                        required=True)
    parser.add_argument('--log', action='store_true',
                        help='Use logarithmic scale',
                        default=False)
    parser.add_argument('--amplitude', action='store', default=5000, type=float,
                        help='Peak number of cases expected')
    parser.add_argument('--stddev', action='store', default=15, type=float,
                        help='Width of gaussian around peak infections')
    parser.add_argument('--logistic', action='store_true',
                        help='Use logistic model', default=False)
    parser.add_argument('--peak', action='store', default=70, type=float,
                        help='Number of days, from first infection to peak, to use as initial guess in curve fitting ')
    parser.add_argument('-k', '--growth-rate', action='store', default=0.15, type=float,
                        help='Logistic growth rate')
    args = parser.parse_args()

    print("Reading file: " + args.file)
    try:
        covid_df = pd.read_csv(args.file, index_col=0)
    except pd.errors.ParserError:
        print("Error reading file")
        exit(1)
    except FileNotFoundError:
        print("Error file " + args.file + " Not found")
        exit(1)

    covid_proc, covid_diff = coalesce_df(covid_df, args.country)

    days = covid_diff.index
    covid_new_cases = covid_diff['Confirmed'].to_numpy()
    covid_new_cases[0] = 0
    covid_new_deaths = covid_diff['Deaths'].to_numpy()
    covid_new_deaths[0] = 0
  
    if not args.logistic:
      amp_model, mean_model, dev_model = gauss_fit(
            days, covid_new_cases, args.peak, args.amplitude, args.stddev)
      param_str = ("Amplitude [new cases]: {}\n"
                   "Peak in [days]: {} \n"
                   "Std-dev [days]: {} \n")
    else:
      amp_model = args.amplitude
      mean_model = args.peak 
      dev_model = args.growth_rate

      amp_model, mean_model, dev_model = logistic_fit(
            days, covid_new_cases, args.peak, args.amplitude, args.growth_rate)
      param_str = ("Amplitude [new cases]: {}\n"
                   "Peak in [days]: {} \n"
                   "Growth rate []: {} \n")
      
    print("Estimated parameters")
    print(param_str.format(amp_model, mean_model, dev_model))
    days_model = np.linspace(0, 2*mean_model , 1000)

    if not args.logistic:
      new_cases_model = gauss_model(days_model,
                                    amp_model, mean_model, dev_model)
    else:
      new_cases_model = logistic_model(days_model,
                                    amp_model, mean_model, dev_model)
     

    # Graphing
    covid_dates = covid_proc['Date']
    initial_date = covid_dates.iloc[0].to_datetime64()
    time_deltas = days_model * (np.timedelta64(1, 'D')/np.timedelta64(1, 's'))
    # Numpy datest,datetimes and timedeltas do not play nice with pandas types
    time_deltas = time_deltas.astype('timedelta64[s]')
    dates_model = initial_date + time_deltas
    peak_idx = np.argmax(new_cases_model)
    print("Peak Date: {}".format(dates_model[peak_idx]))
    dot_size = 3.5

    fig, ax = plt.subplots()
    days_loc = mdates.DayLocator(interval=5)
    months_loc = mdates.MonthLocator()

    ax.scatter(covid_dates, covid_new_cases, s=dot_size, label="New cases")
    ax.scatter(covid_dates, covid_new_deaths, s=dot_size, label="New deaths")
    ax.plot(dates_model, new_cases_model, label="Model",
            color='red', linestyle='dashed')

    ax.legend()
    ax.set_title("New cases per day")
    ax.set_xlabel("Date")
    ax.set_ylabel("New Cases")
    ax.grid()
    ax.xaxis.set_major_locator(months_loc)
    ax.xaxis.set_minor_locator(days_loc)
    fig.autofmt_xdate()

    plt.show()
