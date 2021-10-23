'''
'''
import dash_bootstrap_components as dbc
import json
import logging
import os
from dash import html, dcc
from dash.dependencies import Input, Output, State
from dota_lib.dota_player import DotaPlayer
from dash_app import app


#------------------ Logging information
logger = logging.getLogger(__name__)

#------------------ STATIC DB QUERIES
cwd = os.getcwd()
PLAYER_DIR_PATH = os.path.join(cwd, 'dota_db', 'players')
DOTA_DB = os.path.join(cwd, "dota_db")
DOTA_DB_PLAYERS = os.path.join(DOTA_DB, "players")

with open(os.path.join(cwd, "dota_db", "heroes", "heroes_dict.json")) as content:
    heroes_dict = json.load(content)

#------------------ CSS STYLES
style_center = {
    "width":"1700px",
    "max-width":"1700px",
    "display":"inline-block",
    "margin-left":"auto",
    "margin-right":"auto"
}
style_update = {
    "width":"1500px",
    "max-width":"1500px",
    "display":"inline-block",
    "margin-left":"auto",
    "margin-right":"auto"
}

#------------------ APP LAYOUT
def app_layout(player):
    dota_player = get_dota_player(player)
    win, loss = dota_player.get_winrate_info()
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
            dbc.Col(
                dbc.Button("UPDATE", id="update-btn", style=style_update, className="btn-success")
            ),
            dbc.Col(
                dbc.Fade(
                    dbc.Button("OK", className="btn-info disabled"),
                    id="fade",
                    is_in=False,
                    appear=False,
                ),
            )
        ]),
        dbc.Row([
            dbc.Col([
                html.Label("Player Name: "),
                html.Label(dota_player.player_name, id="player-name"),
            ]),
            dbc.Col([
                html.Label("Player ID: "),
                html.Label(str(dota_player.account_id), id="player-id"),
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                html.Label("Win: "),
                html.Label(str(win), id="player-win"),
            ]),
            dbc.Col([
                html.Label("Loss: "),
                html.Label(str(loss), id="player-loss"),
            ]),
        ]),
    ],style=style_center))
    return app_layout

#------------------ FUNCTIONS
def get_dota_player(player):
    player_dir = os.path.join(PLAYER_DIR_PATH, player)
    dota_player_files = [os.path.join(player_dir, file) for file in os.listdir(player_dir)]
    dota_player = DotaPlayer()
    dota_player.load_data(dota_player_files)
    return dota_player

def register_player(player_id, player_name):
    dota_player = DotaPlayer(player_id, player_name)
    if not dota_player.get_all(): return
    dota_player.save_data(DOTA_DB_PLAYERS, overwrite_data=True)

#------------------ CALLBACK DEFINITION
@app.callback(
    Output('fade', 'is_in'),
    Output('player-win', 'children'),
    Output('player-loss', 'children'),
    Input('update-btn', 'n_clicks'),
    State('fade', 'is_in'),
    State('player-win', 'children'),
    State('player-loss', 'children'),
    State('player-name', 'children'),
    State('player-id', 'children'),
)
def register_player_callback(*args):
    if args[0] is not None:
        player_name = args[4]
        player_id = args[5]
        register_player(player_id, player_name)
        dota_player = get_dota_player(player_name + "_" + player_id)
        win, loss = dota_player.get_winrate_info()
        return not args[1], win, loss
    return args[1], args[2], args[3]
