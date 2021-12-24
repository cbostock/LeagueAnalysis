# -*- coding: utf-8 -*-
"""
Created on Sun Dec 12 10:05:10 2021

@author: Chris
"""

from LeagueAnalysis import LeagueAnalysis
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


#%%

apiKey = "RGAPI-e029bd7b-a0bc-4cc6-b35e-86cb19d60fe2"

lolA = LeagueAnalysis(apiKey, summonerName="Moving Object 2")

# df = lolA.create_mastery_table()
# print(df)


#%%

tsData = lolA.create_champion_timeline_dataframe("EUW1_5612017679")
print(tsData )

tsData_expanded = lolA.expand_champion_stats(tsData)
print()

#%%

example_plotting_data = lolA.create_event_timeline_dataframe('EUW1_5612017679')
example_plotting_dict = lolA.parse_champion_timeline_dataframe(example_plotting_data, parse_on='teamId')

lolA.plot_positional_data(example_plotting_dict[100.0],example_plotting_dict[200.0],index_label=True)
