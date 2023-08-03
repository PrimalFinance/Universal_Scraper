import os
import csv


path = f"D:\\VisualStudioCode\\Projects\\Universal_Dashboard_Helper\\Company_Information\\company_info.csv"


class CompanyInfo:
    def __init__(self) -> None:
        pass

    def company_exists(self, ticker) -> bool:
        column_number = 0
        with open(path, 'r') as file:
            # create a CSV reader object
            reader = csv.reader(file)

            # iterate over each row in the file
            for row in reader:
                try:
                    # check if the search item exists in the specified column
                    if row[column_number] == ticker:
                        return True
                except IndexError:
                    return False
            else:
                return False

    def insert_data(self, data: dict):

        print(f"Data: {data}")
        # Open the CSV file in append mode
        with open(path, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=data.keys())

            # Check if the file is empty
            # Check if the file is empty
            if os.stat(path).st_size == 0:
                writer.writeheader()

            # Write the new dictionary to the CSV file
            writer.writerow(data)

    def get_data(self, ticker) -> str:
        column_number = 0
        with open(path, 'r') as file:
            # create a CSV reader object
            reader = csv.reader(file)

            # iterate over each row in the file
            for row in reader:
                try:

                    # check if the search item exists in the specified column
                    if row[column_number] == ticker:
                        data = {"Ticker": row[0], "Company Name": row[1], "Sector": row[2],
                                "Industry": row[3], "Country": row[4]}
                        return data
                except IndexError:
                    print(
                        f"- [Error] Failed to get data from csv for {ticker}")
