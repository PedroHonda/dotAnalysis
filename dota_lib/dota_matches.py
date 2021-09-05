'''
Use data from OpenDota API (https://api.opendota.com/api/) to collect data from Dota Matches
Refer to OpenDota API official documentation: https://docs.opendota.com/
'''
import json
import logging
import os
import requests
from datetime import datetime as dtm

logger = logging.getLogger(__name__)

class DotaMatch:
    '''
    DotaMatch class to gather and analyze data from a specific match
    '''
    def __init__(self, match_id):
        self.match_id = str(match_id)
        self.match_info = []

        logger.info("DotaMatch created, id=%s", match_id)

    def save_data(self, output_path):
        '''
        '''
        # Create a folder for the specific match
        match_dir = os.path.join(output_path, self.match_id)
        if not os.path.isdir(match_dir):
            os.mkdir(match_dir)

        # Save match_info if available
        if self.match_info:
            file_path = os.path.join(match_dir, "match_info.json")
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(self.match_info, file, ensure_ascii=False, indent=4)

    def load_data(self, dota_match_files):
        '''
        Load data from Dota Match's files given as input
        '''
        logger.debug("Loading data from files: %s", dota_match_files)
        for dota_match_file in dota_match_files:
            if os.path.basename(dota_match_file) == "match_info.json":
                with open(dota_match_file) as content:
                    self.match_info = json.load(content)
                logger.info("match_info.json loaded successfully!")

    def get_match_info(self):
        '''
        Query https://api.opendota.com/api/matches/<match_id>
        '''
        if self.match_id:
            link = "https://api.opendota.com/api/matches/"+str(self.match_id)
            mtach_response = requests.get(link)
            if mtach_response.status_code != 200:
                logger.error("Error querying mtach for ID %s", self.match_id)
                logger.error("Check if match ID %s is valid", self.match_id)
                return False
            self.match_info = json.loads(mtach_response.text)
            return True
