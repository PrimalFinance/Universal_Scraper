import requests
from bs4 import BeautifulSoup
import lxml.etree as et

import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

chrome_driver_path = "D:\\VisualStudioCode\\CHROME_DRIVER\\chromedriver.exe"


countries = {
    "Australia": "AU",
    "Austria": "AT",
    "Belgium": "BE",
    "Canada": "CA",
    "Denmark": "DK",
    "Finland": "FI",
    "France": "FR",
    "Germany": "DE",
    "Iceland": "IS",
    "Ireland": "IE",
    "Italy": "IT",
    "Japan": "JP",
    "Luxembourg": "LU",
    "Netherlands": "NL",
    "New Zealand": "NZ",
    "Norway": "NO",
    "Portugal": "PT",
    "Spain": "ES",
    "Sweden": "SE",
    "Switzerland": "CH",
    "United Kingdom": "GB",
    "United States": "USA"
}

options = webdriver.ChromeOptions()
options.add_argument("--disable-gpu")


class FinvizScraper:
    def __init__(self, ticker: str) -> None:

        self.ticker = ticker.upper()
        self.data_source = "finviz"

        # Define the URL of the website we want to scrape
        self.url = f"https://finviz.com/quote.ashx?t={ticker}&p=d"

        # Find the table that contains the information we want
        self.table_class = "fullview-title"

        self.browser = None

        self.table = None
        self.parsed_data = {}

        # data = self._read_data(method="xpath", data=table_xpath)
        # print(f"Data: {data}")

        # Find the rows of the table

    '''----------------------------------- Company Attributes -----------------------------------'''

    def set_data_finviz(self):
        if self.table == None:
            print("TABLE TAB")
            # Create a browser.
            self._create_browser()
            # Get the table from the website.
            self.table = self._read_data(method="class", data=self.table_class)

            print(f"Ticker: {self.ticker}")

            # Table extracted
            # AAPL [NASD]
            # Apple Inc.
            # Technology | Consumer Electronics | USA

            print(f"Table: {self.table}")

            print(f"Table2: {self.table.split('|')}")
            try:


                ticker, company_name, sector, industry, country = self.table.split("|")

                # Format the sector. Ex: [NYSE]\bIndustrials -> Industrials
                sector = sector.split("\n")[-1]

                print(f"Sector: {sector}")


                '''# First section: 'AAPL [NASD]\nApple Inc.\nTechnology '
                # Second section: ' Consumer Electronics '
                # Third section:  ' USA'
                first_section, second_section, third_section = self.table.split(
                    "|")

                # Clean data in first section.
                _, company_name, sector = first_section.split("\n")'''

                # If the first character is blank.
                if sector[0] == " ":
                    sector = sector[1:]
                if sector[-1] == " ":
                    sector = sector[:-1]
                if sector == "Technology":
                    sector = "Information Technology"

                self.parsed_data["Ticker"] = self.ticker
                self.parsed_data["Name"] = company_name
                self.parsed_data["Sector"] = sector

                # Format the industry data. 
                if industry[0] == " ":
                    industry = industry[1:]
                if industry[-1] == " ":
                    industry = industry[:-1]

                self.parsed_data["Industry"] = industry

                # Format the country data.
                if country[0] == " ":
                    country = country[1:]
                if country[-1] == " ":
                    country = country[:-1]

                
                print(f"""
                Industry: {industry}
                Country: {country}""")

                self.parsed_data["Country"] = country
            except AttributeError:

                print(
                    f'- [Error] Unable to retrieve data for {self.ticker}. Now trying Yahoo Finance')
                self.set_data_yahoo()

    def set_data_yahoo(self):

        url = f"https://finance.yahoo.com/quote/{self.ticker}/profile?p={self.ticker}"

        self._create_browser(url)

        company_name_xpath = "/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[1]/section/div[1]/div/h3"
        table_xpath = "/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[1]/div/div/section/div[1]/div/div/p[2]"
        country_xpath = "/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[1]/section/div[1]/div/div/p[1]/text()[4]"

        company_name = self._read_data(
            method="xpath", data=company_name_xpath)
        data = self._read_data(method="xpath", data=table_xpath)

        try:
            country = self._read_data(method="xpath", data=country_xpath)

            country = countries[country]
        except KeyError:
            country = "N\A"

        data = data.split(
            "\n")
        sector = data[0].split(":")[1]
        industry = data[1].split(":")[1]
        print(f'Data: {data}')
        # Remove any extra spaces. While a method like .replace() would be simpler.
        # We use this splicing method as we do not want to potentially remove spaces in the middle of the word.
        if sector[0] == " ":
            sector = sector[1:]
        elif sector[-1] == " ":
            sector = sector[:-1]
        if industry[0] == " ":
            industry = industry[1:]
        elif industry[-1] == " ":
            industry = industry[:-1]

        if sector == "Technology":
            sector = "Information Technology"

        self.parsed_data["Ticker"] = self.ticker
        self.parsed_data["Company Name"] = company_name
        self.parsed_data["Sector"] = sector
        self.parsed_data["Industry"] = industry
        self.parsed_data["Country"] = country

    def get_data(self):
        if self.parsed_data == {}:
            self.set_data_finviz()
        return self.parsed_data

    '''-----------------------------------'''

    def get_company_ticker(self):
        try:
            if self.parsed_data == {}:
                self.set_data_finviz()
            return self.parsed_data["Ticker"]
        # This error typically happens if the company cannot be found on Finviz.
        except KeyError:
            print(
                f"- [Error] Unable to get {self.ticker} ticker from {self.data_source}")
    '''-----------------------------------'''

    def get_company_name(self) -> str:
        try:
            if self.parsed_data == {}:
                self.set_data_finviz()
            return self.parsed_data["Name"]
        # This error typically happens if the company cannot be found on Finviz.
        except KeyError:
            print(
                f"- [Error] Unable to get {self.ticker} name from {self.data_source}")
    '''-----------------------------------'''

    def get_company_country(self) -> str:
        try:
            if self.parsed_data == {}:
                self.set_data_finviz()
            return self.parsed_data["Country"]
        # This error typically happens if the company cannot be found on Finviz.
        except KeyError:
            print(
                f"- [Error] Unable to get {self.ticker} country from {self.data_source}")
    '''-----------------------------------'''

    def get_company_sector(self):
        try:
            if self.parsed_data == {}:
                self.set_data_finviz()
            return self.parsed_data["Sector"]
        # This error typically happens if the company cannot be found on Finviz.
        except KeyError:
            print(
                f"- [Error] Unable to get {self.ticker} sector from {self.data_source}")

    '''-----------------------------------'''

    def get_company_industry(self):
        try:
            if self.parsed_data == {}:
                self.set_data_finviz()
            return self.parsed_data["Industry"]
    # This error typically happens if the company cannot be found on Finviz.
        except KeyError:
            print(f"- [Error] Unable to get {self.ticker} industry")
    '''-----------------------------------'''

    '''-----------------------------------'''

    def _read_data(self, method: str, data: str):
        '''
        :param browser: Selenium browser object.
        :return: None
        '''

        if method == "xpath" or method == "XPATH":
            try:
                data = self.browser.find_element(By.XPATH, data).text
                return data
            # This usually arises, if we are trying to read data without first creating a browser. To fix this, the except argument will execute the "_create_browser()" function, then the read data function will be re-run.
            except AttributeError:
                self._create_browser()
                self._read_data(data=data)
            except NoSuchElementException:
                print(f"- [Error] Unable to locate xpath. ")

        elif method == "class" or method == "CLASS":
            try:
                data = self.browser.find_element(By.CLASS_NAME, data).text
                return data
            # This usually arises, if we are trying to read data without first creating a browser. To fix this, the except argument will execute the "_create_browser()" function, then the read data function will be re-run.
            except AttributeError:
                self._create_browser()
                self._read_data(data=data)
            except NoSuchElementException:
                print(f"- [Error] Unable to locate class. ")

    '''-----------------------------------'''

    def _create_browser(self, url=None):
        self.browser = webdriver.Chrome(
            executable_path=chrome_driver_path, chrome_options=options)
        if url == None:
            self.browser.get(self.url)
        else:
            self.browser.get(url)

    '''-----------------------------------'''
