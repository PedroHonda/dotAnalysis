import argparse
import logging
import os
import time
import tkinter as tk 
from tkinter import filedialog
from players.dota_player import DotaPlayer

# Logging information
TIME_TAG = time.strftime("%Y_%m_%d-%H_%M_%S")
logName = "./logs/dota_log_" + TIME_TAG + ".txt"
logging.basicConfig(filename=logName,
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname).1s\t\t%(filename)s[%(lineno)d] : %(message)s',
    datefmt='%d-%m-%y %H:%M:%S',
    filemode='w')

# Static paths
CWD = os.getcwd()
DOTA_DB = os.path.join(CWD, "dota_db")

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-new', help="get info from a new user for a given account_id")
    group.add_argument('-load', help="load player data", action='store_true')

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
        if not dota_player.get_player_info(): print("Failed to get player info")
        if not dota_player.get_matches(): print("Failed to get player's matches info")
        dota_player.save_data(DOTA_DB, overwrite_data=True)
    
if __name__ == "__main__":
    tk.Tk().withdraw()
    main()
