# For operating system interactions
import os

# For number storage and manipulation
import pandas as pd

# For time operations
import time

# Database access
import Database_Writer.database

# For web interactions
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from Scraper.scraper_utils import ScraperUtilities

# URL for website. Final URL will look like: https://roic.ai/financials/AAPL
url = "https://roic.ai/company/"


''' -- Chromedriver creation -- '''
# Step back one folder
os.chdir("..")
# Gets the current directory where the chromedriver is stored
cwd = os.getcwd()
chrome_driver = "D:\\ChromeDriver\\chromedriver.exe"


''' -- Chromedriver options -- '''
options = webdriver.ChromeOptions()
options.add_argument('--disable-gpu')
#options.add_argument('--headless')

class ROIC_Scraper:
    def __init__(self, ticker: str, verbose: bool = True):
        # Store ticker
        self.ticker = ticker.upper()

        # If  the output should be verbose
        self.verbose = verbose

        # Track the number of years on each page. This is so we do not have to fetch the years every field.
        self.summary_page_col_labels = []
        self.financial_page_col_labels = []

        # Track the page data
        fields = {"Company Name":[''],
                  "Ticker": [''],
                  "Information": ['']}


        self.info = pd.DataFrame(fields)
        self.summary_page_data = []
        self.income_statement_data = []
        self.balance_sheet_data = []
        self.cash_flow_data = []

        # Track the row labels on each page.
        self.summary_page_row_labels = []
        self.income_statement_row_labels = []
        self.balance_sheet_row_labels = []
        self.cash_flow_row_labels = []

        # Create database object
        #self.db = db_writer




        # Keeps track of URLs within ROIC.ai
        self.summary_page_url = "https://roic.ai/company/" + self.ticker
        self.financial_page_url = "https://roic.ai/financials/" + self.ticker
        self.browser = None



    '-------------------------------------------------------'

    ################################################################################################################
    ################################################################################################################
    #                                                   Column Labels
    '-------------------------------------------------------'
    def set_summary_page_col_labels(self):
        # If the list is empty. If there is already data, we do not want to append to it.
        if not self.summary_page_col_labels:
            # Loop control
            running = True
            i = 1
            while running:
                try:
                    xpath = f"/html/body/div/div/main/div[3]/div/div[1]/div/div[2]/div[2]/div[{i}]"
                    col_label = self.read_data(xpath)
                    self.summary_page_col_labels.append(col_label)
                    i += 1
                except NoSuchElementException:
                    running = False
            if "- -" in self.summary_page_col_labels:
                bad_col_count = 0
                real_num = 0
                for i in self.summary_page_col_labels:
                    if i == "- -":
                        bad_col_count += 1
                    else:
                        real_num = i
                        break
                final_num = int(real_num) - bad_col_count
                for j in range(len(self.summary_page_col_labels)):
                    if j == 0:
                        self.summary_page_col_labels[j] = final_num
                    else:
                        final_num += 1
                        self.summary_page_col_labels[j] = final_num



    '-------------------------------------------------------'
    def set_financial_page_col_labels(self):
        # If the list is empty. If there is already data, we do not want to append to it.
        if not self.financial_page_col_labels:
            # Loop control
            running = True
            i = 1
            while running:
                try:
                    xpath = f"/html/body/div/div/main/div[3]/div/div/div/div[3]/div/div[2]/div[{i}]"
                    col_label = self.read_data(xpath)
                    self.financial_page_col_labels.append(col_label)
                    i += 1
                except NoSuchElementException:
                    running = False
            if "- -" in self.financial_page_col_labels:
                bad_col_count = 0
                real_num = 0
                for i in self.financial_page_col_labels:
                    print(f"I: {i}")
                    if i == "- -":
                        bad_col_count += 1
                    else:
                        real_num = i
                        break
                final_num = int(real_num) - bad_col_count
                for j in range(len(self.financial_page_col_labels)):
                    if j == 0:
                        self.financial_page_col_labels[j] = final_num
                    else:
                        final_num += 1
                        self.financial_page_col_labels[j] = final_num

    '-------------------------------------------------------'
    def get_summary_page_col_labels(self) -> list:
        if not self.summary_page_col_labels:
            self.set_summary_page_col_labels()
        return self.summary_page_col_labels
    '-------------------------------------------------------'
    def get_financial_page_col_labels(self) -> list:
        if not self.financial_page_col_labels:
            self.set_financial_page_col_labels()
        return self.financial_page_col_labels
    '-------------------------------------------------------'
    ################################################################################################################
    ################################################################################################################
    #                                                   Page Scrapers
    '-------------------------------------------------------'
    def set_info(self):

        _company_name_xpath = "/html/body/div/div/main/div[2]/div[1]/div[2]/div[2]/h1"
        _company_ticker_xpath = "/html/body/div/div/main/div[2]/div[1]/div[2]/div[2]/span/span[1]"
        _company_information_xpath = "/html/body/div/div/main/div[2]/div[1]/div[1]/span"

        _company_name = self.read_data(_company_name_xpath)
        _company_ticker = self.read_data(_company_ticker_xpath)
        _company_information = self.read_data(_company_information_xpath)


        self.info['Company Name'] = _company_name
        self.info['Ticker'] = _company_ticker
        self.info['Information'] = _company_information

    '-------------------------------------------------------'
    def get_info(self):
        return self.info
    '-------------------------------------------------------'
    def set_summary_page_data(self):
        '''
        - Gets all of the data from the summary page and stores it in a list.
        :param create_df: If True, the data collected will automatically be turned into a dataframe.
                          If False, then the normal 2-d list will be returned.
        :return: list or pd.Dataframe
        '''
        table = "summary"


        # Keeps track of the index for the row.
        row_index = 3
        element_index = 3
        # List to hold data
        data_storage = []
        print("--------------------------------------------------------\n\n")
        for x in range(25):
            try:
                i = 1
                data = []
                running = True
                # Get the row label
                row_xpath = f"/html/body/div/div/main/div[3]/div/div[1]/div/div[{row_index}]/div[1]/span"
                row = self.read_data(row_xpath)
                if self.verbose:
                    print(f"[Collected] -    {row}")
                # If the element is not found, None will be returned. In this case we want to break the loop.
                if row == None:
                    break

                while running:
                    try:
                        # Get the data from the xpath
                        xpath = f"/html/body/div/div/main/div[3]/div/div[1]/div/div[{element_index}]/div[2]/div[{i}]"
                        d = self.read_data(xpath)
                        data.append(d)
                        i += 1
                    except NoSuchElementException:
                        running = False
                self.summary_page_row_labels.append(row)
                row_index += 1
                element_index += 1
                data_storage.append(data)
            except NoSuchElementException:
                break

        self.summary_page_data = data_storage


    '-------------------------------------------------------'
    def get_summary_page_data(self) -> list:
        '''
        - Gets the data collected from the summary page.
        :return: list
        '''
        return self.summary_page_data

    '-------------------------------------------------------'
    def set_income_statement_data(self):
        '''
        - Gets all of the data from the income statement and stores it in a list.
        :param create_df: If True, the data collected will automatically be turned into a dataframe.
                          If False, then the normal 2-d list will be returned.
        :return: list or pd.Dataframe
        '''
        table = "income_statement"



        main_run = True
        # Keeps track of the index for the row.
        row_index = 2
        element_index = 2
        # List to hold data
        data_storage = []
        print("--------------------------------------------------------\n\n")
        while main_run:
            i = 1
            data = []
            running = True
            # Get the row label
            row_xpath = f"/html/body/div/div/main/div[3]/div/div/div/div[4]/div[{row_index}]/div[1]/span"
            row = self.read_data(row_xpath)
            if row == "SEC Link":
                main_run = False
                break
            else:
                if self.verbose:
                    print(f"[Collected] -    {row}")
                while running:
                    try:
                        # Get the data from the xpath
                        xpath = f"/html/body/div/div/main/div[3]/div/div/div/div[4]/div[{element_index}]/div[3]/div[{i}]"
                        d = self.read_data(xpath)
                        data.append(d)
                        i += 1
                    except NoSuchElementException:
                        running = False
                self.income_statement_row_labels.append(row)
                row_index += 1
                element_index += 1
                data_storage.append(data)
        self.income_statement_data = data_storage
        """else:
            print(f"\n[Table Found]  - '{table}' was detected '{self.db.db_filename}'. Fetching data from database.\n")
            self.income_statement_data = self.db.get_data_from_table("income_statement")"""

    '-------------------------------------------------------'
    def get_income_statement_data(self) -> list:
        '''
        - Returns the data collected from the income statement.
        :return: list
        '''
        return self.income_statement_data
    '-------------------------------------------------------'
    def set_balance_sheet_data(self):
        '''
        - Gets all of the data from the balance sheet and stores it in a list.
        :param create_df: If True, the data collected will automatically be turned i8nto a dataframe
                          If False, then the normal 2-d list will be returned.
        :return: list or pd.Dataframe
        '''
        table = "balance_sheet"
        """if not self.exists_balance_sheet:
            # Check if we are at the page within the website that we should be at.
            if self.browser.current_url != self.financial_page_url:
                self.goto_page_name("financial_page",self.ticker)"""

        main_run = True
        # Keeps track of the index for the row.
        row_index = 32
        element_index = 32
        # List to hold data
        data_storage = []
        print("--------------------------------------------------------\n\n")
        while main_run:
            i = 1
            data = []
            running = True
            # Get the row label
            row_xpath = f"/html/body/div/div/main/div[3]/div/div/div/div[4]/div[{row_index}]/div[1]/span"
            row = self.read_data(row_xpath)
            if row == "SEC Link":
                main_run = False
            else:
                if self.verbose:
                    print(f"[Collected] -    {row}")
                while running:
                    try:
                        # Get the data from the xpath
                        xpath = f"/html/body/div/div/main/div[3]/div/div/div/div[4]/div[{element_index}]/div[3]/div[{i}]"
                        d = self.read_data(xpath)
                        data.append(d)
                        i += 1
                    except NoSuchElementException:
                        running = False
                self.balance_sheet_row_labels.append(row)
                row_index += 1
                element_index += 1
                data_storage.append(data)

        self.balance_sheet_data = data_storage


    '-------------------------------------------------------'
    def get_balance_sheet_data(self) -> list:
        '''
        - Returns the data collected from the balance sheet.
        :return: list
        '''
        return self.balance_sheet_data

    '-------------------------------------------------------'
    def set_cash_flow_data(self):
        table = "cash_flow"

        main_run = True
        # Keeps track of the index for the row.
        row_index = 74
        element_index = 74
        # List to hold data
        data_storage = []
        print("--------------------------------------------------------\n\n")
        while main_run:
            i = 1
            data = []
            running = True
            # Get the row label
            row_xpath = f"/html/body/div/div/main/div[3]/div/div/div/div[4]/div[{row_index}]/div[1]/span"
            row = self.read_data(row_xpath)
            if row == "SEC Link":
                main_run = False
            else:
                if self.verbose:
                    print(f"[Collected] -    {row}")
                while running:
                    try:
                        # Get the data from the xpath
                        xpath = f"/html/body/div/div/main/div[3]/div/div/div/div[4]/div[{element_index}]/div[3]/div[{i}]"
                        d = self.read_data(xpath)
                        data.append(d)
                        i += 1
                    except NoSuchElementException:
                        running = False
                self.cash_flow_row_labels.append(row)
                row_index += 1
                element_index += 1
                data_storage.append(data)

        self.cash_flow_data = data_storage


        """else:
            print(f"\n[Table Found]  - '{table}' was detected '{self.db.db_filename}'. Fetching data from database.\n")
            self.cash_flow_data = self.db.get_data_from_table("cash_flow")"""

    '-------------------------------------------------------'
    def get_cash_flow_data(self) -> list:
        '''
        - Gets the cash flow data.
        :return: list
        '''
        return self.cash_flow_data
    '-------------------------------------------------------'
    ################################################################################################################
    ################################################################################################################
    #                                                   Dataframe Creation
    '-------------------------------------------------------'
    def create_summary_page_df(self,_data) -> pd.DataFrame:


        print("\n[Summary] Data gathered from scraper.\n")
        # Create a dictionary for us to insert into a dataframe.
        d = {}

        for i in range(len(_data)):
            d[self.summary_page_row_labels[i]] = _data[i]

        # Get the column labels
        col_labels = self.get_summary_page_col_labels()

        # Dataframe creation
        df = pd.DataFrame(d)
        df = df.transpose()

        # Insert the column labels
        df.columns = col_labels
        return df
    """else:
        print("\n[Summary] Data gathered from database.\n")
        return self.db.get_data_from_table("summary")"""

    '-------------------------------------------------------'
    def create_income_statement_df(self,_data) -> pd.DataFrame:

        # Create a dictionary for us to insert into a dataframe
        d = {}
        for i in range(len(_data)):
            d[self.income_statement_row_labels[i]] = _data[i]

        # Get the column label
        col_labels = self.get_financial_page_col_labels()

        # Dataframe creation
        df = pd.DataFrame(d)
        df = df.transpose()

        # Insert the column labels
        df.columns = col_labels
        return df
    """else:
        print("\n[Income Statement] Data gathered from database.\n")
        return self.db.get_data_from_table("income_statement")"""


    '-------------------------------------------------------'
    def create_balance_sheet_df(self,_data) -> pd.DataFrame:

        print("\n[Balance Sheet] Data gathered from scraper.\n")
        # Create a dictionary for us to insert into a dataframe
        d = {}
        for i in range(len(_data)):
            d[self.balance_sheet_row_labels[i]] = _data[i]

        # Get the columns label
        col_labels = self.get_financial_page_col_labels()

        # Dataframe creation
        df = pd.DataFrame(d)
        df = df.transpose()

        # Insert the column labels
        df.columns = col_labels
        return df
    """else:
        print(f"\n[Balance Sheet] Data gathered from database.\n")
        return self.db.get_data_from_table("balance_sheet")"""

    '-------------------------------------------------------'
    def create_cash_flow_df(self,_data) -> pd.DataFrame:

        print("\n[Cash Flow] Data gathered from scraper.\n")
        # Create a dictionary for us to insert into a dataframe
        d = {}
        for i in range(len(_data)):
            d[self.cash_flow_row_labels[i]] = _data[i]

        # Get the columns label
        col_labels = self.get_financial_page_col_labels()

        # Dataframe creation
        df = pd.DataFrame(d)
        df = df.transpose()

        # Insert the column labels
        df.columns = col_labels
        return df
    """else:
        print("\n[Cash Flow] Data gathered from database.\n")
        return self.db.get_data_from_table("cash_flow")"""

    #################### Utilities ####################
    '''-----------------------------------'''
    def click_button(self, xpath: str):
        '''
        :param browser: Browser object of the scraper.
        :param xpath: Xpath to object that will be clicked.
        :return: None
        '''
        try:
            # Clicks button at xpath.
            self.browser.find_element_by_xpath(xpath).click()
        except Exception:
            print(f'-- Element could not be found.')

    '''-----------------------------------'''
    def submit_data(self, xpath: str, data):
        '''
        :param xpath: Xpath to object that data will be submitted to.
        :param data: Data to enter in the field.
        :return: None
        '''
        #try:
        # Sends data to field.
        self.browser.find_element("xpath",xpath).send_keys(data)
        #except NoSuchElementException:
          #  print(f' -- Element could not be found.')

    '''-----------------------------------'''
    def read_data(self, xpath:str):
        '''
        :param browser: Selenium browser object.
        :return: None
        '''
        data = self.browser.find_element("xpath",xpath).text
        return data
    '''-----------------------------------'''
    def goto_page(self,url: str):
        '''
        - Will take the browser to a page according to the URL.
        :param url:
        :return: None
        '''
        self.browser.get(url)
    '''-----------------------------------'''
    def create_browser(self, url, ticker=None):
        '''
        :param url: The website to visit.
        :return: None
        '''
        self.browser = webdriver.Chrome(executable_path=chrome_driver,chrome_options=options)
        if ticker == None:
            self.browser.get(url)
        else:
            url += ticker
            self.browser.get(url)

    '''-----------------------------------'''
    def goto_page_name(self,page_name,ticker):
        '''
        - Will go to the summary page within ROIC.ai.
        :param page_name: Name of the page to navigate to.
        :param ticker: Company to navigate to.
        :return: None
        '''
        dict = {"summary_page": f"https://roic.ai/company/{ticker}",
                "financial_page": f"https://roic.ai/financials/{ticker}"}
        self.create_browser(dict[page_name])

    '''-----------------------------------'''
    def format_col_labels(self, cols) -> list:
        '''
        - Will keep cut the list at "TTM". Example: [0,1,2,TTM,3,4,5,6] -> [0,1,2,TTM]
        :param cols: The list of columns.
        :return: list
        '''
        l = []
        for c in cols:
            l.append(c)
            if c == "TTM":
                break
        return l



