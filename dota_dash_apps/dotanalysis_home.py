'''
'''
import dash
import dash_bootstrap_components as dbc
import json
import logging
import os
import queue
import threading
from dash import html, dcc
from dash.dependencies import Input, Output, State
from dota_lib.dota_player import DotaPlayer
from dash_app import app


################ Logging information
logger = logging.getLogger(__name__)

##################### QUEUE
dash_queue = queue.Queue()

################ STATIC DB QUERIES
cwd = os.getcwd()
PLAYER_DIR_PATH = os.path.join(cwd, 'dota_db', 'players')
DOTA_DB = os.path.join(cwd, "dota_db")
DOTA_DB_PLAYERS = os.path.join(DOTA_DB, "players")

with open(os.path.join(cwd, "dota_db", "heroes", "heroes_dict.json")) as content:
    heroes_dict = json.load(content)

dota_players = os.listdir(PLAYER_DIR_PATH)
dota_players.remove(".gitignore")

################ FUNCTIONS
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
    update_all_thread = threading.Thread(target=update_all_t)
    update_all_thread.start()

def update_all_t():
    available_players = get_available_players()
    progress_aux_old = 0
    available_players_length = len(available_players)
    for idx, players in enumerate(available_players):
        split = players.split("_")
        id = split[-1]
        name = "_".join(split[:-1])
        register_player(id, name)
        progress_aux = int((100 * idx) / available_players_length)
        if progress_aux > progress_aux_old and progress_aux <= 100:
            dash_queue.put(progress_aux)
            progress_aux_old = progress_aux
    dash_queue.put(("status", "finished"))

def trigger_queue():
    ok_fade = dash.no_update
    trigger = dash.no_update
    trigger_interval = dash.no_update
    progress = -1

    while dash_queue.qsize():
        queue_info = dash_queue.get(0)
        if isinstance(queue_info, int) or isinstance(queue_info, float):
            progress = queue_info
        elif isinstance(queue_info, tuple):
            if queue_info[0] == "status":
                # script just finished, so we need to check if tput graph is needed
                if queue_info[1] == "finished":
                    progress = 0
                    ok_fade = True
    if progress == -1: progress, progress_str = dash.no_update, dash.no_update
    else: progress_str = f"{int(progress)} %" if progress >= 5 else ""
    return ok_fade, dash.no_update, trigger, trigger_interval, progress, progress_str
################ DASH MODULES
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

################ CSS STYLES
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
################ APP LAYOUT
def app_layout():
    app_layout = html.Center(html.Div([
        dbc.Row(
            dbc.Card([
                dbc.CardHeader("Register a New Player", className="card-body"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(
                            dbc.InputGroup([
                                dbc.InputGroup("Player ID"),
                                dbc.Input(placeholder="", id='player-id', style={'color': 'white'}),
                            ]),
                        ),
                        dbc.Col(
                            dbc.InputGroup([
                                dbc.InputGroup("Player Name"),
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
        # PROGRESS BAR
        dbc.Row(
            dbc.Progress(id="progress", striped=True, animated=True),
        ),
        dcc.Interval(id="trigger", n_intervals=0, interval=1000, disabled=True),
    ],style=style_center))
    return app_layout

################ CALLBACK DEFINITION
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
    [
        Output('ok-fade', 'is_in'),
        Output('update-all', 'n_clicks'),
        Output('trigger', 'disabled'),
        Output('trigger', 'n_intervals'),
        Output("progress", "value"),
        Output("progress", "label"),
    ],
    [
        Input('update-all', 'n_clicks'),
        Input('trigger', 'n_intervals')
    ]
)
def update_all_players(update_all_btn, trigger):
    if trigger:
        return trigger_queue()
    if update_all_btn is not None:
        update_all()
        return dash.no_update, None, False, 0, dash.no_update, dash.no_update
    return (dash.no_update,)*6