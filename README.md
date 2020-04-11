# Covid-19 EDA
This small collection of python scripts allow to scrape and plot the John Hopkings Dataset. 
You can check the original dataset at the official [github repo](https://github.com/CSSEGISandData/COVID-19) 

## Dependencies
* numpy
* scipy
* pandas
* matplolib

## Contents
In this sections every script present is described along with its usages and references.

### Scraping and preprocessing
covid-john.py scrapes the raw data from the official resources and preprocesses it into a more maneageable csv file. It is very simply to use:
```bash
  python3 covid-john
```
The output is a csv file named: covid-19-data-%d-%m-%Y.csv 
The schema is based on this kaggle dataset: [Novel Corona Virus 2019 Dataset](https://www.kaggle.com/sudalairajkumar/novel-corona-virus-2019-dataset)
To visually verify scrapping was succesfull the script also outputs the schema of the read csvs and plots a graph of cases in Mexico.
 
### Basic Graphing and EDA
graph-covid.py reads the previously scraped data and plots the information for one country. The default is Mexcio.
```bash
usage: graph-covid.py [-h] [--country COUNTRY] --file FILE [--log]
                      [--infected] [--no_plot]

Graph country curves.

optional arguments:
  -h, --help         show this help message and exit
  --country COUNTRY  Which country to plot, defaul Mexico
  --file FILE        Preprocessed csv dataset file
  --log              Use logarithmic scale
  --infected         Plot infected, instead of confirmed cases
  --no_plot          Do not plot anything, store figures to disk

```
The only required parameter is --file that points to the dataset previously donwloaded by the covid-john.py script.
The data plotted is the number of confirmed, deaths and recovered cases. It also plots new cases reported daily or first differences. An smoothed version of this graph is also provided since numerical differences tend to be very noisy.

