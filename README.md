# dotAnalysis
Created by Pedro Honda
July 17th, 2021

## Apps

- `dotanalysis_home` : Home Page
  - Register New players
  - Check available players
  - Update all players' data

- `dotanalysis_team` : DotaTeam analysis
  - Returns winrate per hero for the given team
  - Plot monthly winrates by player or by team
  - Clickable graph to displayed detailed matches' info
  - Provides general information for the team (Dire/Radiant Winrate, etc.)

## Bootstrap

- https://bootswatch.com/darkly/

## How-to

1. Install requirements.txt
   - `python -m pip install -r requirements_plain.txt` or `pip install requirements_plain.txt`
2. Run `dotanalysis_index.py`
   - `python dotanalysis_index.py`

## Heroku

This app is deployed here: https://dotanalysis.herokuapp.com/team

For simplicity, the Heroku app will not provide the ability to register new players or update existing ones.

I will update it from time to time though.
