# -*- cding: utf-8 -*-
"""
Created on Sat Dec 11 11:55:55 2021

@author: Chris Bostock
"""

import tinydb as tdb

#%%
class leagueDB:
    """ leagueDB is a object which interacts with a NoSQL database TinyDB.


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
            dbName = "loldb"

        # database files
        self.db_name = "{}.json".format(dbName)
        self.timeline_db_name = "{}-tl.json".format(dbName)
        self.champlist_db_name = "{}-cl.json".format(dbName)
        self.matchSummary_db_name = "{}-ms.json".format(dbName)

        # database object
        self.db = tdb.TinyDB(self.db_name)
        self.db_cl = tdb.TinyDB(self.champlist_db_name)  # champ list
        self.db_tl = tdb.TinyDB(self.timeline_db_name)  # time line
        self.db_ms = tdb.TinyDB(self.matchSummary_db_name)  # match summary

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
        self.contsolePrintOut = contsolePrintOut

    #%%
    def __consoleGetPrintout(self, result: str, methodName: str, key: str):

        if self.contsolePrintOut:
            if result == None:
                print(
                    "{} - {} :: No data found for {}".format(
                        self.db_name, methodName, key
                    )
                )
            else:
                print(
                    "{} - {} :: Data retrieved for {}".format(
                        self.db_name, methodName, key
                    )
                )


    #%%
    def __consoleInsertPrintout(self, successful: bool, methodName: str, key: str):

        if self.contsolePrintOut:
            if successful:
                print(
                    "{} - {} :: data added to the db with the key {}".format(
                        self.db_name, methodName, key
                    )
                )
            else:
                print(
                    "{} - {} :: data not added to the db {}".format(
                        self.db_name, methodName, key
                    )
                )


    #%%
    def listOfSummonersStored(self):
        """Returns the list of summoners stored within the database.


        Returns
        -------
        listOfSummoners : List
            The list of summoners stored within the database.

        """


        listOfSummoners: list = []

        for item in self.tables["summoner_names"]:
            listOfSummoners.append(["account_name"])

        return listOfSummoners

    #%% drop timeline table
    def dropTimelineTable(self):
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
            raise Exception("{} - dropTimelineTable :: failed :: {}".format(self.db_name, e))


    #%% get stored data
    def getStoredData(self, tblName: str, key: str, keyValue: str):
        """Returns data from the given table with the key and value required.


        Parameters
        ----------
        tblName : str
            The corresponding table name.
        key : str
            The key name for the given table. For example, 'match_id'.
        keyValue : Str
            The the value of the key which is required.  For example, .EUW1_5612017679'.

        Returns
        -------
        result : Dict
             The data associated with the key.

        """


        result = self.tables[tblName].get(self.user[key] == keyValue)
        self.__consoleGetPrintout(result, tblName, keyValue)

        return result

    #%% add data to store
    def insertData(self, tblName: str, key: str, keyValue: str, data: dict):
        """Returns data from the given table with the key and value required.


        Parameters
        ----------
        tblName : str
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
        result = self.getStoredData(tblName, key, keyValue)

        # if we dont, result == None
        if result is None:

            try:
                value2insert = {key: keyValue, "details": data}
                self.tables[tblName].insert(value2insert)

                successful = True

            except Exception as e:
                print("{} :: failed :: {}".format(tblName, e))
        else:
            successful = True

        self.__consoleInsertPrintout(successful, tblName, keyValue)

        return successful

    #%% update match list
    def updateStoredSummonerMatchIds(self, summonerName: str, newMatches: list):
        """Add new match id's to the existing match id list


        Parameters
        ----------
        summonerName : str
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

        matchList = self.getStoredData("match_ids", "account_name", summonerName)
        newSummoner = False

        if matchList is not None:

            matchList = matchList["matches"]

            for match in newMatches:
                if match not in matchList:
                    matchList.append(match)

        else:
            matchList = newMatches
            newSummoner = True

        value2update = {"account_name": summonerName, "matches": matchList}

        if newSummoner:
            self.tables["match_ids"].insert(value2update)
        else:
            self.tables["match_ids"].update(value2update)

        return matchList


#%%
if __name__ == "__main__":

    print("")
