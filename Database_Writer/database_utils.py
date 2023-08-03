# For querying the database.
import sqlite3

# For getting the different date data points.
import datetime as dt

# For number generation & handling
import math
import random
import pandas as pd




class DatabaseUtilities:
    def __init__(self, conn: sqlite3):
        '''
        :Description: Passes the connection object of the database so the utilities operations can be performed.
        :param conn: sqlite connection from the database calling the DatabaseUtilities class.
        '''
        self.cur = conn.cursor()
        # Connection
        self.conn = conn

    '-------------------------------------------------------'
    def check_if_table_exists(self, table_name: str) -> bool:
        '''
        :Description: Takes a table name and searches for it in the current database.
        :param table_name: Table to check if it exists.
        :return:  bool
        '''
        try:
            # Query to execute
            query = f"""SELECT * FROM {table_name};"""
            # Get the list of tables matching then name.
            list_of_tables = self.cur.execute(query)
            # If the list is empty that means there are no tables matching the name we are searching for.
            if list_of_tables == []:
                return False
            else:
                return True
        except sqlite3.OperationalError:
            return False

    '-------------------------------------------------------'
    def check_if_table_is_empty(self, table_name: str) -> bool:
        '''
        :Description: Takes the table name and searches for it in the current database.
        :param table_name: Table to check if empty.
        :return: bool
        '''
        # Query to execute
        query = f"""SELECT * FROM {table_name}"""
        # Execute query
        self.cur.execute(query)
        # Get the data
        data = self.cur.fetchall()

        # If the table is empty the function will return True.
        if not data:
            return True
        else:
            return False

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


