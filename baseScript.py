# -*- coding: utf-8 -*-

'''
Currancy rates script
'''

import urllib.request as rq
from urllib.error import HTTPError
import json
import argparse
from datetime import datetime
from datetime import timedelta
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import jinja2
from pathlib import Path

description = '''
This script generates the financial report.
We can pass as an argument:
   * currency name in Polish or currency code - script generate the report about this currency,
   * 'gold' - script generates the report about the price of gold,
   * 'all' - script generates the report with the current table of currency rates.
We can also pass the additional argument:
   * '-b dd-mm-yyyy' - the begin of the period,
   * '-e dd-mm-yyyy' - the end of the period.
To check the available currencies you can use the '-l' option.
Every word in the multi-word currency name has to be separated by '_'.
Data for currencies are available from 02-01-2002.
Data for price of gold are available from 02-01-2013.
'''

# ================== Parser ======================

#This method handle the user input.    
def parserFunction():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=description)
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-l', '--listOfCurrencies', action='store_true', help=u'''Prints the list of available currencies''')
    parser.add_argument('-b', '--beginDate', type=lambda s: datetime.strptime(s +  " {:d}".format(datetime.now().hour), '%d-%m-%Y %H'), default=datetime.now(), help=u'''The first date when we need the currency rate.''')
    parser.add_argument('-e', '--endDate', type=lambda s: datetime.strptime(s + " {:d}".format(datetime.now().hour), '%d-%m-%Y %H'), default=datetime.now(), help=u'''The last date when we need the currency rate.''')    
    parser.add_argument('argument', nargs='?', default='all', type=str,  help=u'''Currency name in Polish, currency code or other available option.''')        
        
    args = parser.parse_args()
    
    if args.listOfCurrencies:
        printListOfAvailableNames()
    
    if args.argument.find('_'):
        args.argument = args.argument.split('_')
        args.argument = ' '.join(args.argument)
    
    currentDate = datetime.now()
    
    if args.endDate.year == currentDate.year and args.endDate.month == currentDate.month and args.endDate.day == currentDate.day and args.endDate.hour < 16:
        args.endDate = args.endDate - timedelta(days=1)
    
    if args.beginDate.year == currentDate.year and args.beginDate.month == currentDate.month and args.beginDate.day == currentDate.day and args.beginDate.hour < 16:
        args.beginDate = args.beginDate - timedelta(days=1)
    
    if not isValidDate(args.beginDate):
        raise ValueError('Wrong begin date of the period!')
    if not isValidDate(args.endDate):
        raise ValueError('Wrong end date of the period!')
    if not checkPeriod(args.beginDate, args.endDate):
        raise ValueError('Wrong relation between begin and end date!')
    if not checkArgumentByCode(args.argument.upper()) and not checkArgumentByName(args.argument) and not args.argument == 'gold' and not args.argument == 'all':
        raise ValueError('Wrong argument!')
    else:
        if args.argument == 'gold':
           if not checkGoldDataAvailability(args.beginDate):
                raise ValueError("Couldn't get price of gold data!")
        else:
           if not checkCurrencyDataAvailability(args.beginDate):
                raise ValueError("Couldn't get currency data!")
    
    return args

# ================== End of parser ========================

# ================== Dates handling =========================

#This method check if the entered date is before today.
def isValidDate(date):
    if date.year > datetime.now().year:
        return False
    if date.year == datetime.now().year and date.month > datetime.now().month:
        return False
    if date.year == datetime.now().year and date.month == datetime.now().month and date.day > datetime.now().day:
        return False
    
    return True

#This method check if the begin date of the period is before the end date of the period.
def checkPeriod(beginDate, endDate):
    if (beginDate.year < endDate.year):
        return True
    if (beginDate.year == endDate.year) and (beginDate.month < endDate.month):
        return True
    if (beginDate.year == endDate.year) and (beginDate.month == endDate.month) and (beginDate.day <= endDate.day):
        return True
    return False

#This function check if we can get the price of gold. It is caused by the data source, which handles the data from 02-01-2013.
def checkGoldDataAvailability(beginDate):
    if beginDate.year < 2013:
        return False
    else: 
        if beginDate.month == 1 and beginDate.day < 2 and beginDate.year == 2013:
            return False
        else:
            return True

#This function check if we can get the currency rate. It is caused by the data source, which handles the data from 02-01-2002.
def checkCurrencyDataAvailability(beginDate):
    if beginDate.year < 2002:
        return False
    else:
        if beginDate.month == 1 and beginDate.day < 2 and beginDate.year == 2002:
            return False
        else:
            return True

#This method returns the last day of each month.
def getEndOfTheMonth(date):
    if date.month == 12:
        tempDate = date
        return tempDate.replace(day=31)
    else:
        tempDate = date
        return tempDate.replace(month=tempDate.month+1, day=1) - timedelta(days=1)

#This method calculates number of months in the given period.
def calculateNumberOfMonths(begin, end):
    diffOfYears = 0
    numOfMonths = 0
    if end.year != begin.year and end.year - begin.year >= 2:
        diffOfYears = end.year - (begin.year + 1)
        numOfMonths = diffOfYears * 12 + (12 - begin.month) + 1 + end.month
    elif end.year == begin.year and end.month != begin.month:
        numOfMonths = end.month - begin.month + 1
    elif end.year == begin.year and end.month == begin.month:
        numOfMonths = 0
    else:
        numOfMonths = 12 + end.month - begin.month + 1
    return numOfMonths

# ===================== End of dates handling ======================

# ===================== Handling the currency argument ==================

#This function return the type of the currency table, it could be 'A' or 'B'.
def checkTableType(currName):
    qu = 'http://api.nbp.pl/api/exchangerates/tables/A/'
    dat = rq.urlopen(qu)
    lista = json.loads(dat.read())
    sl = lista[0]
    listOfCurr = sl['rates']
    currencyList = []
    codeList = []
    for element in listOfCurr:
        currencyList.append(element['currency'])
        codeList.append(element['code'])
    letter = 'b'
    for element in currencyList:
        if currName == element:
            letter = 'a'
    for element in codeList:
        if currName == element:
            letter = 'a'
    return letter

#This method check if the entered currency exisits in data source.    
def checkArgumentByName(argument): 
    currencyNamesList = prepareSpecialListOfCurriencies('currency')
    for element in currencyNamesList:
        if argument == element:
            return True
    return False

#This method check if the entered currency exists in data source.    
def checkArgumentByCode(argument):
    currencyCodesList = prepareSpecialListOfCurriencies('code')
    for element in currencyCodesList:
        if argument == element:
            return True
    return False    

#This method returns the currency code of the given currency name.
def getCurrencyCode(currName):
    currencyNamesList = prepareSpecialListOfCurriencies('currency')
    currencyCodesList = prepareSpecialListOfCurriencies('code')
    idx = 0;
    for element in currencyNamesList:
        if element == currName:
            break
        idx = idx + 1
    
    code = currencyCodesList[idx]
    return code

#This method returns the currency name of the given currency code.
def getCurrencyName(currCode):
    currCode = currCode.upper()
    currencyNamesList = prepareSpecialListOfCurriencies('currency')
    currencyCodesList = prepareSpecialListOfCurriencies('code')
    idx = 0;
    for element in currencyCodesList:
        if element == currCode:
            break
        idx = idx + 1
    
    name = currencyNamesList[idx]
    return name
    
#This method prints a list of available currencies (only names).
def printListOfAvailableNames():
    print('Available currencies: ')
    listCurr = prepareSpecialListOfCurriencies('currency')
    for element in listCurr:
        print('* ' + element)

# ======================= End of handling currency argument ==================

# ======================= Handling the 'all' option ====================

#This method prepare the list of currencies names or currencies codes.
def prepareSpecialListOfCurriencies(type):
    specialList = []
    try:
        qu = 'http://api.nbp.pl/api/exchangerates/tables/A/'
        dat = rq.urlopen(qu)
        lista = json.loads(dat.read())
        sl = lista[0]
        listOfCurr = sl['rates']
        for element in listOfCurr:
            specialList.append(element[type])
    except HTTPError as e:
        print("Couldn't get data! It might be caused by the lack of data.")
    try:
        qu = 'http://api.nbp.pl/api/exchangerates/tables/B/'
        dat = rq.urlopen(qu)
        lista = json.loads(dat.read())
        sl = lista[0]
        listOfCurr = sl['rates']
        for element in listOfCurr:
            specialList.append(element[type]) 
    except HTTPError as e:
        print("Couldn't get data! It might be caused by the lack of data.")
        
    return specialList

#This method prepare the table of all currencies and write it on the disk in setup directory.
def prepareTableOfAllCurrencies():
    listOfNames = prepareSpecialListOfCurriencies('currency')
    listOfCodes = prepareSpecialListOfCurriencies('code')
    listOfRates = prepareSpecialListOfCurriencies('mid')
         
    data = {'Currency name':listOfNames, 'Currency code':listOfCodes, 'Rate':listOfRates}
    currencyTable = pd.DataFrame(data)
    name = 'setup\\currencyTable.csv'
    currencyTable.to_csv(name,sep=';',index=False)
    prepareTableJsonFile('currencyTable', 'thirdForm.html', '', '')

# ======================== End of handling the 'all' option =====================
 
# ======================== Data preparation for currency case ===================== 
 
#This method prepares the report of currency rates or price of gold for each month. 
def prepareMonthlyPartOfTheData(letter, code, begin, end):
    beginDate = begin.strftime("%Y-%m-%d")
    endDate = end.strftime("%Y-%m-%d")
    tempList = []
    tempDateList = []
    
    if code == 'gold':
        if end.year == begin.year and end.month == begin.month and end.day == begin.day:
            qu = 'http://api.nbp.pl/api/cenyzlota/' + endDate
        else:
            qu = 'http://api.nbp.pl/api/cenyzlota/' + beginDate + '/' + endDate
        
        #print(qu)
        try:
            dat = rq.urlopen(qu)
            sl = json.loads(dat.read())
            for element in sl:
                tempDateList.append(element['data'])
                tempList.append(element['cena'])
        except HTTPError as e:
            print("Couldn't get data in " + beginDate + " - " + endDate + "! It might be caused by the lack of data at this date.")
    else:
        if end.year == begin.year and end.month == begin.month and end.day == begin.day:
            qu = 'http://api.nbp.pl/api/exchangerates/rates/' + letter + '/' + code + '/' + endDate + '/'
        else:
            qu = 'http://api.nbp.pl/api/exchangerates/rates/' + letter + '/' + code + '/' + beginDate  + '/' + endDate + '/'
    
        #print(qu)
        try:
            dat = rq.urlopen(qu)
            sl = json.loads(dat.read())
            for element in sl['rates']:
                tempDateList.append(element['effectiveDate'])
                tempList.append(element['mid'])
        except HTTPError as e:
            print("Couldn't get data in " + beginDate + " - " + endDate + "! It might be caused by the lack of data at this date.")
    return (tempDateList, tempList)

#This method returns the arrays of dates and values in the period entered by user    
def getImportantData(valuesList, datesList, beginDate): 
    importantValues = []
    importantDates = []
    idx = 0
    isNotFound = True
    
    delta = beginDate - datetime.strptime(datesList[len(datesList)-1], '%Y-%m-%d')
    if delta.days <= 0:
        while isNotFound: 
            for i in range(0, len(datesList)):
                tempDate = datetime.strptime(datesList[i], '%Y-%m-%d') 
                if tempDate.year == beginDate.year and tempDate.month == beginDate.month and tempDate.day == beginDate.day:
                    idx = i
                    isNotFound = False
            beginDate = beginDate + timedelta(days=1)
    
        for i in range(idx, len(datesList)):
            importantValues.append(valuesList[i])
            importantDates.append(datesList[i])
    return (importantDates, importantValues)
    
#This method prepares the plots and table of currency rates or price of gold.
def prepareDataForReport(data):
    lista = []
    tempBegin = data.beginDate
    if data.argument != 'gold':
        if len(data.argument) < 4:
            name = getCurrencyName(data.argument)
            code = data.argument.upper()
        else:
            name = data.argument
            code = getCurrencyCode(name)
        letter = checkTableType(name)
    else:
        letter = ''
        code = data.argument
        name = data.argument
     
    dateDiff = data.endDate - data.beginDate
    if dateDiff.days <= 155:
        tempBegin = data.endDate - timedelta(days=155)
    else:
        tempVal = dateDiff.days
        while tempVal % 5 != 0:
            tempVal = tempVal + 1
        tempBegin = data.endDate - timedelta(days=tempVal)    
    
    numberOfMonths = calculateNumberOfMonths(tempBegin, data.endDate)
    for i in range(numberOfMonths-1):
        tempEnd = getEndOfTheMonth(tempBegin)
        lista.append(prepareMonthlyPartOfTheData(letter, code, tempBegin, tempEnd))
        tempBegin = tempEnd + timedelta(days=1)
                
    lista.append(prepareMonthlyPartOfTheData(letter, code, tempBegin, data.endDate))
        
    datesList = []
    valuesList = []
    monthsMeans = []
    monthsNames = []
    importantValuesList = []
    for element in lista:
        if len(element[0]) > 0:
            for arg in element[0]:
                datesList.append(arg)
            for arg in element[1]:
                valuesList.append(arg)
            monthsMeans.append(np.mean(element[1]))
            monthsNames.append(element[0][0])
    
    lastFiveValues = []
    lastFiveDates = []
    for i in range(len(valuesList)-5, len(valuesList)):
        lastFiveValues.append(valuesList[i])
        lastFiveDates.append(datesList[i])

    for i in range(0, len(monthsNames)):
        monthsNames[i] = datetime.strptime(monthsNames[i], '%Y-%m-%d').strftime("%B %Y")
    
    importantData = getImportantData(valuesList, datesList, data.beginDate)
    if len(importantData[1]) > 0:
        if importantData[1][0] > 0.009:
            beginVal = "{:10.2f}".format(importantData[1][0])
            endVal = "{:10.2f}".format(importantData[1][len(importantData[1])-1])
            average = "{:10.2f}".format(sum(importantData[1])/len(importantData[1]))
            beginDate = importantData[0][0]
            endDate = importantData[0][len(importantData[1])-1]
            minVal = "{:10.2f}".format(min(importantData[1]))
            maxVal = "{:10.2f}".format(max(importantData[1]))
        else:
            beginVal = "{:10.3f}".format(importantData[1][0])
            endVal = "{:10.3f}".format(importantData[1][len(importantData[1])-1])
            average = "{:10.3f}".format(sum(importantData[1])/len(importantData[1]))
            beginDate = importantData[0][0]
            endDate = importantData[0][len(importantData[1])-1]
            minVal = "{:10.3f}".format(min(importantData[1]))
            maxVal = "{:10.3f}".format(max(importantData[1]))
    else:
        beginVal = 'No data'
        endVal = 'No data'
        average = 'No data'
        beginDate = 'No data'
        endDate = 'No data'
        minVal = 'No data'
        maxVal = 'No data'
    
    prepareWholePeriodFigure(importantData[1], importantData[0]) 
    prepareLastFiveDaysFigures(lastFiveValues, lastFiveDates)
    prepareLastMonthsFigures(monthsMeans, monthsNames, valuesList)
    preparePriceTable(valuesList, datesList, data.beginDate)
    prepareGeneralJsonFile(name, code, beginDate, endDate, beginVal, endVal, average, minVal, maxVal)

# ===================== End of data preparation for currency case =========================
 
# ===================== Figures and table preparation ===================== 

#This method create and save the figure of the whole entered period.
def prepareWholePeriodFigure(importantValues, importantDates):
    plt.figure(figsize=(6,5))
    if len(importantDates) > 15:
        plt.plot(importantDates, importantValues, color='gold', linestyle='-')
        plt.xticks([0, len(importantDates)], [importantDates[0], importantDates[-1]])
    else:
        plt.plot(importantDates, importantValues, color='gold', marker='o', linestyle='-')
        plt.xticks(importantDates, fontsize=6, rotation=45)
    if len(importantDates) == 0:
        plt.title('No data')
    plt.savefig('img\\wholePeriod.png')
    plt.clf()

#This method creater and save the figure of the currency rates for last week. 
def prepareLastFiveDaysFigures(lastFiveValues, lastFiveDates):
    plt.figure(figsize=(6,5))
    plt.plot(lastFiveDates, lastFiveValues, color='gold', marker='o', linestyle='-')
    plt.xticks(lastFiveDates, fontsize=6, rotation=45)
    plt.savefig('img\\lastFive.png')
    plt.clf()
    fig,ax = plt.subplots(figsize=(6,5))
    ax.plot(range(0, len(lastFiveDates)), lastFiveValues, color='gold', marker='o', linestyle='-')
    mean = [np.mean(lastFiveValues)]*len(lastFiveDates)
    ax.plot(lastFiveDates, mean, label='Mean = '+"{:10.3f}".format(np.mean(lastFiveValues))+' zl', color='red', linestyle='-')
    plt.xticks(lastFiveDates, fontsize=6, rotation=45)
    ax.legend(loc='upper right')
    plt.savefig('img\\lastFiveMean.png')
    plt.clf()
 
#This method creates and save the figure of the mean value of the currency rates for each month. 
def prepareLastMonthsFigures(monthsMeans, monthsNames, valuesList):
    plt.figure(figsize=(6,7))
    if len(monthsNames) <= 12:
        plt.plot(monthsNames, monthsMeans, color='gold', marker='o', linestyle='-')
    else:
        plt.plot(monthsNames, monthsMeans, color='gold', linestyle='-')
    plt.xticks(monthsNames, fontsize=6, rotation=60)
    if len(monthsNames) > 12:    
        plt.xticks([0, len(monthsNames)], [monthsNames[0], monthsNames[-1]])
    plt.savefig('img\\lastMonths.png')
    plt.clf()
    
    fig,ax = plt.subplots(figsize=(6,7))
    if len(monthsNames) <= 12:
        ax.plot(range(0, len(monthsMeans)), monthsMeans, color='gold', marker='o', linestyle='-')
    else:
        ax.plot(range(0, len(monthsMeans)), monthsMeans, color='gold', linestyle='-')
    mean = [np.mean(valuesList)]*len(monthsNames)
    ax.plot(monthsNames, mean, label='Mean = '+"{:10.3f}".format(np.mean(valuesList))+' zl', color='red', linestyle='-')
    plt.xticks(monthsNames, fontsize=6, rotation=60)
    if len(monthsNames) > 12:
        plt.xticks([0, len(monthsNames)], [monthsNames[0], monthsNames[-1]])
    ax.legend(loc='upper right')
    plt.savefig('img\\lastMonthsMean.png')
    plt.clf()

#This method creates and save the table of the all currency rates. 
def preparePriceTable(valuesList, datesList, beginDate):
    importantData = getImportantData(valuesList, datesList, beginDate)
         
    data = {'Date':importantData[0], 'Price':importantData[1]}
    currencyTable = pd.DataFrame(data)
    name = 'setup\\priceTable.csv'
    currencyTable.to_csv(name,sep=';',index=False)

# ===================== End of figures and table preparation =========================

# ===================== Preparation of json files and report =========================

#This method prepares json file for tables. 
def prepareTableJsonFile(fileName, formFileName, name, code):
    personalData = {}
    temp = pd.read_csv('setup\\'+fileName+'.csv', sep=';')
    temp = temp.to_html()
    personalData['table'] = temp
    if fileName == 'priceTable':
        if name == 'gold':
            personalData['name'] = name
            personalData['code'] = 'No data'
        else:
            personalData['name'] = name
            personalData['code'] = code
    with open('setup\\generalData.json','w') as f:
        json.dump(personalData,f,indent=4)
        
    prepareReport('forms',formFileName,personalData,fileName)

#This method prepares json file for report and figures. 
def prepareGeneralJsonFile(name, code, beginDate, endDate, beginVal, endVal, average, minVal, maxVal):
    personalData = {}
    prepareTableJsonFile('priceTable', 'firstForm.html', name, code)
    if name == 'gold':
        personalData['name'] = name
        personalData['code'] = 'No data'
    else:
        personalData['name'] = name
        personalData['code'] = code
    personalData['begin'] =  beginDate
    if minVal == 'No data':
        personalData['minVal'] = minVal
    else:
        personalData['minVal'] = minVal + ' zł'
    if maxVal == 'No data':
        personalData['maxVal'] = maxVal
    else:
        personalData['maxVal'] = maxVal + ' zł'
    if beginVal == 'No data':
        personalData['beginVal'] = beginVal
    else:
        personalData['beginVal'] = beginVal + ' zł'
    personalData['end'] = endDate
    if endVal == 'No data':
        personalData['endVal'] = beginVal
    else:
        personalData['endVal'] = endVal + ' zł'
    if average == 'No data':
        personalData['average'] = average
    else:
        personalData['average'] = average + ' zł'
    personalData['fig'] = '..\\img\\wholePeriod.png'
    personalData['fig1'] = '..\\img\\lastFive.png'
    personalData['fig2'] = '..\\img\\lastMonths.png'
    with open('setup\\generalData.json','w') as f:
        json.dump(personalData,f,indent=4)
        
    prepareReport('forms','secondForm.html',personalData,'report')

#This method creates final report.  
def prepareReport(addTempFol,name,data,out):
    addTempFol = Path(addTempFol).resolve()
    loader = jinja2.FileSystemLoader(addTempFol.as_posix())
    env = jinja2.Environment(loader=loader)
    template = env.get_template(name)
    htmlDoc = template.render(general=data)
    addRep = addTempFol.joinpath(f'{out}.html')
    with open(addRep,'w') as f:
        f.write(htmlDoc)  
    print(f'Report saved to: {addRep.as_posix()}\n') 

# ======================= End of json files and report preparation =========================
    
def main(args):
    if not args.listOfCurrencies:
        if args.argument == 'all':
            prepareTableOfAllCurrencies()
        else:
            prepareDataForReport(args)

if __name__ == '__main__':

    args = parserFunction()
    main(args)
