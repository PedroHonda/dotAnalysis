'''
'''
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

#------------------ CSS STYLES
style_center = {
        "width":"1700px",
        "max-width":"1700px",
        "display":"inline-block",
        "margin-left":"auto",
        "margin-right":"auto"}

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
                    dbc.Card(
                        dbc.CardBody("", id="files_names", style=style_center),
                        style=style_center,
                    ),
                    id="players-collapse",
                    is_open=False,
                )
            ),
        ),
    ],style=style_center))
    return app_layout

#------------------ FUNCTIONS
def get_available_players():
    available_players = os.listdir(PLAYER_DIR_PATH)
    available_players.remove(".gitignore")
    return available_players

def register_player(player_id, player_name):
    dota_player = DotaPlayer(player_id, player_name)
    if not dota_player.get_all(): return
    dota_player.save_data(DOTA_DB_PLAYERS, overwrite_data=True)

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
    Output('players-collapse', 'children'),
    Output('players-collapse', 'is_open'),
    Input('available-players', 'n_clicks'),
    State('players-collapse', 'is_open')
)
def update_output(available_players, players_collapse):
    if available_players is not None:
        available_players = get_available_players()
        table_header = [html.Thead(html.Tr([html.Th("Players")]))]
        table_body = [html.Tbody(
                [html.Tr([html.Td(dcc.Link(p, href="/players/"+p))]) for p in available_players]
            )]
        table = dbc.Table(table_header + table_body,
            bordered=True,
            dark=True,
            hover=True,
            responsive=True,
            striped=True,)
        return table, not players_collapse
    else:
        return "", False
