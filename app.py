import os
import pandas as pd
import tkinter as tk

from Scraper.scraper import FinvizScraper
from Scraper.roic_scraper import ROIC_Scraper
from Excel.excel import UniversalDashboard, CompanyModels
from Company_Information.company_info import CompanyInfo

from Database_Writer.database import AssetDatabase
from Excel_Writer.excel_writer import ExcelWriter

# Error handling 
from pandas.errors import DatabaseError



# Paths to files
paths = {"Company Models": "C:\\Users\\William\\OneDrive\\Company Models CloudSave\\"}

# Fonts
fonts = {"Home": ("Ariel", 25),
         "Input": ("Ariel", 45)}


# Colors
colors = {"ETH Purple": "#6C4F99"}


# Formats for excel sheets
main_dict = {"": [
    "Ticker", "Price", "Shares", "MC", "Cash", "Debt", "EV"]}
info_dict = {"": ["Company Name", "Ticker",
                  "Country", "Sector", "Industry"]}
model_dict = {"": ["Quarter", "Filing Date", "Period of Report"]}

main_df = pd.DataFrame(main_dict)
info_df = pd.DataFrame(info_dict)
model_df = pd.DataFrame(model_dict)


class App:
    def __init__(self, master):
        self.label_x = 0.5
        self.label_y = 0.2
        self.entry_x = 0.5
        self.entry_y = 0.2
        self.button_width = 20
        self.button_height = 5

        self.master = master
        self.master.geometry("1280x720")
        self.master.title("Universal Dashboard")
        # Color of homescreen
        self.master.config(bg=colors["ETH Purple"])

        self.ignore_list = ["RYCEY"]
        self.home_screen()

    '''-----------------------------------------------------------------------------------------  Home Screen'''

    def home_screen(self) -> None:
        # Delete any previous widgets.
        self.clear_screen()

        excel_button_x = 0.3
        excel_button_y = 0.4
        roic_button_x = 0.7
        roic_button_y = 0.4

        # Add a label with the text "Universal Dashboard"
        universal_dashboard_label = tk.Label(
            self.master, text="Universal Dashboard", font=fonts["Home"], bg=colors["ETH Purple"], fg="white")
        universal_dashboard_label.place(
            relx=self.label_x, rely=self.label_y, anchor=tk.CENTER)

        excel_page_button = tk.Button(
            self.master, text="Excel Functions", width=self.button_width, height=self.button_height, command=self.excel_page_screen)
        excel_page_button.place(
            relx=excel_button_x, rely=excel_button_y, anchor=tk.CENTER)
        
        roic_scraper_button = tk.Button(
            self.master, text="ROIC Scraper", width=self.button_width, height=self.button_height, command=self.ROIC_screen)
        roic_scraper_button.place(relx=roic_button_x, rely=roic_button_y, anchor=tk.CENTER)

    '''-----------------------------------------------------------------------------------------  Excel Pages'''
    '''-------------------------------'''
    def excel_page_screen(self) -> None:
        button_x = 0.3
        button_y = 0.4

        # Clear the screen of widgets from the previous screen
        self.clear_screen()

        # Place home button
        self.place_home_button()

        # Add a label with the text "Universal Dashboard"
        excel_title_label = tk.Label(
            self.master, text="Universal Dashboard", font=fonts["Home"], bg=colors["ETH Purple"], fg="white")
        prepare_files_button = tk.Button(
            self.master, text="Prepare Files", width=self.button_width, height=self.button_height, command=self.prepare_excel_files)
        insert_company_info = tk.Button(
            self.master, text="Insert Copany Info", width=self.button_width, height=self.button_height, command=self.insert_company_info_into_files)

        excel_title_label.place(
            relx=self.label_x, rely=self.label_y, anchor=tk.CENTER)
        prepare_files_button.place(
            relx=button_x, rely=button_y, anchor=tk.CENTER)
        insert_company_info.place(
            relx=button_x + 0.15, rely=button_y, anchor=tk.CENTER)

    '''------------------------------------------ Excel Utilities ------------------------------------------'''
    '''-------------------------------'''
    def prepare_excel_files(self):
            tickers = self.get_tickers_in_directory()
            for ticker in tickers:
                if ticker == "":
                    pass
                elif ticker == "~ar4BE":
                    pass
                elif ticker in self.ignore_list:
                    pass
                else:
                    try:
                        excel = CompanyModels(ticker)

                        # Create sheets.
                        excel.create_sheet_if_not_exist("Main")
                        excel.create_sheet_if_not_exist("Info")
                        excel.create_sheet_if_not_exist("Model")

                        # Move sheets to their correct order.
                        excel.organize_sheets("Main", dest_index=0)
                        excel.organize_sheets("Info", dest_index=1)
                        excel.organize_sheets("Model", dest_index=2)

                        # Write the default formats to the sheets.
                        excel.write_df_to_sheet("Main", main_df)
                        excel.write_df_to_sheet("Info", info_df)

                        # Remove any blank rows at the top of the excel file.
                        excel.remove_empty_rows("Main")
                        excel.remove_empty_rows("Info")
                
                    except AttributeError:
                        print(f"- [Error] Failed to create sheets for: {ticker}")

    '''-------------------------------'''
    def insert_company_info_into_files(self):
        '''
        ===================================
        Page
        ===================================
        '''
        self.clear_screen()
        self.place_home_button()

        company_info_entry = tk.Entry(self.master)

        company_info_entry.place(relx=self.entry_x, rely=self.entry_y)

        '''
        ===================================
        Logic
        ===================================
        '''
        tickers = self.get_tickers_in_directory()
        for ticker in tickers:
            if ticker == "":
                pass
            elif ticker == "~ar4BE":
                pass
            elif ticker in self.ignore_list:
                pass
            else:
                sc = FinvizScraper(ticker)
                excel = CompanyModels(ticker)

                # Hold a dictionary of cells mapped to their functions.
                data_funcs = {
                    "B1": sc.get_company_name,
                    "B2": sc.get_company_ticker,
                    "B3": sc.get_company_country,
                    "B4": sc.get_company_sector,
                    "B5": sc.get_company_industry
                }

                try:
                    for cell, data_func in data_funcs.items():
                        self.insert_if_not_exists(excel=excel, sheet_name="Info",
                                                  cell=cell, data_func=data_func)
                except AttributeError:
                    print(f"[Error] Failed to insert data for {ticker}")
    '''-------------------------------'''
    def insert_if_not_exists(self, excel, sheet_name, cell, data_func):
            item_exists = excel.if_sheet_item_exists(sheet_name, cell)
            if not item_exists:
                data = data_func()
                excel.insert_sheet_item(sheet_name, cell, data)
    '''-------------------------------'''
    def insert_into_universal_dashboard(self, tickers):
        csv = CompanyInfo()
        excel = UniversalDashboard()

        company_sectors = {"Basic Materials": [],
                           "Communication Services": [],
                           "Consumer Cyclical": [],
                           "Consumer Defensive": [],
                           "Energy": [],
                           "Financial": [],
                           "Healthcare": [],
                           "Industrials": [],
                           "Information Technology": [],
                           "Real Estate": [],
                           "Utilities": []}

        # Get the data for each ticker. Organize into a dictionary where the key is the sector.
        for ticker in tickers:
            # print(f"Ticker: {ticker}")
            if ticker == "":
                pass
            else:
                sc = FinvizScraper(ticker)
                # Get data if the company is in the csv file.
                if csv.company_exists(ticker):
                    company_data = csv.get_data(ticker)

                # If the company is not in the csv file, get if from the scraper.
                else:
                    company_data = sc.get_data()
                    csv.insert_data(data=company_data)

                # print(f"Row: {company_data}")
                company_sectors[company_data["Sector"]].append(company_data)

        # Iterate through dictionary. Send list within dictionary to excel fucntion.
        for sector in company_sectors:
            excel.insert_tickers(sector, company_sectors[sector])

    '''-------------------------------'''
    def print_message(self):
        print(f"TAG")

    '''-----------------------------------------------------------------------------------------  Excel Pages'''

    def get_tickers_in_directory(self) -> list:
        dir_list = os.listdir(paths["Company Models"])
        dir_list = [str(x).split(".")[0] for x in dir_list]

        return dir_list
    
    '''-----------------------------------------------------------------------------------------  ROIC Pages'''
    def ROIC_screen(self):
        
        # Button placements
        get_data_button_x = 0.3
        get_data_button_y = 0.4

        # Clear the screen of widgets from the previous screen
        self.clear_screen()

        # Place home button
        self.place_home_button()

        # Add a label with the text "Universal Dashboard"
        excel_title_label = tk.Label(
            self.master, text="Universal Dashboard", font=fonts["Home"], bg=colors["ETH Purple"], fg="white")
        get_data_button = tk.Button(
            self.master, text="Get Data", width=self.button_width, height=self.button_height, command=self.get_roic_data)


        excel_title_label.place(
            relx=self.label_x, rely=self.label_y, anchor=tk.CENTER)
        get_data_button.place(
            relx=get_data_button_x, rely=get_data_button_y, anchor=tk.CENTER)

        
    '''-------------------------------'''
    def get_roic_data(self):
        # Clear the screen of widgets from the previous screen
        self.clear_screen()

        # Place home button
        self.place_home_button()


        # Button placements
        search_stock_button_x = 0.5
        search_stock_button_y = 0.5
        stock_input_button_x = 0.37
        stock_input_button_y = 0.3

        # Button dimesions
        stock_input_width = 10
        stock_input_height = 1


        # input entry
        inValue = tk.StringVar()
        inValueEntry = tk.Entry(self.master,width=stock_input_width, font=fonts["Input"],  textvariable=inValue)
        inValueEntry.place(relx=stock_input_button_x, rely=stock_input_button_y)


        # Add a label with the text "Universal Dashboard"
        excel_title_label = tk.Label(
            self.master, text="Universal Dashboard", font=fonts["Home"], bg=colors["ETH Purple"], fg="white")
        search_stock_button = tk.Button(
            self.master, width=stock_input_width, text="Search" , height=stock_input_height, font=fonts["Home"], command=lambda: self.get_stock_data(inValue.get()))


        excel_title_label.place(
            relx=self.label_x, rely=self.label_y, anchor=tk.CENTER)
        search_stock_button.place(
            relx=search_stock_button_x, rely=search_stock_button_y, anchor=tk.CENTER)
    '''-------------------------------'''
    def get_stock_data(self, ticker: str):

        info = None
        summary = None
        incomeStatement= None
        balanceSheet = None
        cashFlow = None
        
        self.create_folder_for_company(ticker=ticker)

        db = AssetDatabase(ticker=ticker)
        scraper = ROIC_Scraper(ticker=ticker)

        databaseExists = db.check_if_file_exists()

        main_dict = {"":["Price", "Shares", "MC", "Cash", "Debt", "EV"]}




        main_df = pd.DataFrame(main_dict)
        main_df = main_df.set_index("")

        ### If the database exists
        if databaseExists:
            # Get the data from the database.
            try:
                info = db.get_data_from_table("info")
                summary = db.get_data_from_table("summary")
                incomeStatement = db.get_data_from_table("income_statement")
                balanceSheet = db.get_data_from_table("balance_sheet")
                cashFlow = db.get_data_from_table("cash_flow")
            # This usually occurs if a file has been created but data has not been entred.
            except DatabaseError:
                info, summary, incomeStatement, balanceSheet, cashFlow = self.scrape_content(scraper, db)
        ### If there is no database go straight to scraping.
        elif not databaseExists:
            info, summary, incomeStatement, balanceSheet, cashFlow = self.scrape_content(scraper, db)
            

        ######################################################################################## Database handling end

        ######################################################################################## Excel Writing Start
        # Create excel object
        excel = ExcelWriter(ticker=ticker)

        if excel.check_if_file_exists():
            pass
        elif not excel.check_if_file_exists():
            excel.write_to_file(summary_df=summary, income_statement_df=incomeStatement, balance_sheet_df=balanceSheet,
                                cash_flow_df=cashFlow)


    '''-------------------------------'''
    def scrape_content(self, scraper, db: AssetDatabase):

        summary_url = scraper.summary_page_url
        financial_url = scraper.financial_page_url

        scraper.create_browser(summary_url)

        ''' -- Info -- '''
        scraper.set_info()
        info_df = scraper.get_info()

        ''' -- Summary -- '''
        scraper.set_summary_page_data()
        summary_data = scraper.get_summary_page_data()
        summary_df = scraper.create_summary_page_df(summary_data)
        if '' in summary_df.columns:
            # axis 0 = rows     axis 1 = columns
            summary_df.drop(summary_df.columns[-1], inplace=True, axis=1)
        ''' -- Income Statement -- '''
        scraper.goto_page(financial_url)
        scraper.set_income_statement_data()
        income_statement_data = scraper.get_income_statement_data()
        income_statement_df = scraper.create_income_statement_df(income_statement_data)
        if '' in income_statement_df.columns:
            income_statement_df.drop(income_statement_df.columns[-1], inplace=True, axis=1)
        ''' -- Balance Sheet -- '''
        scraper.set_balance_sheet_data()
        balance_sheet_data = scraper.get_balance_sheet_data()
        balance_sheet_df = scraper.create_balance_sheet_df(balance_sheet_data)
        if '' in balance_sheet_df.columns:
            balance_sheet_df.drop(balance_sheet_df.columns[-1], inplace=True, axis=1)
        ''' -- Cash Flow -- '''
        scraper.set_cash_flow_data()
        cash_flow_data = scraper.get_cash_flow_data()
        cash_flow_df = scraper.create_cash_flow_df(cash_flow_data)
        if '' in cash_flow_df.columns:
            cash_flow_df.drop(cash_flow_df.columns[-1], inplace=True, axis=1)

        # Database inserts
        db.create_table_from_dataframe(info_df, table_type="info")
        db.create_table_from_dataframe(summary_df, table_type="summary")
        db.create_table_from_dataframe(income_statement_df, table_type="income_statement")
        db.create_table_from_dataframe(balance_sheet_df, table_type="balance_sheet")
        db.create_table_from_dataframe(cash_flow_df, table_type="cash_flow")


        return info_df, summary_df, income_statement_df, balance_sheet_df, cash_flow_df
    '''-------------------------------'''


    def get_most_recent_excel_file(ticker: str, oneDrive: bool):
    
        listDir = os.listdir(paths["Company Models"] + f"\\{ticker}")
        mostRecentFile = listDir[-1]
        mostRecentFile = mostRecentFile.split(".")[0]
    
        return mostRecentFile
    
    '''-------------------------------'''
    def increment_extension(ticker_extension: str):
        if "_" in ticker_extension:
            # Split the ticker at the underscore. Ex: AAPL_1 -> ['AAPL
            ticker, extension = ticker_extension.split("_")
            new_extension = int(extension) + 1
            new_ticker_extension = ticker + "_" + str(new_extension)
            return new_ticker_extension
        # If the file does not have any duplicates
        elif "_" not in ticker_extension:
            return ticker_extension + "_1"
    '''-------------------------------'''
    '''-------------------------------'''
    '''------------------------------------------ Other Utilities'''
    def create_folder_for_company(self, ticker: str):

        # If the path does exist
        if self.check_if_path_exists(paths["Company Models"] + ticker.upper()):
            pass
        # If the path does not exist (The company folder has not been created yet)
        elif not self.check_if_path_exists(paths["Company Models"] + ticker.upper()):
            os.chdir(paths["Company Models"])
            os.mkdir(paths["Company Models"] + f"\\{ticker.upper()}")

            # Path to check if the excel file is not in it's folder.
            excel_file_movement = paths["Company Models"] + ticker.upper() + ".xlsx"

            # If the file has not been moved to its folder yet
            if os.path.exists(excel_file_movement):
                # D:\Company Models\{ticker}.xlsx -> D:\Company Models\{ticker}\{ticker}.xlsx
                os.rename(paths["Company Models"] + ticker.upper() + ".xlsx",
                        paths["Company Models"] + ticker.upper() + "\\" + ticker.upper() + ".xlsx")
            # If the file is not outside of its folder then we do not need to do anything.
            else:
                pass
    '''-------------------------------'''
    def check_if_path_exists(self, path: str):
        return os.path.exists(path)
    '''-------------------------------'''
    '''-------------------------------'''
    
    '''-------------------------------'''
    '''-------------------------------'''
    '''-------------------------------'''

    def place_home_button(self):
        # Create the home button
        home_button = tk.Button(self.master, text="Home",
                                command=self.home_screen)
        home_button.place(relx=0, rely=0, anchor=tk.NW)
    
    '''-------------------------------'''
    def clear_screen(self):
        # Destroy all child widgets of the master widget
        for widget in self.master.winfo_children():
            widget.destroy()


root = tk.Tk()
app = App(root)
root.mainloop()
