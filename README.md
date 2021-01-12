# PIEC-FinancialScript-Proj

## Requirements
This script is dedicated for Windows. It wasn't tested on Linux, but probably it wouldn't work because of the paths syntax.
In the directory where script is placed, user has to create img and setup directories.

## Required modules
* urllib
* json
* argparse
* datetime
* numpy
* pandas
* matplotlib
* jinja2
* pathlib

## Description
This script generates the financial report.
We can pass as an argument:
   * currency name in Polish or currency code - script generate the report about this currency,
   * 'gold' - script generates the report about the price of gold,
   * 'all' - script generates the report with the current table of currency rates.
   
We can also pass the additional argument:
   * '-b dd-mm-yyyy' - beginning of the period, by default it's datetime.now(),
   * '-e dd-mm-yyyy' - end of the period, by default it's datetime.now().
   
The '-l' option enables user to check the available currencies.
Every word in the multi-word currency name has to be separated by '_'.
Data for currencies are available from 02-01-2002.
Data for price of gold are available from 02-01-2013.

## Result
### All option
The script returns 'currencyTable.html' file which is placed in forms directory. This HTML file contains the table of all available currencies with the current currency rates.

### Gold or currency name option
The script returns 'report.html' file and 'priceTable.html' file which are placed in forms directory. The 'priceTable.html' file contains all available values of currency rates or
gold prices in the entered period. The 'report.html' file contains the description section in which the user can check the currency name, currency code, the begginning date of 
the period, the end date of the period, values in the first and last day of this period, min value in whole period, max value in whole period and average value. If there is no data,
description section contains a currency name, a currency code and 'No data' label in other fields. In the next section the website contains three charts. The first one shows 
the values in the entered period. If there is no values, it contains only the title 'No data'. The second one shows values available in the last five days. Under this image is a
checkbox, which enable user to load the image with mean value line. The third one shows average values for each month available in the last 155 days or the whole entered period. 
Same as above, user can load the image with mean value line. Left menu enable user to get
directly to each paragraph.
