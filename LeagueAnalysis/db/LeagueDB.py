# -*- cding: utf-8 -*-
"""
Created on Sat Dec 11 11:55:55 2021

@author: Chris Bostock
"""

import tinydb as tdb

#%%
class LeagueDB:
    """ LeagueDB is a object which interacts with a NoSQL database TinyDB.


         Parameters
         ----------
         dbName : str, optional
             The name of the database.  If None is passed default name will be loldb.json with the
             corresponding databases having a prefix.
         contsolePrintOut : bool, optional
            Prints out to the console when data is retreieved or written. The default is False.

         Returns
         -------
         None.


    """

    #%%
    def __init__(self, dbName: str = None, contsolePrintOut: bool = False):

        # database name -- this could include a path

        if dbName is None:
            dbName = "./db/loldb"

        # database files
        self.db_name = "{}.json".format(dbName)
        self.timeline_db_name = "{}-tl.json".format(dbName)
        self.champlist_db_name = "{}-cl.json".format(dbName)
        self.match_summary_db_name = "{}-ms.json".format(dbName)

        # database object
        self.db = tdb.TinyDB(self.db_name)
        self.db_cl = tdb.TinyDB(self.champlist_db_name)  # champ list
        self.db_tl = tdb.TinyDB(self.timeline_db_name)  # time line
        self.db_ms = tdb.TinyDB(self.match_summary_db_name)  # match summary

        # User
        self.user = tdb.Query()

        # tables
        self.tables = {}
        self.tables["summoner_names"] = self.db.table("summoner_name")
        self.tables["match_ids"] = self.db.table("match_ids")
        self.tables["champ_list"] = self.db_cl.table("champ_list")
        self.tables["match_timeline"] = self.db_tl.table("match_timeline")
        self.tables["match_summary"] = self.db_ms.table("match_summary")

        # consoleprintout
        self.contsole_print_out = contsolePrintOut

    #%%
    def __console_get_printout(self, result: str, method_name: str, key: str):

        if self.contsole_print_out:
            if result is None:
                print(
                    "{} - {} :: No data found for {}".format(
                        self.db_name, method_name, key
                    )
                )
            else:
                print(
                    "{} - {} :: Data retrieved for {}".format(
                        self.db_name, method_name, key
                    )
                )

    #%%
    def __console_insert_printout(self, successful: bool, method_name: str, key: str):

        if self.contsole_print_out:
            if successful:
                print(
                    "{} - {} :: data added to the db with the key {}".format(
                        self.db_name, method_name, key
                    )
                )
            else:
                print(
                    "{} - {} :: data not added to the db {}".format(
                        self.db_name, method_name, key
                    )
                )

    #%%
    def get_list_of_stored_summoners(self):
        """Returns the list of summoners stored within the database.


        Returns
        -------
        listOfSummoners : List
            The list of summoners stored within the database.

        """

        list_of_summoners: list = []

        for item in self.tables["summoner_names"]:
            list_of_summoners.append(item["account_name"])

        return list_of_summoners

    #%%
    def get_list_of_stored_match_ids_for_account_id(self, account_id: str):
        """Return a list of stored match id's for a given account id.


        Parameters
        ----------
        summoner_name : str
            Summoner name for the requested list of match id's.

        Returns
        -------
        None.

        """

        match_list = self.getStoredData("match_ids", "account_id", account_id)

        if match_list is not None:
            match_list = match_list["matches"]
        else:
            match_list = []

        return match_list

    #%% drop timeline table
    def drop_all_tables(self):
        """ Drops all tables

        This is to be used when wanting to reduce processing time or reduce the db size.

        Raises
        ------
        Exception
            Failure when dropping the timeline table

        Returns
        -------
        None.

        """

        self.drop_champ_list_table()
        self.drop_match_summary_table()
        self.drop_summoner_info_table()
        self.drop_timeline_table()

    #%% drop timeline table
    def drop_champ_list_table(self):
        """ Drops all tables from the ***-cl.json.

        This is to be used when wanting to reduce processing time or reduce the db size.

        Raises
        ------
        Exception
            Failure when dropping the timeline table

        Returns
        -------
        None.

        """

        try:
            self.db_cl.drop_tables()
            print(
                "{} - dropChampListTable :: match_timeline table dropped".format(
                    self.champlist_db_name
                )
            )
        except Exception as e:
            raise Exception(
                "{} - dropChampListTable :: failed :: {}".format(
                    self.champlist_db_name, e
                )
            )

    #%% drop timeline table
    def drop_match_summary_table(self):
        """ Drops all tables from the ***-ms.json.

        This is to be used when wanting to reduce processing time or reduce the db size.

        Raises
        ------
        Exception
            Failure when dropping the timeline table

        Returns
        -------
        None.

        """

        try:
            self.db_ms.drop_tables()
            print(
                "{} - dropMatchSummaryTable :: match_timeline table dropped".format(
                    self.match_summary_db_name
                )
            )
        except Exception as e:
            raise Exception(
                "{} - dropMatchSummaryTable :: failed :: {}".format(
                    self.match_summary_db_name, e
                )
            )

    #%%
    def drop_summoner_info_table(self):
        """ Drops all tables from the ***.json.

        This is to be used when wanting to reduce processing time or reduce the db size.

        Raises
        ------
        Exception
            Failure when dropping the timeline table

        Returns
        -------
        None.

        """

        try:
            self.db.drop_tables()
            print(
                "{} - dropSummaryInfoTable :: match_timeline table dropped".format(
                    self.db_name
                )
            )
        except Exception as e:
            raise Exception(
                "{} - dropSummaryInfoTable :: failed :: {}".format(self.db_name, e)
            )

    #%% drop timeline table
    def drop_timeline_table(self):
        """ Drops all tables from the ***-tl.json.

        This is to be used when wanting to reduce processing time or reduce the db size.

        Raises
        ------
        Exception
            Failure when dropping the timeline table

        Returns
        -------
        None.

        """

        try:
            self.db_tl.drop_tables()
            print(
                "{} - dropTimelineTable :: match_timeline table dropped".format(
                    self.db_name
                )
            )
        except Exception as e:
            raise Exception(
                "{} - dropTimelineTable :: failed :: {}".format(self.db_name, e)
            )

    #%% get stored data
    def getStoredData(self, tbl_name: str, key: str, key_value: str):
        """Returns data from the given table with the key and value required.


        Parameters
        ----------
        tbl_name : str
            The corresponding table name.
        key : str
            The key name for the given table. For example, 'match_id'.
        key_value : Str
            The the value of the key which is required.  For example, .EUW1_5612017679'.

        Returns
        -------
        result : Dict
             The data associated with the key.

        """

        result = self.tables[tbl_name].get(self.user[key] == key_value)
        self.__console_get_printout(result, tbl_name, key_value)

        return result

    #%% add data to store
    def insertData(self, tbl_name: str, key: str, key_value: str, data: dict):
        """Returns data from the given table with the key and value required.


        Parameters
        ----------
        tbl_name : str
            Table in which the data is being stored.
        key : str
            The key name for the given table. For example, 'match_id'.
        keyValue : str
            The the value of the key which is being stored.  For example, 'EUW1_5612017679'.
        data : dict
            The data associated with the key.

        Returns
        -------
        successful : bool
            If successful method returns True.

        """
        successful = False

        # check to see if we already have that data:
        result = self.getStoredData(tbl_name, key, key_value)

        # if we dont, result == None
        if result is None:

            try:
                value2insert = {key: key_value, "details": data}
                self.tables[tbl_name].insert(value2insert)

                successful = True

            except Exception as e:
                print("{} :: failed :: {}".format(tbl_name, e))
        else:
            successful = True

        self.__console_insert_printout(successful, tbl_name, key_value)

        return successful

    #%% update match list
    def updateStoredSummonerMatchIds(self, account_id: str, newMatches: list):
        """Add new match id's to the existing match id list


        Parameters
        ----------
        summoner_name : str
            Summoner name the matches are associated with.
        newMatches : list
            A list of match id's.
            For example ['EUW1_5612017679','EUW1_561201780','EUW1_56120176781'].


        Returns
        -------
        matchList : list
            The matches added to the database. This will only include matches which are not already
                stored within the database.

        """

        match_list = self.getStoredData("match_ids", "account_id", account_id)
        new_summoner = False

        if match_list is not None:

            match_list = match_list["matches"]

            for match in newMatches:
                if match not in match_list:
                    match_list.append(match)

        else:
            match_list = newMatches
            new_summoner = True

        value2update = {"account_id": account_id, "matches": match_list}

        if new_summoner:
            self.tables["match_ids"].insert(value2update)
        else:
            self.tables["match_ids"].update(value2update)

        return match_list


#%%
if __name__ == "__main__":

    print("")
