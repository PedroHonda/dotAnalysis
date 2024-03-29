'''
Use data from OpenDota API (https://api.opendota.com/api/) to collect data from Dota Players
Refer to OpenDota API official documentation: https://docs.opendota.com/
'''
import json
import logging
import os
import time
import pandas as pd
from datetime import datetime as dtm
import requests

logger = logging.getLogger(__name__)

class DotaPlayer:
    '''
    DotaPlayer class to gather and analyze data from a specific player
    '''
    def __init__(self, account_id="", player_name=""):
        self.account_id = account_id
        self.player_name = player_name
        self.player_info = []
        self.player_matches = []
        self.player_wardmap = []
        self.player_wordcloud = []
        self.data_info = {}

        logger.info("DotaPlayer created, id=%s", account_id)

    def __repr__(self) -> str:
        return "DotaPlayer('{}', '{}')".format(self.account_id, self.player_name)

    def __str__(self) -> str:
        return "{} - {}".format(self.account_id, self.player_name)

    def __len__(self) -> int:
        return len(self.player_matches)

    def save_data(self, output_path, overwrite_data=True):
        '''
        Save all data from DotaPlayer to self.output_path
        '''
        # Create a folder for the specific player
        player_dir = os.path.join(output_path,
            self.player_name.replace(" ", "_")+"_"+str(self.account_id))
        if not os.path.isdir(player_dir):
            os.mkdir(player_dir)
        elif os.path.isdir(player_dir) and not overwrite_data:
            logger.info("Player dir %s already exists and overwrite_data is %s, so skip save_data",
                player_dir, overwrite_data)
            return

        # Save player_info if available
        if self.player_info:
            file_path = os.path.join(player_dir, "player_info.json")
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(self.player_info, file, ensure_ascii=False, indent=4)

        # Save player_matches if available
        if self.player_matches:
            file_path = os.path.join(player_dir, "player_matches.json")
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(self.player_matches, file, ensure_ascii=False, indent=4)

        # Save player_wardmap if available
        if self.player_wardmap:
            file_path = os.path.join(player_dir, "player_wardmap.json")
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(self.player_wardmap, file, ensure_ascii=False, indent=4)

        # Save player_wordcloud if available
        if self.player_wordcloud:
            file_path = os.path.join(player_dir, "player_wordcloud.json")
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(self.player_wordcloud, file, ensure_ascii=False, indent=4)

        # Save data_info if available
        if self.data_info:
            file_path = os.path.join(player_dir, "data_info.json")
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(self.data_info, file, ensure_ascii=False, indent=4)

    def load_data_path(self, dota_player_files_path):
        '''
        Load data from Dota Player's files inside given dota_player_files_path
        '''
        logger.info("load_data_path called for path %s", dota_player_files_path)
        self.load_data(os.listdir(dota_player_files_path))

    def load_data(self, dota_player_files):
        '''
        Load data from Dota Player's files given as input
        '''
        logger.info("Loading data from files: %s", dota_player_files)
        for dota_player_file in dota_player_files:
            if os.path.basename(dota_player_file) == "player_info.json":
                logger.debug(dota_player_file)
                with open(dota_player_file) as content:
                    self.player_info = json.load(content)
                self.account_id = self.player_info["profile"]["account_id"]
                self.player_name = self.player_info["profile"]["personaname"]
                logger.info("player_info.json loaded successfully!")
                logger.debug("Player Info: account_id=%s, player_name=%s",
                    self.account_id, self.player_name)
            elif os.path.basename(dota_player_file) == "player_matches.json":
                with open(dota_player_file) as content:
                    self.player_matches = json.load(content)
                logger.info("player_matches.json loaded successfully!")
            elif os.path.basename(dota_player_file) == "player_wardmap.json":
                with open(dota_player_file) as content:
                    self.player_wardmap = json.load(content)
                logger.info("player_wardmap.json loaded successfully!")
            elif os.path.basename(dota_player_file) == "player_wordcloud.json":
                with open(dota_player_file) as content:
                    self.player_wordcloud = json.load(content)
                logger.info("player_wordcloud.json loaded successfully!")
            elif os.path.basename(dota_player_file) == "data_info.json":
                with open(dota_player_file) as content:
                    self.data_info = json.load(content)
                logger.info("data_info.json loaded successfully!")

    def get_player_info(self):
        '''
        Query https://api.opendota.com/api/players/<account_id>
        Player's info
        '''
        link = "https://api.opendota.com/api/players/"+str(self.account_id)
        player_info_response = requests.get(link)
        if player_info_response.status_code == 429:
            logger.warning("HTTP error 429 received, waiting 70 seconds...")
            time.sleep(70)
            logger.info("70 seconds timer expired, trying to query data again")
            player_info_response = requests.get(link)
        if player_info_response.status_code != 200:
            logger.error("Error querying player info for ID %s", self.account_id)
            logger.error("Check if account ID %s is valid", self.account_id)
            return False
        self.player_info = json.loads(player_info_response.text)
        if not self.player_name:
            self.player_name = self.player_info["profile"]["personaname"]
            logger.info("Getting player_name from player_info: %s", self.player_name)
        self.data_info["Last Updated"] = time.strftime("%Y-%m-%d")
        return True

    def get_matches(self):
        '''
        Query https://api.opendota.com/api/players/<account_id>/matches
        Player's history of matches
        '''
        link = "https://api.opendota.com/api/players/"+str(self.account_id)+"/matches"
        player_matches_response = requests.get(link)
        if player_matches_response.status_code == 429:
            logger.warning("HTTP error 429 received, waiting 70 seconds...")
            time.sleep(70)
            logger.info("70 seconds timer expired, trying to query data again")
            player_matches_response = requests.get(link)
        if player_matches_response.status_code != 200:
            logger.error("Error querying player info for ID %s", self.account_id)
            logger.error("Check if account ID %s is valid", self.account_id)
            return False
        self.player_matches = json.loads(player_matches_response.text)
        self.data_info["Last Updated"] = time.strftime("%Y-%m-%d")
        return True

    def get_wardmap(self):
        '''
        Query https://api.opendota.com/api/players/<account_id>/wardmap
        Player's history of wardmap
        '''
        link = "https://api.opendota.com/api/players/"+str(self.account_id)+"/wardmap"
        player_wardmap_response = requests.get(link)
        if player_wardmap_response.status_code == 429:
            logger.warning("HTTP error 429 received, waiting 70 seconds...")
            time.sleep(70)
            logger.info("70 seconds timer expired, trying to query data again")
            player_wardmap_response = requests.get(link)
        if player_wardmap_response.status_code != 200:
            logger.error("Error querying player wardmap for ID %s", self.account_id)
            logger.error("Check if account ID %s is valid", self.account_id)
            return False
        self.player_wardmap = json.loads(player_wardmap_response.text)
        self.data_info["Last Updated"] = time.strftime("%Y-%m-%d")
        return True

    def get_wordcloud(self):
        '''
        Query https://api.opendota.com/api/players/<account_id>/wordcloud
        Player's history of wordcloud
        '''
        link = "https://api.opendota.com/api/players/"+str(self.account_id)+"/wordcloud"
        player_wordcloud_response = requests.get(link)
        if player_wordcloud_response.status_code == 429:
            logger.warning("HTTP error 429 received, waiting 70 seconds...")
            time.sleep(70)
            logger.info("70 seconds timer expired, trying to query data again")
            player_wordcloud_response = requests.get(link)
        if player_wordcloud_response.status_code != 200:
            logger.error("Error querying player wordcloud for ID %s", self.account_id)
            logger.error("Check if account ID %s is valid", self.account_id)
            return False
        self.player_wordcloud = json.loads(player_wordcloud_response.text)
        self.data_info["Last Updated"] = time.strftime("%Y-%m-%d")
        return True

    def get_all(self):
        '''
        Combined method of all GET data methods available
        '''
        if not self.get_player_info():
            return False
        if not self.get_matches():
            return False
        if not self.get_wardmap():
            return False
        if not self.get_wordcloud():
            return False
        self.data_info["Last Updated"] = time.strftime("%Y-%m-%d")
        return True

    def simplified_matches(self, hero_dict=None):
        '''
        Based on self.player_matches return a list with:
        - "match_id" : match ID
        - "date" : <year>-<month>-<day> in a string format
        - "kda" : <kill>/<death>/<assist> in a string format
        - "hero" : in case hero_dict is provided, translate ID to hero's name
        - "side" : either 'radiant' or 'dire'
        - "win" : 0 = lose; 1 = win
        '''
        hero_dict = hero_dict or {}
        simplified = []
        if self.player_matches:
            for match in self.player_matches:
                # Skip games that are not "All Pick"
                if match["game_mode"] not in (1, 22):
                    continue
                entry = {}
                entry["match_id"] = match["match_id"]
                entry["date"] = dtm.fromtimestamp(match["start_time"])
                entry["kda"] = str(match["kills"])
                entry["kda"] += "/"+str(match["deaths"])
                entry["kda"] += "/"+str(match["assists"])
                entry["hero"] = hero_dict.get(str(match["hero_id"]), str(match["hero_id"]))
                # "player_slot" > 127 : Dire
                # "player_slot" < 128 : Radiant
                if match["player_slot"] > 127:
                    entry["side"] = "dire"
                else:
                    entry["side"] = "radiant"
                if entry["side"] == "radiant" and match["radiant_win"]:
                    entry["win"] = 1
                elif entry["side"] == "dire" and not match["radiant_win"]:
                    entry["win"] = 1
                else:
                    entry["win"] = 0
                simplified.append(entry)
        return simplified

    def simplified_matches_df(self, hero_dict=None):
        '''
        Based on self.player_matches return a Pandas DataFrame with:
        - pd.DataFrame(data, columns)
        -- data : list(zip(match_id, date, kda, hero, side, win))
        -- columns : ["match_id", "date", "kda", "hero", "side", "win"]
        --- "match_id" : match ID
        --- "date" : <year>-<month>-<day> in a string format
        --- "kda" : <kill>/<death>/<assist> in a string format
        --- "hero" : in case hero_dict is provided, translate ID to hero's name
        --- "side" : either 'radiant' or 'dire'
        --- "win" : 0 = lose; 1 = win
        '''
        hero_dict = hero_dict or {}
        match_id, date, kda, hero, side, win = [], [], [], [], [], []
        if self.player_matches:
            for match in self.player_matches:
                # Skip games that are not "All Pick"
                if match["game_mode"] not in (1, 22):
                    continue
                entry = {}
                match_id.append(match["match_id"])
                date.append(dtm.fromtimestamp(match["start_time"]))
                kda.append(str(match["kills"])+"/"+str(match["deaths"])+"/"+str(match["assists"]))
                hero.append(hero_dict.get(str(match["hero_id"]), str(match["hero_id"])))
                # "player_slot" > 127 : Dire
                # "player_slot" < 128 : Radiant
                if match["player_slot"] > 127:
                    side.append("dire")
                else:
                    side.append("radiant")
                if side[-1] == "radiant" and match["radiant_win"]:
                    win.append(1)
                elif side[-1] == "dire" and not match["radiant_win"]:
                    win.append(1)
                else:
                    win.append(0)
        simplified = pd.DataFrame(list(zip(match_id, date, kda, hero, side, win)),
                                  columns=["match_id", "date", "kda", "hero", "side", "win"])
        return simplified

    def get_winrate_info(self):
        '''
        Requires player_matches
        '''
        win = 0
        loss = 0
        if self.player_matches:
            for match in self.player_matches:
                # "player_slot" > 127 : Dire
                # "player_slot" < 128 : Radiant
                if match["player_slot"] > 127 and not match["radiant_win"]:
                    win += 1
                elif match["player_slot"] <= 127 and match["radiant_win"]:
                    win += 1
                else:
                    loss += 1
            return win, loss
        return 0, 0

    def get_hero_performance(self, heroes_dict=None):
        '''
        '''
        logger.info("get_hero_performance called")
        heroes_dict = heroes_dict or {}

    def get_hero_performance_with_players(self, hero, players, heroes_dict=None):
        '''
        Input:
        - hero (str|int) : it can be either the hero name or hero ID
        - players : list of DotaPlayer
        
        Output:
        - pd.DataFrame(data, columns)
        -- data : list(zip(player_id, t_matches, win, winrate))
        -- columns : ["player_id", "t_matches", "win", "winrate"]
        --- "player_id" : player ID
        --- "t_matches" : total matches
        --- "win" : total matches won
        --- "winrate" : winrate
        '''
        logger.info("get_hero_performance_with_players called")
        logger.debug("  for hero %s, players = %s", hero, players)
        heroes_dict = heroes_dict or {}

        if not isinstance(players, list):
            logger.error("ERROR! players is not a list!")
            return pd.DataFrame()

        hero_dict_id = {}
        if isinstance(hero, str):
            if hero not in heroes_dict:
                hero_dict_id =  {y.replace(" ", "_").replace("-", "_").lower():x
                                for x,y in heroes_dict.items()}
                hero = hero.replace(" ", "_").replace("-", "_").lower()
                if hero in hero_dict_id:
                    hero_id = hero_dict_id[hero.replace(" ", "_").replace("-", "_").lower()]
                else:
                    logger.debug("Couldn't find %s in %s",
                                hero.replace(" ", "_").replace("-", "_").lower(),
                                hero_dict_id)
                    hero_id = hero
        elif isinstance(hero, int):
            hero_id = str(hero)
        else:
            logger.error("ERROR! Hero provided must be either int or str!")
            return pd.DataFrame()

        if self.player_matches:
            simplified_matches = self.simplified_matches_df()
            flt = simplified_matches['hero'].isin([hero_id])
            matches_hero_match_id = simplified_matches[flt]["match_id"].tolist()
            matches_hero_win = simplified_matches[flt]["win"].tolist()
            matches_hero = dict(zip(matches_hero_match_id, matches_hero_win))

            player_id, t_matches, win, winrate = [], [], [], []

            try:
                for player in players:
                    player_matches_id = [match["match_id"] for match in player.player_matches]
                    intersec = list(set(matches_hero_match_id) & set(player_matches_id))
                    if not intersec:
                        continue
                    player_id.append(player.player_name+"_"+str(player.account_id))
                    win.append(0)
                    t_matches.append(0)
                    for match_id in intersec:
                        t_matches[-1]+=1
                        if matches_hero[match_id]:
                            win[-1]+=1
                    winrate.append(win[-1]/t_matches[-1])
                return pd.DataFrame(list(zip(player_id, t_matches, win, winrate)),
                                            columns=["player_id", "t_matches", "win", "winrate"])
            except ZeroDivisionError:
                logger.exception("ERROR! calculating data for player %s", player)
                logger.debug("matches_hero_match_id : %s", matches_hero_match_id)
        else:
            logger.error("ERROR! self.matches is not populated!")
            return pd.DataFrame()
