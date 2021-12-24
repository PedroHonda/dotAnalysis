'''
'''
import dash_bootstrap_components as dbc
import logging
from dash import dcc, html
from dotanalysis_control.dta import (get_available_players, get_dota_player, get_dota_team,
                                     heroes_dict)

################ Logging information
logger = logging.getLogger(__name__)

style_center = {
    "width":"1700px",
    "max-width":"1700px",
    "display":"inline-block",
    "margin-left":"auto",
    "margin-right":"auto"
}
style_update = {
    "width":"700px",
    "max-width":"700px",
    "display":"inline-block",
    "margin-left":"auto",
    "margin-right":"auto"
}
style_logo = {
    "width":"100px",
    "max-width":"100px",
}
style_register_box = {
    "width":"800px",
    "margin-left":"auto",
    "margin-right":"auto"
}

def players_table():
    t_header = ["Player", "Last Updated"]
    players_table_header = [
        html.Thead(html.Tr([html.Th(h) for h in t_header]))
    ]
    rows = []
    dota_players = get_available_players()
    if dota_players == ["EMPTY"]:
        return []
    for player in dota_players:
        dota_player = get_dota_player(player)
        rows.append(html.Tr([
            html.Td(dcc.Link(player, href="/players/"+player)),
            html.Td(dota_player.data_info["Last Updated"]),
        ]))
    players_table_body = [html.Tbody(rows)]
    players_table = dbc.Table(players_table_header + players_table_body,
        bordered=True,
        dark=True,
        hover=True,
        responsive=True,
        striped=True,)
    return players_table

def get_players_data(dota_team):
    dota_team_obj = get_dota_team(dota_team)

    most_played_heroes_list = dota_team_obj.get_most_played_heroes_df(heroes_dict)
    player_data = [[], [], [], [], []]
    for idx, player in enumerate(dota_team):
        player_data[idx].append(dcc.Markdown(f"#### {player}"))

    for idx, mph_df in enumerate(most_played_heroes_list):
        most_played_heroes_tables = dbc.Table.from_dataframe(mph_df,
                                                             dark=True,
                                                             striped=True,
                                                             bordered=True,
                                                             hover=True)
        player_data[idx].append(most_played_heroes_tables)

    return player_data

def get_team_info(dota_team):
    dota_team_obj = get_dota_team(dota_team)
    wins = sum([result["win"] for result in dota_team_obj.matches])
    losses = len(dota_team_obj.matches) - wins
    team_info = ["Wins: "+str(wins), html.Br(), "Losses: "+str(losses), html.Br()]
    radiant_winrate, radiant_matches = dota_team_obj.get_team_radiant_winrate_matches()
    radiant_winrate = "{:10.2f}".format(radiant_winrate)
    dire_winrate, dire_matches = dota_team_obj.get_team_dire_winrate_matches()
    dire_winrate = "{:10.2f}".format(dire_winrate)
    team_info.append("Radiant Winrate: "+str(radiant_winrate)+"%, Matches: "+str(radiant_matches))
    team_info.append(html.Br())
    team_info.append("Dire Winrate: "+str(dire_winrate)+"%, Matches: "+str(dire_matches))
    team_info.append(html.Br())
    return team_info

def get_monthly_matches_data(dota_team, date):
    monthly_matches_data = []
    if dota_team:
        dota_team_obj = get_dota_team(dota_team)
        team_matches_month_df = dota_team_obj.get_monthly_matches_df(date)

        if not team_matches_month_df.empty:
            month = date.strftime("%B")
            monthly_matches_data.append(
                dcc.Markdown(f"#### Monthly matches - {month} {str(date.year)}")
            )
            team_matches_month_table = dbc.Table.from_dataframe(
                                    team_matches_month_df,
                                    dark=True, striped=True, bordered=True, hover=True)

            # thead = team_matches_month_table.children[0].children
            tbody = team_matches_month_table.children[1].children

            for tr_row in tbody:
                td = tr_row.children[0].children
                match_id_link = "https://www.opendota.com/matches/"+str(td)
                tr_row.children[0].children = dcc.Link(match_id_link, href=match_id_link)

            monthly_matches_data.append(team_matches_month_table)
            return monthly_matches_data

    return []
