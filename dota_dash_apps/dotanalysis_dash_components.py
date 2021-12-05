'''
'''
import dash_bootstrap_components as dbc
import logging
from dash import dcc, html
from dotanalysis_control.dta import (get_available_players, get_dota_player)

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
