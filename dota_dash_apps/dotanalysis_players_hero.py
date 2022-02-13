'''
'''
import dash_bootstrap_components as dbc
import logging
import os
from dash import html, dcc
from dash.dependencies import Input, Output, State
from dash_app import app
from dota_dash_apps.dotanalysis_dash_components import style_center, style_update
from dotanalysis_control.dta import get_dota_player, register_player, heroes_dict, get_available_dota_players

################ Logging information
logger = logging.getLogger(__name__)

################ STATIC DB QUERIES
cwd = os.getcwd()
PLAYER_DIR_PATH = os.path.join(cwd, 'dota_db', 'players')
DOTA_DB = os.path.join(cwd, "dota_db")
DOTA_DB_PLAYERS = os.path.join(DOTA_DB, "players")

################ APP LAYOUT
def app_layout(player, hero):
    dota_player = get_dota_player(player)
    hero_performance = dota_player.get_hero_performance_with_players(hero, get_available_dota_players(), heroes_dict)

    hero_performance_table = dbc.Table.from_dataframe(
                                    hero_performance.sort_values("t_matches", ascending=False),
                                    dark=True, striped=True, bordered=True, hover=True)

    app_layout = html.Center(html.Div([
        dbc.Row([
            dbc.Col(
                html.H1(
                    dcc.Link(player,
                        href="https://www.opendota.com/players/"+str(dota_player.account_id))
                )
            ),
        ]),
        dbc.Row([
            dbc.Col([
                hero_performance_table
            ]),
        ]),
    ],style=style_center))
    return app_layout
