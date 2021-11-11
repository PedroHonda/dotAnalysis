import argparse
import logging
import os
import time
import tkinter as tk
from tkinter import filedialog
from dota_lib.dota_player import DotaPlayer
from dota_lib.dota_matches import DotaMatch

# Logging information
TIME_TAG = time.strftime("%Y_%m_%d-%H_%M_%S")
logName = "./logs/run.log"
logging.basicConfig(filename=logName,
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname).1s\t\t%(filename)s[%(lineno)d] : %(message)s',
    datefmt='%d-%m-%y %H:%M:%S',
    filemode='a')

# Static paths
CWD = os.getcwd()
DOTA_DB = os.path.join(CWD, "dota_db")
DOTA_DB_PLAYERS = os.path.join(DOTA_DB, "players")
DOTA_DB_MATCHES = os.path.join(DOTA_DB, "matches")

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-new', help="get info from a new user for a given account_id")
    group.add_argument('-load', help="load player data", action='store_true')
    group.add_argument('-new_match', help="get info from a new match for a given match_id")

    parser.add_argument('-name', help="player's name")

    args = parser.parse_args()
    if args.name: player_name = args.name
    else: player_name = "Player_"+TIME_TAG

    if args.load:
        dota_player_files = filedialog.askopenfilenames(
            filetypes=(("Dota Player JSON data", ".json"),),
            title="Select the Dota Player's JSON Data you want to load")
        dota_player = DotaPlayer()
        dota_player.load_data(dota_player_files)
    elif args.new:
        account_id = str(args.new).replace("None","")
        dota_player = DotaPlayer(account_id, player_name)
        if not dota_player.get_all(): print("Failed to get player info")
        dota_player.save_data(DOTA_DB_PLAYERS, overwrite_data=True)
    elif args.new_match:
        match_id = str(args.new_match).replace("None","")
        dota_match = DotaMatch(match_id)
        if not dota_match.get_match_info(): print("Failed to get match info")
        dota_match.save_data(DOTA_DB_MATCHES)

if __name__ == "__main__":
    tk.Tk().withdraw()
    main()
