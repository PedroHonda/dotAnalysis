'''
DotaTeam class that groups up to 5 DotaPlayer objects to gather information about
the team as a whole, e.g. winrate together
'''
import logging
from dota_lib.dota_player import DotaPlayer

logger = logging.getLogger(__name__)

class DotaTeam:
    '''
    DotaPlayer class to gather and analyze data from a specific player
    '''
    def __init__(self, dota_team=None):
        if not dota_team:
            self.dota_team = []
            self.matches = []
            # Temporary list to be logged later on
            players = []
        elif isinstance(dota_team, list):
            if len(dota_team) > 5:
                logger.error("Only up to 5 players supported")
                raise IndexError("dota_team only support up to 5 players")
            # Loop through players to check if they are all DotaPlayer objects
            for dota_player in dota_team:
                if not isinstance(dota_player, DotaPlayer):
                    logger.error("Dota Player %s is not a DotaPlayer object", dota_player)
                    raise TypeError("dota_team list must contain only DotaPlayer objects")
            players = [player.player_name for player in dota_team]
            self.dota_team = dota_team
            self.matches = self.get_team_simplified_matches()
            self.winrate = self.get_team_winrate()
        else:
            raise TypeError("dota_team should either be None/null or a list of DotaPlayer")

        logger.info("DotaTeam created: %s", players)

    def add_player(self, dota_player):
        '''
        Add a dota player to the team
        '''
        if len(self.dota_team) == 5:
            logger.error("DotaTeam is full (5 players), need remove one player to add more")
            raise IndexError("Dota Team is already full")
        elif not isinstance(dota_player, DotaPlayer):
            logger.error("dota_player is not a DotaPlayer object")
            raise TypeError("dota_player is not a DotaPlayer object")
        else:
            self.dota_team.append(dota_player)
            logger.info("Dota Player %s added to the team", dota_player.player_name)
            self.matches = self.get_team_simplified_matches()
            logger.info("Team's matches updated")
            self.winrate = self.get_team_winrate()
            logger.info("Team's winrate updated")
    
    def get_team_simplified_matches(self):
        '''
        Use current dota_team's players info to generate a list of matches with key information:
        - "match_id" : match ID
        - "date" : <year>-<month>-<day> in a string format
        - "side" : either 'radiant' or 'dire'
        - "win" : 0 = lose; 1 = win
        '''
        logger.info("get_team_simplified_matches requested...")
        # If there is no dota_player, return empty list
        if not self.dota_team:
            logger.info("dota_team is empty, returning empty match list")
            return []
        logger.debug("Current DotaTeam: %s", [player.player_name for player in self.dota_team])
        # Start using first player's matches as a base
        simplified_matches = self.dota_team[0].simplified_matches()
        # If only one player is available, return simplified_matches
        if len(self.dota_team) == 1: return simplified_matches
        # Parsing matches to get only matches as a team
        team_matches = [(entry["match_id"], entry["side"]) for entry in simplified_matches]
        for dota_player in self.dota_team[1:]:
            aux_simpl_matches = dota_player.simplified_matches()
            player_matches = [(entry["match_id"], entry["side"]) for entry in aux_simpl_matches]
            intersection_matches = set(team_matches).intersection(set(player_matches))
            team_matches = list(intersection_matches)
        team_matches_id = [match[0] for match in team_matches]
        # Reformulating simplified_matches to only consider team matches
        simplified_matches_final = []
        for match in simplified_matches:
            if match["match_id"] in team_matches_id:
                match["hero"] = "---"
                match["kda"] = "---"
                simplified_matches_final.append(match)
        return simplified_matches_final

    def get_team_winrate(self):
        '''
        Require self.matches to be populated
        Returns winrate %
        '''
        # If self.matches is not populated, return 0.0
        if not self.matches: return 0.0
        n_of_matches = len(self.matches)
        win_matches = sum([result["win"] for result in self.matches])
        winrate = 100*win_matches/n_of_matches
        logger.debug("Dota Team winrate: %s", winrate)

        return winrate
