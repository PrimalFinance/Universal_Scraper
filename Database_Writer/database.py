# For querying the database.
import os
import sqlite3

# For getting the different date data points.
import datetime as dt

# Database utilities
import pandas as pd

from Database_Writer.database_utils import DatabaseUtilities

cwd = os.getcwd()

db_directory = "C:\\Users\\William\\PycharmProjects\\Investing\\Webscraping\\ROIC\\Database_Files"


class AssetDatabase(DatabaseUtilities):
    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        # Establish connection to the database we want.
        self.conn = sqlite3.connect(f"{db_directory}\\{ticker.upper()}.db")
        # Create cursor object
        self.cur = self.conn.cursor()
        self.db_filename = ticker + ".db"
        super().__init__(self.conn)




    '-------------------------------------------------------'
    def create_table_from_dataframe(self, df: pd.DataFrame, table_type: str):
        '''
        - Takes a pandas dataframe and will create a table based on the data contained within the dataframe.
        :param df: Dataframe to insert.
        :param table_type: Determine what type of table to create.
        :return: None
        '''
        # Possible table types
        #----------------
        # summary
        # income_statement
        # balance_sheet
        # cash_flow
        exists = self.check_if_table_exists(table_name=table_type)
        # If there is not already data in this file.
        if not exists:
            # Check if there are duplicates in the column names
            duplicates = self.check_for_duplicates(df.columns)
            # Duplicates have been found
            if len(duplicates) >= 1:
                index_to_delete = self.get_index_by_element(df.columns, duplicates)
                print(f"DF: {df}")
                print(f"col1: {df.columns}")
                print(f"Index to delete: {index_to_delete}")
                df = df.drop(df.columns[index_to_delete], axis=1)
                print(f"col2: {df.columns}")
                print(f"Target: {df.columns[index_to_delete]}")
                print(f'DF 2: {df}')

            df.to_sql(table_type,self.conn,if_exists="replace")

    def check_if_file_exists(self):
        db_file_path = f"{db_directory}\\{self.ticker}.db"
        file_exists = os.path.exists(db_file_path)
        return file_exists

    '-------------------------------------------------------'

    def check_for_duplicates(self, myList):
        occurrences = []

        for item in myList:
            count = 0
            for x in myList:
                if x == item:
                    count += 1
            occurrences.append(count)

        duplicates = set()
        index = 0
        while index < len(myList):
            if occurrences[index] != 1:
                duplicates.add(myList[index])
            index += 1

        return list(duplicates)

    '-------------------------------------------------------'

    def get_data_from_table(self, table_name: str) -> pd.DataFrame:
        '''
        :Description: Fetches all of the data from the table.
        :param table_name: Table name to search for
        :return: pd.Dataframe
        '''
        try:
            # Query to execute
            query = f"""SELECT * FROM {table_name}"""
            # Execute query
            df = pd.read_sql(query, con=self.conn)
            # Return the data from the query.
            df = df.set_index("index")
            return df
        except sqlite3.OperationalError as e:
            print(f" -- {e}")

    '-------------------------------------------------------'

    def get_index_by_element(self, myList, element):

        indexes_of_desired_elements = []
        index = 0
        for elem in myList:
            print(f'Element: {element}     {element[0]}              Elem: {elem}')
            
            if element[0] == elem:
                indexes_of_desired_elements.append(index)
            index += 1

        print(f'{indexes_of_desired_elements}')
        # We are returning the first one because, chances are if
        # there is a duplicate year, the later entry is correcting the existing entry.
        # That is why we are sending the index of the first occurrence back to be deleted.
        return indexes_of_desired_elements[0]

    '-------------------------------------------------------'

    def wipe_database(self):
        table_names = ["summary", "income_statement", "balance_sheet", "cash_flow"]
        with self.conn:
            for i in range(len(table_names)):
                query = f"DROP TABLE IF EXISTS {table_names[i]}"
                self.cur.execute(query)
        print(f"[Cleared] -    Cleared database: {self.db_filename}")


