# -*- coding: utf-8 -*-
"""
Created on Sun Dec 12 10:05:10 2021

@author: Chris
"""

from LeagueAnalysis import LeagueAnalysis

#%%

apiKey = "RGAPI-b0201a7b-93b7-48e4-a2d0-e162150cd6c7"

lolA = LeagueAnalysis(apiKey, summonerName="Moving Object 2")

df = lolA.create_mastery_table()
print(df)


#%%

tsData = lolA.create_champion_timeline_dataframe("EUW1_5612017679")
print(tsData )

tsData_expanded = lolA.expand_champion_stats(tsData)
print()
