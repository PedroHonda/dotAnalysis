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

def get_dota_team(dota_team):
    dota_team_obj = []

    for player in dota_team:
        # Get DotaPlayer object per player name/ID
        dota_player = get_dota_player(player)
        dota_team_obj.append(dota_player)

    return DotaTeam(dota_team_obj)

def get_available_players():
    available_players = os.listdir(PLAYER_DIR_PATH)
    if ".gitignore" in available_players:
        available_players.remove(".gitignore")
    if available_players:
        return available_players
    else:
        return ["EMPTY"]

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
