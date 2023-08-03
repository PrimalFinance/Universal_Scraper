import os
import pandas as pd
import time
import yfinance as yf
import yahoo_fin.stock_info as si

from Scraper.scraper import FinvizScraper
from Excel.excel import UniversalDashboard, CompanyModels
from Company_Information.company_info import CompanyInfo


company_model_path = "C:\\Users\\William\\OneDrive\\Company Models CloudSave"

main_dict = {"": [
    "Ticker", "Price", "Shares", "MC", "Cash", "Debt", "EV"]}
info_dict = {"": ["Company Name", "Ticker",
                  "Country", "Sector", "Industry"]}
model_dict = {"": ["Quarter", "Filing Date", "Period of Report"]}

main_df = pd.DataFrame(main_dict)
info_df = pd.DataFrame(info_dict)
model_df = pd.DataFrame(model_dict)


def get_tickers_in_directory():
    dir_list = os.listdir(company_model_path)
    dir_list = [str(x).split(".")[0] for x in dir_list]

    return dir_list


def compare_directory_with_sheet(scraper: UniversalDashboard, ticker_list: list, sheet_contents: dict):
    # Iterate through every ticker in the list.
    print(f"Ticker: {ticker_list}")
    for ticker in ticker_list:
        index = 0
        # Check if the ticker is in the sector.
        if not check_sector_tickers("Basic Materials", ticker, sheet_contents):
            index += 1
        if not check_sector_tickers("Communication Services", ticker, sheet_contents):
            index += 1
        if not check_sector_tickers("Consumer Cyclical", ticker, sheet_contents):
            index += 1
        if not check_sector_tickers("Consumer Defensive", ticker, sheet_contents):
            index += 1
        if not check_sector_tickers("Energy", ticker, sheet_contents):
            index += 1
        if not check_sector_tickers("Financial", ticker, sheet_contents):
            index += 1
        if not check_sector_tickers("Healthcare", ticker, sheet_contents):
            index += 1
        if not check_sector_tickers("Industrials", ticker, sheet_contents):
            index += 1
        if not check_sector_tickers("Information Technology", ticker, sheet_contents):
            index += 1
        if not check_sector_tickers("Real Estate", ticker, sheet_contents):
            index += 1
        if not check_sector_tickers("Utilities", ticker, sheet_contents):
            index += 1

        # If the index is 11, the ticker is not present.
        if index == 11:
            scraper.get_company_sector()
            print(f'Ticker: {ticker}    {index}')


def check_sector_tickers(sector: str, ticker: str, sheet_contents: dict):

    # print(f"{ticker}   {sheet_contents[sector]}")
    if ticker in sheet_contents[sector]:
        return True
    else:
        return False


def prep_excel_files(tickers, update=False):

    if update:
        for ticker in tickers:
            if ticker == "":
                pass
            else:
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
    elif not update:
        pass


def insert_company_info_into_files(ticker):
    csv_writer = CompanyInfo()
    """ for ticker in tickers:
            if ticker == "":
                pass
            else:
        """
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

    print(f"TIcker: {ticker}")
    for cell, data_func in data_funcs.items():
        insert_if_not_exists(excel=excel, sheet_name="Info",
                             cell=cell, data_func=data_func)


def insert_if_not_exists(excel, sheet_name, cell, data_func):
    item_exists = excel.if_sheet_item_exists(sheet_name, cell)
    if not item_exists:
        data = data_func()
        excel.insert_sheet_item(sheet_name, cell, data)


def write_to_csv(tickers, update=False):
    if update:
        for ticker in tickers:
            if ticker == "":
                pass
            else:
                csv_writer = CompanyInfo()
                sc = FinvizScraper(ticker)

                if not csv_writer.company_exists(ticker):
                    data = sc.get_data()
                    csv_writer.insert_data(data=data)


def insert_into_universal_dashboard(tickers):
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
        excel.insert_tickers_to_dashboard(sector, company_sectors[sector])


def main():

    # Get the tickers currently on the dashboard.
    excel = UniversalDashboard()
    start = time.time()
    # Get the tickers from the directory.
    ticker_list = get_tickers_in_directory()

    """prep_excel_files(ticker_list)

    write_to_csv(ticker_list)"""

    insert_into_universal_dashboard(ticker_list)
    # print(f"Elapse: {end - start}")


main()
