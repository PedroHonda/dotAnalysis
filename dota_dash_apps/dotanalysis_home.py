'''
'''
import dash
import dash_bootstrap_components as dbc
import logging
import queue
from dash import html, dcc
from dash.dependencies import Input, Output, State
from dash_app import app
from dota_dash_apps.dotanalysis_dash_components import (style_center, style_update,
    style_register_box, players_table)
from dotanalysis_control.dta import register_player, update_all

################ Logging information
logger = logging.getLogger(__name__)

##################### QUEUE
dash_queue = queue.Queue()

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
                                dbc.InputGroup("Player ID / Link"),
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
            html.Label("Available Players",
                id="available-players",
            )
        ),
        html.Hr(),
        html.Br(),
        dbc.Row(
            html.Div(
                dbc.Collapse(
                    children=players_table(),
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
                    dbc.Button("OK", className="btn-outline-success disabled"),
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
    ],style=style_register_box))
    return app_layout

################ FUNCTIONS
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
        # Workaround to accept dotabuff/opendota link
        player_id = player_id.split('/')[-1]
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
        update_all(dash_queue)
        return dash.no_update, None, False, 0, dash.no_update, dash.no_update
    return (dash.no_update,)*6
