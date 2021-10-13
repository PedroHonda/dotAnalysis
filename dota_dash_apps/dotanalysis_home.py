'''
'''
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import json
import logging
import os
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

dota_players = os.listdir(PLAYER_DIR_PATH)
dota_players.remove(".gitignore")

#------------------ FUNCTIONS
def get_dota_player(player):
    player_dir = os.path.join(PLAYER_DIR_PATH, player)
    dota_player_files = [os.path.join(player_dir, file) for file in os.listdir(player_dir)]
    dota_player = DotaPlayer()
    dota_player.load_data(dota_player_files)
    return dota_player

def get_available_players():
    available_players = os.listdir(PLAYER_DIR_PATH)
    available_players.remove(".gitignore")
    return available_players

def register_player(player_id, player_name):
    dota_player = DotaPlayer(player_id, player_name)
    if not dota_player.get_all(): return
    dota_player.save_data(DOTA_DB_PLAYERS, overwrite_data=True)

def update_all():
    available_players = get_available_players()
    for players in available_players:
        split = players.split("_")
        id = split[-1]
        name = "_".join(split[:-1])
        register_player(id, name)
    return True

#------------------ DASH MODULES
### Players Table
t_header = ["Player", "Last Updated"]
players_table_header = [
    html.Thead(html.Tr([html.Th(h) for h in t_header]))
]
rows = []
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
def app_layout():
    app_layout = html.Center(html.Div([
        dbc.Row(
            dbc.Card([
                dbc.CardHeader("Register a New Player", className="card-body"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(
                            dbc.InputGroup([
                                dbc.InputGroupAddon("Player ID", addon_type="prepend"),
                                dbc.Input(placeholder="", id='player-id', style={'color': 'white'}),
                            ]),
                        ),
                        dbc.Col(
                            dbc.InputGroup([
                                dbc.InputGroupAddon("Player Name", addon_type="prepend"),
                                dbc.Input(placeholder="(optional)", id='player-name', style={'color': 'white'}),
                            ]),
                        ),
                    ]),
                    html.Br(),
                    dbc.Row(
                        dbc.Button("REGISTER",
                            id="register-player",
                            color="primary",
                            className="mr-1"
                        )
                    )
                ]),
            ], className="card text-white mb-3", color="bg-primary")
        ),
        html.Br(),
        dbc.Row(
            dbc.Button("Available Players",
                id="available-players",
                color="primary",
                className="mr-1"
            )
        ),
        html.Br(),
        dbc.Row(
            html.Div(
                dbc.Collapse(
                    children=players_table,
                    id="players-collapse",
                    is_open=False,
                )
            ),
        ),
        html.Br(),
        dbc.Row([
            dbc.Col(
                dbc.Button("UPDATE ALL PLAYERS", id="update-all", style=style_update, className="btn-success")
            ),
            dbc.Col(
                dbc.Fade(
                    dbc.Button("OK", className="btn-info disabled"),
                    id="ok-fade",
                    is_in=False,
                    appear=False,
                ),
            )
        ]),
    ],style=style_center))
    return app_layout

#------------------ CALLBACK DEFINITION
@app.callback(
    Output('player-id', 'value'),
    Output('player-name', 'value'),
    Input('register-player', 'n_clicks'),
    Input('player-id', 'value'),
    Input('player-name', 'value'),
)
def register_player_callback(register, player_id, player_name):
    if register is not None:
        register_player(player_id, player_name)
        return "", ""
    return player_id, player_name

@app.callback(
    Output('players-collapse', 'is_open'),
    Input('available-players', 'n_clicks'),
    State('players-collapse', 'is_open')
)
def update_output(available_players, players_collapse):
    if available_players is not None:
        return not players_collapse
    else:
        return False

@app.callback(
    Output('ok-fade', 'is_in'),
    Input('update-all', 'n_clicks')
)
def update_all_players(update_all_btn):
    if update_all_btn is not None:
        return update_all()
    return dash.no_update