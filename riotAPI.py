# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 10:15:32 2021

@author: Chris Bostock
"""

import requests
import pandas as pd
from leagueDB import leagueDB

#%% riotAPI Class


class RiotAPI(leagueDB):

    #%% class inistalisation
    def __init__(
        self,
        apiKey: str,
        ddragon: str = "9.3.1",
        summonerName: str = None,
        region: str = "euw",
        dbCaching: bool = True,
        dbName: str = None,
        contsolePrintOut: bool = False,
    ):

        """A basic class to interact with riots league of legends api endpoints.

        This class inherentes leagueDB to enable localise storage of data to reduce
        the number of potential API calls.


        Parameters
        ----------
        apiKey : str
            Your api key to access riot's api endpoints..
        ddragon : str, optional
            The data dragon version to obtain.. The default is "9.3.1".
        summonerName : str, optional
            The summoner name for all data retrieval when no other summoner
            name has been defined. The default is None.
        region : str, optional
            Server region of the summoner:
            'br','eune','euw','jp','kr','la1','la2','na','oc','tr','ru'. The default is "euw".
        dbCaching : bool, optional
            To enable db caching to reduce api calls for already recieved data.
            Storing the data within local database allows for future analysis
            without the use of an active API key.. The default is True.
        dbName : str, optional
            The name of the database.  If none is passed a default name
            of loldb will be used.. The default is None.
        contsolePrintOut : bool, optional
            Prints out any interation with the db to the console. The default is False.


        Returns
        -------
        None.

        """

        # cachine database
        if dbCaching:
            super().__init__(dbName=dbName, contsolePrintOut=contsolePrintOut)
            self.dbCachingActive = True
        else:
            self.dbCachingActive = False

        if summonerName is not None:
            self.summoner_name = summonerName

        # region
        self.region: str = region

        # api addressed and keys
        self.__setup_api_details()

        # headers
        self.header: dict = {"X-Riot-Token": apiKey}

        # endpoints
        self.api_endpoints: dict = {}
        self.__setup_endpoints()

        # responses:
        self.response: dict = {}

        # champ list
        self.ddragon_version: str = ddragon
        self.champion_list: dict = {}

        # get champ list
        self.get_champ_details()

    #%% validate summoner name
    def __validate_summoner_name(self, summoner_name: str):
        """ Method to establish which summoner name to use.


        Parameters
        ----------
        summoner_name : str
            Summoner Name to be validated.

        Raises
        ------
        NameError
            No summoner name found.

        Returns
        -------
        summoner_name : str
            The summoner name to be used within the api urls.

        """

        if summoner_name is None and self.summoner_name is not None:
            summoner_name = self.summoner_name
        elif summoner_name is None and self.summoner_name is None:
            raise NameError("Summoner Name Required")

        return summoner_name

    #%% storing or using an additional name
    def __initalise_cache(self, summoner_name: str):
        """Initalise a key within the response property for the given summoner name


        Parameters
        ----------
        summoner_name : str
            Summoner Name to initalise

        Returns
        -------
        None.

        """

        # create caching area
        if summoner_name not in self.response:
            self.response[summoner_name] = {}

    #%% api details (euw atm)
    def __setup_api_details(self):
        """Intalises all regional specific api urls for the given region


        Returns
        -------
        None.

        """

        self.api_details = {}

        region = self.region.lower()

        if region == "br":
            self.api_details["url"] = "https://br1.api.riotgames.com"
        elif region == "eune":
            self.api_details["url"] = "https://eun1.api.riotgames.com"
        elif region == "euw":
            self.api_details["url"] = "https://euw1.api.riotgames.com"
        elif region == "jp":
            self.api_details["url"] = "https://jp1.api.riotgames.com"
        elif region == "kr":
            self.api_details["url"] = "https://kr.api.riotgames.com"
        elif region == "la1":
            self.api_details["url"] = "https://la1.api.riotgames.com"
        elif region == "la2":
            self.api_details["url"] = "https://la2.api.riotgames.com"
        elif region == "na":
            self.api_details["url"] = "https://na1.api.riotgames.com"
        elif region == "oc":
            self.api_details["url"] = "https://oc1.api.riotgames.com"
        elif region == "tr":
            self.api_details["url"] = "https://tr1.api.riotgames.com"
        elif region == "ru":
            self.api_details["url"] = "https://ru.api.riotgames.com"

        if region in ["eune", "euw", "ru", "tr"]:
            self.api_details["regionalRouting"] = "https://europe.api.riotgames.com"
        elif region in ["la1", "la2", "na", "br"]:
            self.api_details["regionalRouting"] = "https://americas.api.riotgames.com"
        elif region in ["jp", "kr", "oc"]:
            self.api_details["regionalRouting"] = "https://asia.api.riotgames.com"

    #%% endpoint locations
    def __setup_endpoints(self):
        """ Loads end points into memory.


        Returns
        -------
        None.

        """

        self.api_endpoints["summoner-by-name"]: dict = {}
        self.api_endpoints["summoner-by-name"][
            "url"
        ]: str = "/lol/summoner/v4/summoners/by-name/{}"
        self.api_endpoints["summoner-by-name"]["parameter"]: str = "Summoner Name"

        self.api_endpoints["champ-mast-by-name"]: dict = {}
        self.api_endpoints["champ-mast-by-name"][
            "url"
        ]: str = "/lol/champion-mastery/v4/champion-masteries/by-summoner/{}"
        self.api_endpoints["champ-mast-by-name"]["parameter"]: str = "id"

        self.api_endpoints["curr-game-by-summoner"]: dict = {}
        self.api_endpoints["curr-game-by-summoner"][
            "url"
        ]: str = "/lol/spectator/v4/active-games/by-summoner/{}"
        self.api_endpoints["curr-game-by-summoner"]["parameter"]: str = "id"

        self.api_endpoints["match-list"]: dict = {}
        self.api_endpoints["match-list"][
            "url"
        ]: str = "/lol/match/v5/matches/by-puuid/{}/ids"
        self.api_endpoints["match-list"]["parameter"]: str = "puid"

        self.api_endpoints["match_summary"]: dict = {}
        self.api_endpoints["match_summary"]["url"]: str = "/lol/match/v5/matches/{}"

        self.api_endpoints["match_timeline"]: dict = {}
        self.api_endpoints["match_timeline"][
            "url"
        ]: str = "/lol/match/v5/matches/{}/timeline"

    #%% make endpoint url
    def __make_url(
        self, endpoint_key: str, summoner_name: str, regional_routing: bool = False
    ):
        """Generates the appropriate url


        Parameters
        ----------
        endpoint_key : str
            endpoint key which is stored within self.api_endpoints.
        summoner_name : str
            Summoner name for the api endpoint.
        regional_routing : bool, optional
            If the regional url is required. The default is False.

        Returns
        -------
        url : str
            The generated url.

        """

        # check to make sure we have summoner details
        summoner_datails = self.getStoredData(
            "summoner_names", "account_name", summoner_name
        )

        # if we don't go and get it
        if summoner_datails is None:
            summoner_datails_retrned = self.get_summoner_by_name(summoner_name)

            summoner_datails = {}
            summoner_datails["details"] = summoner_datails_retrned

        # regional routing..
        if regional_routing:
            url: str = "{}{}".format(
                self.api_details["regionalRouting"],
                self.api_endpoints[endpoint_key]["url"],
            )
        else:
            url: str = "{}{}".format(
                self.api_details["url"], self.api_endpoints[endpoint_key]["url"]
            )

        # endpoint selection
        if self.api_endpoints[endpoint_key]["parameter"] == "Summoner Name":
            url: str = url.format(summoner_name)

        elif self.api_endpoints[endpoint_key]["parameter"] == "id":
            url: str = url.format(summoner_datails["details"]["id"])

        elif self.api_endpoints[endpoint_key]["parameter"] == "puid":
            url: str = url.format(summoner_datails["details"]["puuid"])

        return url

    #%% make match url
    def __make_match_url(self, endpoint_key: str, match_id: str):
        """Generates a url for a given match id.


        Parameters
        ----------
        endpoint_key : str
            endpoint key which is stored within self.api_endpoints.
        match_id : str
            Match id for the api endpoint.

        Returns
        -------
        url : str
            The generated url.

        """

        url: str = "{}{}".format(
            self.api_details["regionalRouting"], self.api_endpoints[endpoint_key]["url"]
        )
        url: str = url.format(match_id)

        return url

    #%% get the champion list from data dragon
    def get_champ_details(self):
        """Retreives the data dragon data via riot's api.

        The information is also cached within a dictionary as an object
        property: self.champion_list.  A DataFrame object is also created within
        this property (self.champion_list['df']) for later use.


        Raises
        ------
        Exception
            API Failure.

        Returns
        -------
        pd.DataFrame
            The resulting data dragon data within a DataFrame

        """

        champ_list = None

        if self.dbCachingActive:
            champ_list = self.getStoredData(
                "champ_list", "ddragon", self.ddragon_version
            )

        # if we have stored data:
        if champ_list is not None:
            self.champion_list["df"] = pd.DataFrame.from_dict(
                champ_list["details"], orient="index"
            )

        # if we don't go and get it
        else:
            url: str = "https://ddragon.leagueoflegends.com/cdn/{}/data/en_GB/champion.json".format(
                self.ddragon_version
            )

            # check to see if the champ list dict is empty
            if len(self.champion_list) == 0:
                try:
                    response = requests.get(url)
                    self.champion_list = response.json()
                except Exception as e:
                    raise Exception("get_champ_details :: failed :: {}".format(e))

            if self.champion_list is not None:
                self.champion_list["df"] = pd.DataFrame.from_dict(
                    self.champion_list["data"], orient="index"
                )
            else:
                self.champion_list["df"] = None

            # update lolbd
            if self.dbCachingActive:
                self.insertData(
                    "champ_list",
                    "ddragon",
                    self.ddragon_version,
                    self.champion_list["data"],
                )

        return self.champion_list["df"]

    #%%
    def __get_summmoner_data(
        self, endpoint: str, summoner_name: str, regional_routing: bool = False
    ):
        """Obtain Summoner Data.


        Parameters
        ----------
        endpoint : str
            Endpoint key which the method is targeting.
        summoner_name : str
            Summoner Name.
        regional_routing : bool, optional
            If regional routing is required. The default is False.

        Raises
        ------
        Exception
            API failure.

        Returns
        -------
        result : dict
            The response within in a dictionary.

        """

        if endpoint == "summoner-by-name":
            url: str = "{}{}".format(
                self.api_details["url"], self.api_endpoints["summoner-by-name"]["url"]
            )
            url: str = url.format(summoner_name)
        else:
            url: str = self.__make_url(endpoint, summoner_name, regional_routing)

        try:
            response = requests.get(url, headers=self.header)
            result = response.json()
        except Exception as e:
            raise Exception("{} :: failed :: {}".format(endpoint, e))

        return result

    #%% get summoner details
    def get_summoner_by_name(self, summoner_name: str = None):
        """Retreieves Summoner information using the summoner name.

        To utalise other endpoints information is required from this endpoint.
        Such as id, and puuid.  If dbCahcing has been enabled this information
        will be stored within the appropriate database.


        Parameters
        ----------
        summoner_name : str, optional
            If None is passed the summoner name used will be from the object
            inialisation. The default is None.

        Returns
        -------
        result : dict
            The response within in a dictionary.

        """

        summoner_name = self.__validate_summoner_name(summoner_name)

        table = "summoner_names"
        table_key = "account_name"
        endpoint = "summoner-by-name"

        if self.dbCachingActive:
            result = self.getStoredData(table, table_key, summoner_name)
        else:
            result = None

        if result is None:
            result = self.__get_summmoner_data(endpoint, summoner_name)

            if self.dbCachingActive and "status" not in result:
                self.insertData(table, table_key, summoner_name, result)

        return result

    #%% current game stats
    def get_live_game_info(self, summoner_name: str = None):
        """Obtains the current live game's data.

        This endpoint will succeed when there is an ongoing game.  Otherwise
        the request will fail.  This information is not stored within a db.


        Parameters
        ----------
        summoner_name : str, optional
            If None is passed the summoner name used will be from the object
            inialisation. The default is None.

        Returns
        -------
        result : dict
            The response within in a dictionary.

        """

        summoner_name = self.__validate_summoner_name(summoner_name)
        self.__initalise_cache(summoner_name)

        endpoint = "curr-game-by-summoner"

        result = self.__get_summmoner_data(endpoint, summoner_name)

        return result

    #%% match history
    def get_list_of_matches(self, summoner_name: str = None):
        """Retrieves the last 20 match id's for a given summoner name.


        Parameters
        ----------
        summoner_name : str, optional
            If None is passed the summoner name used will be from the object
            inialisation. The default is None.

        Returns
        -------
        result : dict
            The response within in a dictionary.

        """

        summoner_name = self.__validate_summoner_name(summoner_name)

        endpoint = "match-list"
        result = self.__get_summmoner_data(
            endpoint, summoner_name, regional_routing=True
        )

        # update loldb
        if self.dbCachingActive and "status" not in result:
            self.updateStoredSummonerMatchIds(summoner_name, result)

        return result

    #%%
    def __get_match_id_data(self, endpoint: str, match_id: str):
        """Get Match id information


        Parameters
        ----------
        endpoint : str
            Endpoint key which the method is targeting.
        match_id : str
            Descired match id

        Raises
        ------
        Exception
            API Failure.

        Returns
        -------
        result : TYPE
            The response within in a dictionary.

        """

        url: str = self.__make_match_url(endpoint, match_id)

        try:
            response = requests.get(url, headers=self.header)
            result = response.json()
        except Exception as e:
            raise Exception("{} :: failed :: {}".format(endpoint, e))

        return result

    #%% get match details
    def get_match_summary(self, match_id: str):
        """Retrieves the match summary for a  given match id.

        This this is a less comprehensive dataset in comparison to the timeline
        data.  Ths information has KPIs which have been summerised for the entire
        game.  This information is also stored within the db if enabled.


        Parameters
        ----------
        match_id : str
            The match id of the data required.

        Returns
        -------
        result : dict
            The retrieved data in a dictionary format.

        """

        table = "match_summary"
        endpoint = "match_summary"

        result = self.getStoredData(table, "match_id", match_id)

        if result is None:
            result = self.__get_match_id_data(endpoint, match_id)

            if self.dbCachingActive:
                self.insertData(table, "match_id", match_id, result)

        return result

    #%% get match timeline details
    def get_match_timeline(self, match_id: str):
        """Retieve match timeline data for a givem match id.

        A more comprehensive dataset. The information retreieved contains 60s
        summaries and a timeline of key events: keys ect.  This data is also
        stored within the database.


        Parameters
        ----------
        match_id : str
            The match id of the data required.

        Returns
        -------
        result : dict
            The retrieved data in a dictionary format.

        """

        table = "match_timeline"
        endpoint = "match_timeline"

        result = self.getStoredData(table, "match_id", match_id)

        if result is None:
            result = self.__get_match_id_data(endpoint, match_id)

            if self.dbCachingActive:
                self.insertData(table, "match_id", match_id, result)

        return result

    #%% get summoner champ masteries
    def get_champion_mastery_by_summoner(self, summoner_name: str = None):
        """Retieves a list champions with the summoners champion mastery.


        Parameters
        ----------
        summoner_name : str, optional
             The summoner name in which you want to query. The default is None.

        Returns
        -------
        result : dict
            The retrieved data in a dictionary format.

        """

        summoner_name = self.__validate_summoner_name(summoner_name)

        endpoint = "champ-mast-by-name"
        result = self.__get_summmoner_data(endpoint, summoner_name)

        return result


#%%

if __name__ == "__main__":
    print("main")
