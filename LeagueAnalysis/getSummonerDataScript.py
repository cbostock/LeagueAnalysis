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

apiKey = "RGAPI-be013ceb-17d3-445a-82fa-e1bd7bba68fk"

lolA = LeagueAnalysis(apiKey, summonerName="Moving Object 1")
