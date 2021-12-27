# -*- coding: utf-8 -*-
"""
Created on Sun Dec 12 10:05:10 2021

@author: Chris
"""

from LeagueAnalysis import LeagueAnalysis
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


#%% this code is for testing.

apiKey = "RGAPI-be013ceb-17d3-445a-82fa-e1bd7bba68fk"

lolA = LeagueAnalysis(apiKey, summoner_name="Moving Object 1")


#%%

example_plotting_data = lolA.create_event_timeline_dataframe("EUW1_5612017679")
example_plotting_dict = lolA.parse_champion_timeline_dataframe(
    example_plotting_data, parse_on="teamId"
)

lolA.plot_positional_data(example_plotting_dict[100.0], example_plotting_dict[200.0])
