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
            players = []
        elif isinstance(dota_team, list):
            if len(dota_team) > 5:
                raise IndexError("dota_team only support up to 5 players")
            for dota_player in dota_team:
                if not isinstance(dota_player, DotaPlayer):
                    logger.debug("Dota Player %s is not a DotaPlayer object", dota_player)
                    raise TypeError("dota_team list must contain only DotaPlayer objects")
            players = [player.player_name for player in dota_team]
            self.dota_team = dota_team
        else:
            raise TypeError("dota_team should either be None/null or a list of DotaPlayer")

        logger.info("DotaTeam created: %s", players)

    def add_player(self, dota_player):
        '''
        Add a dota player to the team
        '''
        if len(self.dota_team) == 5:
            raise IndexError("Dota Team is already full")
        elif not isinstance(dota_player, DotaPlayer):
            raise TypeError("dota_player is not a DotaPlayer object")
        else:
            self.dota_team.append(dota_player)
            logger.info("Dota Player %s added to the team", dota_player.player_name)
    
    def get_team_simplified_matches(self, hero_dict=None):
        '''
        '''
        # If there is no dota_player, return empty list
        if not self.dota_team: return []
        # Start using first player's matches as a base
        simplified_matches = self.dota_team[0].simplified_matches(hero_dict)
        # If only one player is available, return simplified_matches
        if len(self.dota_team) == 1: return simplified_matches
        # Parsing matches to get only matches as a team
        team_matches = [(entry["match_id"], entry["side"]) for entry in simplified_matches]
        for dota_player in self.dota_team[1:]:
            aux_simpl_matches = dota_player.simplified_matches(hero_dict)
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
