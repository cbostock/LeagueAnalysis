# -*- coding: utf-8 -*-
"""
Created on Fri Dec 17 10:14:31 2021

@author: Chris Bostock
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from riotAPI import RiotAPI

#%% LeagueAnalysis
class LeagueAnalysis(RiotAPI):
    """League Analysis

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
        """ A object used to analysis league of legends data.

        This class inherentes from the riotAPI class to obtain the data required
        to be analysed.


        Parameters
        ----------
        api_key: str
             Your api key to access riot's api endpoints.

         ddragon: str
             (Default value = 9.3.1)
             The data dragon version to obtain.

         summoner_name: str
             (Default value = None)
             The summoner name for all data retrieval when no other summoner
             name has been defined.

         region: str :
             (Default value = euw)
             Server region of the summoner

         db_saving: bool
             (Default value = True)
             To enable db caching to reduce api calls for already recieved data.
             Storing the data within local database allows for future analysis
             without the use of an active API key.

         dbName: str
             (Default value = None)
             The name of the database.  If none is passed a default name
             of loldb will be used.

         contsolePrintOut : bool
             (Default value = False)
             Prints out any interation with the db to the console.

        """

        super().__init__(
            api_key,
            ddragon = ddragon,
            summoner_name = summoner_name,
            region = region,
            db_saving = db_saving,
            db_name = db_name,
            contsole_print_out = contsole_print_out,
        )

    #%% __plot_positions
    @staticmethod
    def __plot_positions(ax, df, face_colour, index_label):

        # plot position data
        for index, row in df.iterrows():
            position = row["position"]

            if isinstance(position, dict):
                ax.plot(
                    int(position["x"]),
                    int(position["y"]),
                    "X",
                    markeredgecolor="k",
                    markerfacecolor=face_colour,
                    ms=8,
                )

                if index_label:
                    ax.text(
                        int(position["x"]),
                        int(position["y"]),
                        str(index),
                        horizontalalignment="left",
                        fontweight="semibold",
                    )

    #%% create_mastery_table
    def create_mastery_table(self, summoner_name: str = None):
        """Create's a champion mastery table in a dataframe.

        Generates a dataframe with the champion, mastery level, mastery points,
        and last time played. This infromation is not stored within the database


        Parameters
        ----------
        summoner_name : str, optional
            The summoner name of the mastery list required. The default is None.

        Returns
        -------
        cleanDf : pd.DataFrame
            The resulting dataframe from the queries and merging.

        Example
        -------
            df = lolA.create_mastery_table(); print(df)
            Out[65]:
                    name  championLevel  championPoints   lastTimePlayed-dt
            0      Yasuo              7          966690 2021-12-08 17:49:52
            1    Camille              5          156843 2021-12-16 22:01:43
            2     Kennen              5           64670 2021-09-09 21:53:58
            3    Nidalee              5           58225 2020-03-30 13:13:19
            4    Lee Sin              5           39973 2020-03-25 14:09:22
            ..       ...            ...             ...                 ...
            111    Karma              1             150 2019-09-22 13:29:14
            112  Warwick              1             150 2017-08-12 10:48:31
            113    Xayah              1             148 2021-08-06 23:37:14
            114     Sona              1             139 2021-09-04 20:21:58
            115   Viktor              1             120 2021-08-04 21:16:59

                [114 rows x 4 columns]

        """

        # champ mastery dataframe
        result = self.get_champion_mastery_by_summoner(summoner_name)

        df = pd.DataFrame(result)

        # readable datetime
        df["lastTimePlayed-dt"] = pd.to_datetime(df["lastPlayTime"], unit="ms")

        # int64 champion id
        self.champion_list["df"]["championId"] = self.champion_list["df"].key.astype(
            "int64"
        )

        # merge dataframes
        df = pd.merge(
            df, self.champion_list["df"], left_on="championId", right_on="championId"
        )

        # readable dataframe
        clean_df = df[["name", "championLevel", "championPoints", "lastTimePlayed-dt"]]

        return clean_df

    #%% create_event_timeline_dataframe
    def create_event_timeline_dataframe(
        self,
        match_id: str,
        creator_id: bool = True,
        victim_id: bool = True,
        killer_id: bool = True,
    ):
        """Creates a timeline dataframe with information from two api endpoints.

        Data from the timeline api, and the match summary api are used here to
        generate a comprehensive event timeline dataframe.  Information misisng
        from the timelin api, such as chamption name position etc. are joined
        together from the match details api endpoint.

        The dataframe can be used to filter down types of events or particular
        champtions/summoners.


        Parameters
        ----------
        match_id : str
            The match id for the reasulting timeline dataframe.
        creator_id : bool
            If a join is required to obtain the createrId's summoner name etc.
            Namely for WARD_PLACED events. The default is True.
        victim_id : bool
            If a join is required to obtain the victimId's summoner name etc. The default is True.
        killer_id : bool
            If a join is required to obtain the killerId's summoner name etc. The default is True.

        Returns
        -------
        tl_df : pd.DataFrame
            The resulting event timeline dataframe.

        Example
        -------
        df = lolA.create_event_timeline_dataframe('EUW1_5612017679'); print(df)
              realTimestamp  timestamp  ... championName_killer  individualPosition_killer
        0      1.639663e+12          0  ...                 NaN                        NaN
        1               NaN      25104  ...                 NaN                        NaN
        2               NaN      25104  ...                 NaN                        NaN
        3               NaN      25104  ...                 NaN                        NaN
        4               NaN      25104  ...                 NaN                        NaN
                    ...        ...  ...                 ...                        ...
        1645            NaN    1784834  ...              Irelia                        TOP
        1646            NaN    1769100  ...              Irelia                        TOP
        1647            NaN    1934930  ...              Irelia                        TOP
        1648            NaN    1091900  ...              Irelia                        TOP
        1649            NaN    1929942  ...              Irelia                        TOP

        [1650 rows x 50 columns]

        """

        # get timeline data
        raw_data_tl = self.get_match_timeline(match_id)

        # get match summary
        raw_data_ms = self.get_match_summary(match_id)

        tl_df = pd.DataFrame()

        for frame in raw_data_tl["details"]["info"]["frames"]:
            df = pd.DataFrame.from_dict(frame["events"], orient="columns")
            tl_df = tl_df.append(df)

        participants = pd.DataFrame(raw_data_tl["details"]["info"]["participants"])

        participants_detailed = pd.DataFrame(
            raw_data_ms["details"]["info"]["participants"]
        )

        participants_summary = participants_detailed[
            [
                "summonerName",
                "summonerId",
                "puuid",
                "championName",
                "individualPosition",
                "teamId",
                "win",
            ]
        ]

        # a dataframe with all participant id and participant information
        participants_summary = pd.merge(
            participants, participants_summary, left_on="puuid", right_on="puuid"
        )

        # obtain the participant informaion
        tl_df = pd.merge(
            tl_df,
            participants_summary,
            "outer",
            left_on="participantId",
            right_on="participantId",
            suffixes=("", "_info"),
        )

        if creator_id:
            # Obtain creator id
            tl_df = pd.merge(
                tl_df,
                participants_summary,
                "outer",
                left_on="creatorId",
                right_on="participantId",
                suffixes=("", "_creator"),
            )

        if victim_id:
            # obtain the victims information
            tl_df = pd.merge(
                tl_df,
                participants_summary,
                "outer",
                left_on="victimId",
                right_on="participantId",
                suffixes=("", "_victim"),
            )

        if killer_id:
            # obtain the killers information
            tl_df = pd.merge(
                tl_df,
                participants_summary,
                "outer",
                left_on="killerId",
                right_on="participantId",
                suffixes=("", "_killer"),
            )

        return tl_df

    #%% expand_champion_stats
    @staticmethod
    def expand_champion_stats(event_df: pd.DataFrame):
        """Expand the champion stats, and damage columns.


        Parameters
        ----------
        ts_df : pd.DataFrame
            The resuling DataFrame from self.create_champion_timeline_dataframe()

        Raises
        ------
        TypeError
            When ts_df has a length of zero.

        Returns
        -------
        expanded_df : pd.DataFrame
            The resulting dataframe.

        """

        pd.set_option("mode.chained_assignment", None)

        expanded_df = event_df.copy()

        if len(expanded_df) == 0:
            raise TypeError("DataFrame has a length of zero.")

        # Champion Stats
        champion_stat_keys = expanded_df["championStats"][0].copy().keys()

        # preallocate columns
        for key in champion_stat_keys:
            expanded_df[key] = np.NaN

        for j in range(0, len(expanded_df)):
            row_champion_stats = expanded_df["championStats"][j].copy()

            for key in row_champion_stats:
                expanded_df[key][j] = row_champion_stats[key]

        expanded_df.drop(columns=["championStats"], inplace=True)

        # Damage Stats
        damage_stat_keys = expanded_df["damageStats"][0].copy().keys()

        # preallocate columns
        for key in damage_stat_keys:
            expanded_df[key] = np.NaN

        for j in range(0, len(expanded_df)):
            row_damage_stats = expanded_df["damageStats"][j].copy()

            for key in row_damage_stats:
                expanded_df[key][j] = row_damage_stats[key]

        expanded_df.drop(columns=["damageStats"], inplace=True)

        return expanded_df

    #%% create_champion_timeline_dataframe
    def create_champion_timeline_dataframe(self, match_id: str):
        """Create a timesries dataframe from the timeline endpoint.


        Parameters
        ----------
        match_id : str
            The match id for the reasulting timeline dataframe.

        Returns
        -------
        ts_df : pd.DataFrame
            The resulting timeseries data DataFrame.

        Example
        -------

        """

        # get timeline data
        raw_data_tl = self.get_match_timeline(match_id)

        # get match summary
        raw_data_ms = self.get_match_summary(match_id)

        ts_df = pd.DataFrame()

        for frame in raw_data_tl["details"]["info"]["frames"]:
            df = pd.DataFrame.from_dict(frame["participantFrames"], orient="index")
            df["timestamp"] = frame["timestamp"]
            ts_df = ts_df.append(df)

        participants = pd.DataFrame(raw_data_tl["details"]["info"]["participants"])

        participants_detailed = pd.DataFrame(
            raw_data_ms["details"]["info"]["participants"]
        )

        participants_summary = participants_detailed[
            [
                "summonerName",
                "summonerId",
                "puuid",
                "championName",
                "individualPosition",
                "teamId",
                "win",
            ]
        ]

        # a dataframe with all participant id and participant information
        participants_summary = pd.merge(
            participants, participants_summary, left_on="puuid", right_on="puuid"
        )

        # merge participants information
        ts_df = pd.merge(
            ts_df,
            participants_summary,
            left_on="participantId",
            right_on="participantId",
        )

        return ts_df

    #%% parse_champion_timeline_dataframe
    def parse_champion_timeline_dataframe(
        self,
        ts_df: pd.DataFrame = None,
        match_id: str = None,
        parse_on: str = "championName",
    ):
        """Seperactes each champiosn data into their own dataframe within a dictionary.

        Aggrogates the data for a given columns such as 'championName',
        'summonerName', 'puuid'.  The default is to parse for 'championName'


        Parameters
        ----------
        ts_df : pd.DataFrame, optional
            DataFrame required to be parsed. The default is None.
        match_id : str, optional
            Match id of the data required. The default is None.
        parse_on: str, optional
            Chose what to arrgorate the dictionary on. For example,
            'championName', 'summonerName', etc. The default is 'championName'

        Raises
        ------
        TypeError
            If a DataFrame or match id has not been passed.

        Returns
        -------
        parsed_df_dict : dict
            The data for each chamption within a dictionary, where the 'keys'
            are the champion name, and the values are dataframes

        Example
        -------
        champ_dict = lolA.parse_champion_timeline_dataframe(match_id='EUW1_5612017679')
        champ_dict['Twitch']
        Out[1]:
                                                championStats  ...       time
        0   {'abilityHaste': 0, 'abilityPower': 0, 'armor'...  ...   0.000000
        1   {'abilityHaste': 0, 'abilityPower': 24, 'armor...  ...   1.000383
        2   {'abilityHaste': 0, 'abilityPower': 24, 'armor...  ...   2.000750
        3   {'abilityHaste': 0, 'abilityPower': 24, 'armor...  ...   3.000933
        4   {'abilityHaste': 0, 'abilityPower': 24, 'armor...  ...   4.001350
        ...                                               ...  ...        ...
        33  {'abilityHaste': 0, 'abilityPower': 556, 'armo...  ...  33.009983
        34  {'abilityHaste': 0, 'abilityPower': 575, 'armo...  ...  34.010367
        35  {'abilityHaste': 0, 'abilityPower': 575, 'armo...  ...  35.010600
        36  {'abilityHaste': 0, 'abilityPower': 596, 'armo...  ...  36.011133
        37  {'abilityHaste': 0, 'abilityPower': 596, 'armo...  ...  36.220183

        [38 rows x 19 columns]

        """

        parsed_df_dict = {}

        if ts_df is None and match_id is not None:
            ts_df = self.create_champion_timeline_dataframe(match_id)
        elif ts_df is None and match_id is None:
            raise TypeError("DataFrame or match id required.")

        ts_df["time"] = ts_df["timestamp"] / 1_000 / 60
        parse_list = ts_df[parse_on].unique()

        for item in parse_list:
            parsed_df_dict[item] = (
                ts_df[(ts_df[parse_on] == item)].copy().reset_index(drop=True)
            )

        return parsed_df_dict

    #%% plot_positional_data
    def plot_positional_data(
        self,
        df: pd.DataFrame,
        df_for_comparison: pd.DataFrame = None,
        map_type: str = "summoners rift",
        index_label: bool = False,
    ):
        """Plot event data.

        The passed DataFrame requires the position columns which is returned
        from the riot api endpoint.  The values within this column are stored
        are stored within a dictionary.


        Parameters
        ----------
        df : pd.DataFrame
            pd.DataFrame with a position column which requires plotting.
            Blue markers when two pd.DataFrames are being plotted.
        df_for_comparison : pd.DataFrame, optional
            An additional pd.DataFrame with a position column that will be
            plotted along side the first pd.DataFrame. Red markers when two
            pd.DataFrames are being plotted. The default is None.
        map_type : str, optional
            Minimap style: 'summoners rift' or 'howling abyss'. The default
            is 'summoners rift'.
        index_label : bool, optional
            Index value printed next to the marker. The default is False.

        Returns
        -------
        matplotlib figure.

        """

        colours = {"blue": "#1E90FF", "red": "#EE3B3B", "green": "#32CD32"}

        # Read map png
        if map_type == "summoners rift":
            img = plt.imread("maps\\summoners_rift_map_11.png")
        elif map_type == "howling abyss":
            img = plt.imread("maps\\howling_abyss_map_12.png")
        else:
            raise NameError("map_type: {} not found".format(map_type))

        # show map on plot
        fig, ax = plt.subplots()

        map_size = 14_750
        ax.imshow(img, extent=[0, map_size, 0, map_size])
        ax.set_xticks([])
        ax.set_yticks([])

        if df_for_comparison is not None:
            face_colour = colours["blue"]
        else:
            face_colour = colours["green"]

        self.__plot_positions(ax, df, face_colour, index_label)

        if df_for_comparison is not None:
            self.__plot_positions(ax, df_for_comparison, colours["red"], index_label)

    #%% combine_match_summaries
    def combine_match_summaries(self, summoner_name: str, match_id_list: list):
        """Create a pd.DataFrame of all the match summaries for a given summoner.

        The pd.DataFrame generated compiles all the match summaries for a given
        summoner for a list of specified games.


        Parameters
        ----------
        summoner_name : str
            sumoner name.
        match_id_list : list
            DESCRIPTION.

        Returns
        -------
        summoner_match_summaries : TYPE
            DESCRIPTION.

        """

        summoner_match_summaries = pd.DataFrame()

        for match_id in match_id_list:

            try:

                match_details = self.get_match_summary(match_id)

                if "status" not in match_details:

                    match_details_df = pd.DataFrame(
                        match_details["details"]["info"]["participants"]
                    )

                    match_details_df["match_id"] = match_id

                    summoner_match_summaries = summoner_match_summaries.append(
                        match_details_df[
                            (match_details_df["summonerName"] == summoner_name)
                        ]
                    )

            except:
                print("unable to get match summary for: {}".format(match_id))
                continue

        return summoner_match_summaries

#%% if __name__ == "__main__":
if __name__ == "__main__":
    print("main")
