# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 10:15:32 2021

@author: Chris Bostock
"""

import requests
import pandas as pd
from db.LeagueDB import LeagueDB

#%% riotAPI Class


class RiotAPI(LeagueDB):
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
    db_saving : bool, optional
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

    #%% __init__
    def __init__(
        self,
        api_key: str,
        ddragon: str = "9.3.1",
        summoner_name: str = None,
        region: str = "euw",
        db_saving: bool = True,
        db_name: str = None,
        contsole_print_out: bool = False,
    ):

        # cachine database
        if db_saving:
            super().__init__(db_name=db_name, contsole_print_out=contsole_print_out)
            self.db_savingActive = True
        else:
            self.db_savingActive = False

        if summoner_name is not None:
            self.summoner_name = summoner_name

        # region
        self.region: str = region

        # api addressed and keys
        self.__setup_api_details()

        # headers
        self.header: dict = {"X-Riot-Token": api_key}

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

    #%% __validate_summoner_name
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

    #%% __initalise_cache
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

    #%% __setup_api_details
    def __setup_api_details(self):
        """Intalises all regional specific api urls for the given region


        Returns
        -------
        None.

        """

        self.api_details = {}

        region = self.region.lower()

        url_list = {}
        url_list["br"] = "https://br1.api.riotgames.com"
        url_list["eune"] = "https://eun1.api.riotgames.com"
        url_list["euw"] = "https://euw1.api.riotgames.com"
        url_list["jp"] = "https://jp1.api.riotgames.com"
        url_list["kr"] = "https://kr.api.riotgames.com"
        url_list["la1"] = "https://la1.api.riotgames.com"
        url_list["la2"] = "https://la2.api.riotgames.com"
        url_list["na"] = "https://na1.api.riotgames.com"
        url_list["oc"] = "https://oc1.api.riotgames.com"
        url_list["tr"] = "https://tr1.api.riotgames.com"
        url_list["ru"] = "https://ru.api.riotgames.com"

        region_list = [
            "br",
            "eune",
            "euw",
            "jp",
            "kr",
            "la1",
            "la2",
            "na",
            "oc",
            "tr",
            "ru",
        ]

        if region not in region_list:
            raise NameError(
                "{} is not in the list of regions: {}".format(region, region_list)
            )

        self.api_details["url"] = url_list[region]

        if region in ["eune", "euw", "ru", "tr"]:
            self.api_details["regionalRouting"] = "https://europe.api.riotgames.com"
        elif region in ["la1", "la2", "na", "br"]:
            self.api_details["regionalRouting"] = "https://americas.api.riotgames.com"
        elif region in ["jp", "kr", "oc"]:
            self.api_details["regionalRouting"] = "https://asia.api.riotgames.com"

    #%% __setup_endpoints
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

    #%% __make_url
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
        summoner_datails = self.get_stored_data(
            "summoner_names", "account_name", summoner_name
        )

        # if we don't go and get it
        if summoner_datails is None:
            summoner_datails = self.get_summoner_by_name(summoner_name)

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

    #%% __make_match_url
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

    #%% __response_checker
    @staticmethod
    def __response_checker(response):
        """Check the vadility of the response


        Parameters
        ----------
        response : dict
            response from the api call.

        Raises
        ------
        Exception
            If the data has not been returned.

        Returns
        -------
        None.

        """

        if "status" in response and "status_code" in response["status"]:
            raise Exception(
                "Error: {} API key incorrect or expired.".format(
                    response["status"]["status_code"]
                )
            )

    #%% __get_summmoner_data
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
            self.__response_checker(result)
        except Exception as e:
            raise Exception("{} :: failed :: {}".format(endpoint, e))

        return result

    #%% __get_match_id_data
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
        result : dict
            The response within in a dictionary.

        """

        url: str = self.__make_match_url(endpoint, match_id)

        try:
            response = requests.get(url, headers=self.header)
            result = response.json()
            self.__response_checker(result)
        except Exception as e:
            raise Exception("{} :: failed :: {}".format(endpoint, e))

        return result

    #%% get_champ_details
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
            Champion.json from data dragon formatted to be a pd.DataFrame.

        """
        champ_list = None

        if self.db_savingActive:
            champ_list = self.get_stored_data(
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
                    self.__response_checker(self.champion_list)
                except Exception as e:
                    raise Exception("get_champ_details :: failed :: {}".format(e))

            if self.champion_list is not None:
                self.champion_list["df"] = pd.DataFrame.from_dict(
                    self.champion_list["data"], orient="index"
                )
            else:
                self.champion_list["df"] = None

            # update lolbd
            if self.db_savingActive:
                self.insert_data(
                    "champ_list",
                    "ddragon",
                    self.ddragon_version,
                    self.champion_list["data"],
                )

        return self.champion_list["df"]

    #%% get_summoner_by_name
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

        if self.db_savingActive:
            result = self.get_stored_data(table, table_key, summoner_name)
        else:
            result = None

        if result is None:
            result_returned = self.__get_summmoner_data(endpoint, summoner_name)

            result = {}
            result["details"] = result_returned

            if self.db_savingActive and "status" not in result:
                self.insert_data(table, table_key, summoner_name, result_returned)

        return result

    #%% get_summoner_account_id
    def get_summoner_account_id(self, summoner_name: str = None):
        """Returns the account id for a summoner name.


        Parameters
        ----------
        summoner_name : str, optional
            Summoner name for the account requring the information. The default is None.

        Returns
        -------
        summoner_id : str
            account id for the summoner

        """

        summoner_name = self.__validate_summoner_name(summoner_name)
        summoner_details = self.get_summoner_by_name(summoner_name)

        if summoner_details is not None:
            summoner_id = summoner_details["details"]["accountId"]

        return summoner_id

    #%% get_live_game_info
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

    #%% get_list_of_matches
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
        if self.db_savingActive and "status" not in result:
            account_id = self.get_summoner_account_id(summoner_name)
            self.update_stored_summoner_match_ids(account_id, result)

        return result

    #%% get_match_summary
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

        table: str = "match_summary"
        endpoint: str = "match_summary"

        result = self.get_stored_data(table, "match_id", match_id)

        if result is None:
            reponse_result = self.__get_match_id_data(endpoint, match_id)
            self.__response_checker(reponse_result)

            if self.db_savingActive:
                self.insert_data(table, "match_id", match_id, reponse_result)

            result: dict = {}
            result["details"] = reponse_result

        return result

    #%% get_match_timeline
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

        table: str = "match_timeline"
        endpoint: str = "match_timeline"

        result = self.get_stored_data(table, "match_id", match_id)

        if result is None:
            reponse_result = self.__get_match_id_data(endpoint, match_id)
            self.__response_checker(reponse_result)

            if self.db_savingActive:
                self.insert_data(table, "match_id", match_id, reponse_result)

            result: dict = {}
            result["details"] = reponse_result

        return result

    #%% get_champion_mastery_by_summoner
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
        self.__response_checker(result)

        return result

    #%% get_list_of_stored_match_ids_for_summoner_name
    def get_list_of_stored_match_ids_for_summoner_name(self, summoner_name: str = None):
        """Get the list of stored match id's from the db.

        Due to summoners changing their names it is easier and simpler to store
        match id that are linked to their account id oppose to their summoner name


        Parameters
        ----------
        summoner_name : str, optional
            The summoner name in which you want to query.. The default is None.

        Returns
        -------
        match_list : list
            List of matches stored within the database.

        """

        summoner_name = self.__validate_summoner_name(summoner_name)
        account_id = self.get_summoner_account_id(summoner_name)

        match_list = self.get_list_of_stored_match_ids_for_account_id(account_id)

        return match_list


#%% if __name__ == "__main__"
if __name__ == "__main__":
    print("main")
