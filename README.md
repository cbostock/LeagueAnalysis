# LeagueAnalysis

![](https://img.shields.io/pypi/status/ansicolortags.svg)   ![](https://img.shields.io/pypi/l/ansicolortags.svg) ![](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)  ![](https://img.shields.io/badge/Made%20with%20-Anaconda-limegreen) ![](https://img.shields.io/badge/code%20style-black-black.svg)

### About the project 
Pre-curer: this project was more of a self-developing journey of how to develop conventional python code.  In this project I wanted to utilise a lightweight NoSql database, TinyDB (for learning purposes).  This project was also developed with the use of Anaconda.

The aim of the project was to retrieve data from riots api for the league of legends match, and mastery data qnd format the data into an easy manageable data structures, namely pandas within DataFrames. I am aware of other projects which were developed for primarily retrieve data from riots endpoints such as [RiotWatcher](https://riot-watcher.readthedocs.io/en/latest/).  However, as this project was for developing my own skills I decided to create the requests myself. 

### Obtaining data.

Using your own API key, the key below is for demonstration purposes and has exired you can, using the following section will return the champion mastery DataFrame for the given summoner name.

	import pandas as pd
	from LeagueAnalysis import LeagueAnalysis

	# API key
	api_key = "RGAPI-b0201a7b-93b7-48e4-a2d0-e162150cd6c7"

	# create object 
	lolA = LeagueAnalysis(api_key, summonerName="Moving Object 2")

	# retrieve mastery list
	df = lolA.create_mastery_table()

Here, df is the DataFrame containing all mastery list information, including the last time played.  Any information which could be potentially used again, such as summoner information (id, puuid etc.) will be stored locally within a database. 

A more comprehensive example can be seen within the Example Notebook. 
 
# Example notebook
 [![Made withJupyter](https://img.shields.io/badge/Made%20with-Jupyter-orange?style=for-the-badge&logo=Jupyter)](https://jupyter.org/try)  
Within the folder LeagueAnalysis there is an example notebook named "[example notebook.ipynb](https://github.com/cbostock/LeagueAnalysis/blob/main/LeagueAnalysis/example%20notebook.ipynb)."  Many of the methods can be seen in use here in addition of how to plot the returned KPI's from riot.  One example is plotting total gold for the champions in the "bottom" role.  Another example plots the minions killed for the last five games for a given summoner name. 

# Requirements

- requests
- pandas
- numpy
- [TinyDB](https://pypi.org/project/tinydb/) ( [Anaconda](https://anaconda.org/conda-forge/tinydb) ) 

# References
- [Riot's API](https://developer.riotgames.com/)
- [TinyDB](https://pypi.org/project/tinydb/) ( [Anaconda](https://anaconda.org/conda-forge/tinydb) ) 

