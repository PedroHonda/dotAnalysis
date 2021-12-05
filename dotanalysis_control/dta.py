'''
Management of files using DotaPlayer and DotaTeam objects
'''
import json
import logging
import os
import pandas as pd
import plotly.graph_objects as go
import threading
from datetime import datetime as dtm
from dota_lib.dota_player import DotaPlayer
from dota_lib.dota_team import DotaTeam

logger = logging.getLogger(__name__)
cwd = os.getcwd()
PLAYER_DIR_PATH = os.path.join(cwd, 'dota_db', 'players')
DOTA_DB = os.path.join(cwd, "dota_db")
DOTA_DB_PLAYERS = os.path.join(DOTA_DB, "players")

with open(os.path.join(cwd, "dota_db", "heroes", "heroes_dict.json")) as content:
    heroes_dict = json.load(content)

def get_dota_player(player):
    player_dir = os.path.join(PLAYER_DIR_PATH, player)
    dota_player_files = [os.path.join(player_dir, file) for file in os.listdir(player_dir)]
    dota_player = DotaPlayer()
    dota_player.load_data(dota_player_files)
    return dota_player

def get_available_players():
    available_players = os.listdir(PLAYER_DIR_PATH)
    available_players.remove(".gitignore")
    return available_players

def register_player(player_id, player_name):
    dota_player = DotaPlayer(player_id, player_name)
    if not dota_player.get_all(): return
    dota_player.save_data(DOTA_DB_PLAYERS, overwrite_data=True)

def update_all(queue=None):
    update_all_thread = threading.Thread(target=update_all_t, kwargs={'queue':queue})
    update_all_thread.start()

def update_all_t(queue=None):
    available_players = get_available_players()
    progress_aux_old = 0
    available_players_length = len(available_players)
    for idx, players in enumerate(available_players):
        split = players.split("_")
        id = split[-1]
        name = "_".join(split[:-1])
        register_player(id, name)
        progress_aux = int((100 * idx) / available_players_length)
        if progress_aux > progress_aux_old and progress_aux <= 100:
            if queue:
                queue.put(progress_aux)
            progress_aux_old = progress_aux
    if queue:
        queue.put(("status", "finished"))

def get_team_simplified_matches_df(dota_team):
    simplified_matches = dota_team.matches
    sdf = pd.DataFrame(simplified_matches)
    sdf.index = sdf.date
    sdf["match"]=1
    return sdf

def get_winrate_fig_by_team(team, dota_team_obj):
    dota_team = []
    available_players = get_available_players()
    for dota_player in team:
        dota_player = dota_player.replace("_team", "")
        if dota_player in ("<Empty>", "All"): continue
        if dota_player in available_players: dota_team.append(dota_player)

    layout = go.Layout(uirevision = 'value', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig = go.Figure(layout = layout)

    if not dota_team: return fig, 0.0

    for idx, player in enumerate(dota_team):
        dota_player = get_dota_player(player)
        dota_team[idx] = dota_player

    dota_team_obj = DotaTeam(dota_team)
    sdf = get_team_simplified_matches_df(dota_team_obj)
    sdf_month = sdf[["win", "match"]].groupby([lambda x: x.year, lambda x: x.month]).sum()
    sdf_month["winrate"] = 100*sdf_month.win/sdf_month.match
    month = [dtm(date[0], date[1], 1) for date in sdf_month.index]
    fig.add_trace(go.Scatter(x=month, y=sdf_month.winrate))
    fig.layout.xaxis.color = 'white'
    fig.layout.yaxis.color = 'white'

    return fig, dota_team_obj.winrate
