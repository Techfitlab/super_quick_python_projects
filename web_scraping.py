import pandas as pd
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import requests 
import urllib.request
import time
from io import StringIO
from datetime import datetime, timedelta
pd.options.display.float_format = '{:.0f}'.format

class YahooFinanceCurrent:
    def __init__(self):
        self.link = 'https://finance.yahoo.com/quote/BTC-USD?p=BTC-USD&.tsrc=fin-srch'
    # Show Chrome Page    
        service = Service('/usr/local/bin/chromedriver')
        service.start()
        driver = webdriver.Remote(service.service_url)
        driver.get(self.link)
        time.sleep(5)
        driver.quit()
    
    def getCurrentPrice(self):
        Url_Open = urllib.request.urlopen(self.link)
        soup = BeautifulSoup(Url_Open, 'html.parser')
        Current_Price = {}
        for i in soup.find_all('div', {'class':'D(ib) smartphone_Mb(10px) W(70%) W(100%)--mobp smartphone_Mt(6px)'}):
            price=i.find('span')
            Current_Price['Current_Price'] = price.text.strip()
        return Current_Price

class YahooFinanceHistoric: 
    # Open Driver to see link
    crumb_link = 'https://finance.yahoo.com/quote/{0}/history?p={0}'
    crumb_regex = r'CrumbStore":{"crumb":"(.*?)"}'
    quote_link = 'https://query1.finance.yahoo.com/v7/finance/download/{quote}?period1={dfrom}&period2={dto}&interval=1d&events=history&crumb={crumb}'
    timeout = 2

    def __init__(self, symbol, days_back=1):
        # YahooFinanceCurrent.__init__(self)
        self.symbol = symbol
        self.session = requests.Session()
        self.dt = timedelta(days=days_back)
    
    def getCrumb(self):
        response = self.session.get(self.crumb_link.format(self.symbol), timeout=self.timeout)
        response.raise_for_status()
        match = re.search(self.crumb_regex, response.text)
        if not match:
            raise ValueError('No Valid crumb for Yahoo Finance..')
        else:
            self.crumb = match.group(1)

    def getQuote(self):
        if not hasattr(self, 'crumb') or len(self.session.cookies) == 0:
            self.getCrumb()
        now = datetime.utcnow()
        dateto = int(now.timestamp())
        datefrom = int((now - self.dt).timestamp())
        url = self.quote_link.format(quote=self.symbol, dfrom = datefrom, dto = dateto, crumb = self.crumb)
        response = self.session.get(url)
        response.raise_for_status()
        return pd.read_csv(StringIO(response.text), parse_dates=['Date'])

if __name__ == '__main__':
    ls = YahooFinanceCurrent()
    btc_current = ls.getCurrentPrice()
    data = YahooFinanceHistoric('BTC-USD', days_back=30).getQuote()

