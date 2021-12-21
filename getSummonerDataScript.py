# -*- coding: utf-8 -*-
"""
Created on Sun Dec 12 10:05:10 2021

@author: Chris
"""

import pandas as pd
from lolAnalysis import LeagueAnalysis

import matplotlib.pyplot as plt
from pprint import pprint


#%%

apiKey = "RGAPI-b0201a7b-93b7-48e4-a2d0-e162150cd6c7"

lolA = LeagueAnalysis(apiKey, summonerName="BlazingB")

df =  lolA.create_mastery_table()

#%%

result = lolA.get_match_timeline("EUW1_5612017679")

#%%

result = lolA.create_event_timeline_dataframe('EUW1_5612017679')


#%%

tsData = lolA.create_champion_timeline_dataframe('EUW1_5612017679')

output = lolA.expand_champion_stats(tsData)

#%%

# a = tsData[ (tsData['type'] == 'CHAMPION_KILL') | (tsData['type'] == 'CHAMPION_SPECIAL_KILL')]



champ_dict = lolA.parse_champion_timeline_dataframe(match_id='EUW1_5612017679')

#%%

b = tsData[ (tsData['championName'] == 'Twitch')].copy()
b['time'] = b['timestamp']/1_000/60

plt.plot(b['time'],b['totalGold'])

