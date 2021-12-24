'''
'''
import dash
import dash_bootstrap_components as dbc
import logging
import plotly.graph_objects as go
from datetime import datetime as dtm
from dash import html, dcc
from dash.dependencies import Input, Output, State
from dash_app import app
from dota_dash_apps.dotanalysis_dash_components import (style_center, get_players_data, get_team_info, get_monthly_matches_data)
from dotanalysis_control.dta import (get_available_players, get_dota_team)

################ LOGGING
logger = logging.getLogger(__name__)

################ AVAILABLE PLAYERS
AVAILABLE_PLAYERS = get_available_players()

################ APP LAYOUT
app_layout = html.Center(html.Div([
    dbc.Row(
        dbc.Col(
            html.H3("Dota Team", style={'text-align': 'center'}),
                    width={'size': 6, 'offset': 3},
        ),
    ),
    html.Br(),
    dbc.Row([
        dbc.Card(
            dbc.CardBody(
                [dbc.Button(player, id=player+"_team", className="btn btn-dark") for player in AVAILABLE_PLAYERS],
            ),
        color='dark'),
    ]),
    html.Br(),
    dbc.Row(
        dbc.Col(html.H3(["Winrate: ", dbc.Badge(" %", className="ml-1", id="team-winrate-percentage")]),),
    ),
    dbc.Row(
        dbc.Col(
            html.Div(id='team-graph-container',
                children=[dcc.Graph(id='team-winrate-graph',
                                    figure=go.Figure(
                                        layout=go.Layout(uirevision='value',
                                                         paper_bgcolor='rgba(0,0,0,0)',
                                                         plot_bgcolor='rgba(0,0,0,0)')
                                                    )
                                    ),
                        ],
                style={'display':'none'})
        )
    ),
    # ADDITIONAL INFO
    dbc.Row(html.Label("More", id='more')),
    html.Hr(),
    dbc.Row(
        dbc.Collapse(
            dbc.Card(
                dbc.CardBody([
                    dbc.Row(
                        html.P(
                            [],
                            className="card-text",
                            id="more-card",
                            style={"text-align":"left"}
                        ),
                    ),
                    html.Br(),
                    dbc.Row(
                        html.Div(
                            [],
                            id="team-matches-month"
                        )
                    )
                ]),
            color='dark'),
            id="more-collapse",
            is_open=False,
        )
    ),
    html.Br(),
    dbc.Row([
        dbc.Col(html.Div(id='1_player')),
        dbc.Col(html.Div(id='2_player')),
        dbc.Col(html.Div(id='3_player')),
        dbc.Col(html.Div(id='4_player')),
        dbc.Col(html.Div(id='5_player')),
    ]),
    dcc.Store(id='dota-team', data=[]),
],style=style_center))

################ FUNCTIONS

################ CALLBACK DEFINITION
## Updating dota_team according to user's input
@app.callback(
    [   Output(player+"_team", "n_clicks") for player in AVAILABLE_PLAYERS  ]+
    [   Output(player+"_team", "className") for player in AVAILABLE_PLAYERS  ]+
    [   Output('dota-team', 'data') ],
    [   Input(player+"_team", "n_clicks") for player in AVAILABLE_PLAYERS  ],
    [   State('dota-team', 'data')  ]
)
def updating_dota_team(*args):
    dota_team = args[-1]
    n_clicks = [0]*len(AVAILABLE_PLAYERS)
    class_names = [dash.no_update]*len(AVAILABLE_PLAYERS)
    
    ctx = dash.callback_context

    if ctx.triggered:
        ctx_entry = ctx.triggered[0]["prop_id"].split(".")[0]
        new_player = ctx_entry.replace("_team", "")

        for player in dota_team:
            player_idx = AVAILABLE_PLAYERS.index(player)
            n_clicks[player_idx] = 1
            class_names[player_idx] = "btn btn-outline-info"

        new_player_idx = AVAILABLE_PLAYERS.index(new_player)

        if new_player not in dota_team:
            # DotaTeam does not support more than 5 players
            if len(dota_team) == 5:
                logger.debug("Not able to add more players because DotaTeam is full")
                return tuple(n_clicks)+tuple(class_names)+(dash.no_update,)
            dota_team.append(new_player)
            n_clicks[new_player_idx] = 1
            class_names[new_player_idx] = "btn btn-outline-info"
            logger.debug("Player %s added to DotaTeam: %s", new_player, dota_team)
            return tuple(n_clicks)+tuple(class_names)+(dota_team,)
        else:
            dota_team.remove(new_player)
            n_clicks[new_player_idx] = 0
            class_names[new_player_idx] = "btn btn-dark"
            logger.debug("Removing player %s from DotaTeam: %s", new_player, dota_team)
            return tuple(n_clicks)+tuple(class_names)+(dota_team,)

    return tuple(n_clicks)+tuple(class_names)+(dash.no_update,)

## Plot Team's winrate graph
@app.callback(
    [
        Output('team-winrate-graph', 'figure'),
        Output('team-graph-container', 'style')
    ],
    Input('dota-team', 'data')
)
def plot_winrate_graph_callback(dota_team):
    dota_team_obj = get_dota_team(dota_team)
    fig = dota_team_obj.get_winrate_fig()
    if dota_team:
        return fig, {'display':'block'}
    return fig, {'display':'none'}

## Get individual players' data
@app.callback(
    [Output(str(idx)+"_player", "children") for idx in range(1,6) ],
    Input('dota-team', 'data')
)
def update_player_data_callback(dota_team):
    return get_players_data(dota_team)

## Get Team's additional info
@app.callback(
    Output('more-card', 'children'),
    Input('dota-team', 'data')
)
def get_team_info_callback(dota_team):
    return get_team_info(dota_team)

## Get Team's winrate
@app.callback(
    Output('team-winrate-percentage', 'children') ,
    Input('dota-team', 'data')
)
def get_team_winrate_callback(dota_team):
    if not dota_team:
        return " %"
    dota_team_obj = get_dota_team(dota_team)
    return "{:10.2f}".format(dota_team_obj.get_team_winrate())+" %",

## Expand "More" info card
@app.callback(
    Output('more-collapse', 'is_open'),
    Input('more', 'n_clicks'),
    State('more-collapse', 'is_open')
)
def advanced_settings_callback(n, collapse_is_open):
    if n is not None:
        return not collapse_is_open
    return dash.no_update

## Get Team's winrate
@app.callback(
    Output('team-matches-month', 'children'),
    Input('team-winrate-graph', 'clickData'),
    State('dota-team', 'data')
)
def display_click_data_table_dbc(clickData, dota_team):
    if clickData:
        if dota_team:
            logging.debug("team_clickData=%s", clickData)
            date = dtm.strptime(clickData["points"][0]["x"], "%Y-%m-%d")
            return get_monthly_matches_data(dota_team, date)
    return []
