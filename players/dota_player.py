'''
Use data from OpenDota API (https://api.opendota.com/api/) to collect data from Dota Players
Refer to OpenDota API official documentation: https://docs.opendota.com/
'''
import json
import logging
import os
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

        logger.info("DotaPlayer created, id=%s", account_id)

    def save_data(self, output_path, overwrite_data=True):
        '''
        Save all data from DotaPlayer to self.output_path
        '''
        # Create a folder for the specific player
        player_dir = os.path.join(output_path, self.player_name+"_"+str(self.account_id))
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

    def load_data(self, dota_player_files):
        '''
        Load data from Dota Player's files given as input
        '''
        logger.debug("Loading data from files: %s", dota_player_files)
        for dota_player_file in dota_player_files:
            if os.path.basename(dota_player_file) == "player_info.json":
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

    def get_player_info(self):
        '''
        Query https://api.opendota.com/api/players/<account_id>
        Player's info
        '''
        link = "https://api.opendota.com/api/players/"+str(self.account_id)
        player_info_response = requests.get(link)
        if player_info_response.status_code != 200:
            logger.error("Error querying player info for ID %s", self.account_id)
            logger.error("Check if account ID %s is valid", self.account_id)
            return False
        self.player_info = json.loads(player_info_response.text)
        if not self.player_name:
            self.player_name = self.player_info["profile"]["personaname"]
            logger.info("Getting player_name from player_info: %s", self.player_name)
        return True

    def get_matches(self):
        '''
        Query https://api.opendota.com/api/players/<account_id>/matches
        Player's history of matches
        '''
        link = "https://api.opendota.com/api/players/"+str(self.account_id)+"/matches"
        player_matches_response = requests.get(link)
        if player_matches_response.status_code != 200:
            logger.error("Error querying player info for ID %s", self.account_id)
            logger.error("Check if account ID %s is valid", self.account_id)
            return False
        self.player_matches = json.loads(player_matches_response.text)
        return True
