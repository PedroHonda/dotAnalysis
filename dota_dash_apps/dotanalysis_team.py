'''
'''
from dota_lib.dota_team import DotaTeam
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import json
import logging
import os
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from datetime import datetime as dtm
from dota_lib.dota_player import DotaPlayer
from dota_lib.dota_team import DotaTeam
from dash_app import app

#------------------ Logging information
logger = logging.getLogger(__name__)

#------------------ STATIC DB QUERIES
cwd = os.getcwd()
PLAYER_DIR_PATH = os.path.join(cwd, 'dota_db', 'players')
available_players = os.listdir(os.path.join(cwd, "dota_db", "players"))
available_players.remove(".gitignore")
available_players.append("All")
available_players.append("<Empty>")

with open(os.path.join(cwd, "dota_db", "heroes", "heroes_dict.json")) as content:
    heroes_dict = json.load(content)

#------------------ CSS STYLES
style_center = {
        "width":"1700px",
        "max-width":"1700px",
        "display":"inline-block",
        "margin-left":"auto",
        "margin-right":"auto"}
style_logo = {
        "width":"100px",
        "max-width":"100px",}

#------------------ DOTA TEAM
dota_team_obj = DotaTeam()

#------------------ PLOTLY FIG
layout = go.Layout(uirevision = 'value', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
fig = go.Figure(layout = layout)

#------------------ APP LAYOUT
def app_layout():
    app_layout = html.Div([
        
    html.Center(html.Div([
        dbc.Row(
            dbc.Col(
                html.H3("Dota Team", style={'text-align': 'center'}),
                        width={'size': 6, 'offset': 3},
            ),
        ),
        dbc.Row(
            dbc.Col(html.H3(["Winrate: ", dbc.Badge(" %", className="ml-1", id="team_winrate_percentage")]),),
        ),
        dbc.Row(
            dbc.Col(
                html.Div(id='team_graph_container',
                    children=[dcc.Graph(id='team_winrate_graph', figure=fig),],
                    style={'display':'none'})
            )
        ),
        dbc.Row([
            dbc.Col([
                dbc.Row([
                    html.Div([
                        dbc.DropdownMenu(
                            [dbc.DropdownMenuItem(player, id="1_"+player+"_team", toggle=True) for player in available_players],
                            label="Player 1",
                            id='1_player-dropdown-menu_team',
                        )
                    ],style={"display": "flex", "flexWrap": "wrap"},),
                    html.Div(id='1_heroes'),
                ])
            ]),
            dbc.Col([
                dbc.Row([
                    html.Div([
                        dbc.DropdownMenu(
                            [dbc.DropdownMenuItem(player, id="2_"+player+"_team", toggle=True) for player in available_players],
                            label="Player 2",
                            id='2_player-dropdown-menu_team',
                        )
                    ],style={"display": "flex", "flexWrap": "wrap"},),
                    html.Div(id='2_heroes'),
                ])
            ]),
            dbc.Col([
                dbc.Row([
                    html.Div([
                        dbc.DropdownMenu(
                            [dbc.DropdownMenuItem(player, id="3_"+player+"_team", toggle=True) for player in available_players],
                            label="Player 3",
                            id='3_player-dropdown-menu_team',
                        )
                    ],style={"display": "flex", "flexWrap": "wrap"},),
                    html.Div(id='3_heroes'),
                ])
            ]),
            dbc.Col([
                dbc.Row([
                    html.Div([
                        dbc.DropdownMenu(
                            [dbc.DropdownMenuItem(player, id="4_"+player+"_team", toggle=True) for player in available_players],
                            label="Player 4",
                            id='4_player-dropdown-menu_team',
                        )
                    ],style={"display": "flex", "flexWrap": "wrap"},),
                    html.Div(id='4_heroes'),
                ])
            ]),
            dbc.Col([
                dbc.Row([
                    html.Div([
                        dbc.DropdownMenu(
                            [dbc.DropdownMenuItem(player, id="5_"+player+"_team", toggle=True) for player in available_players],
                            label="Player 5",
                            id='5_player-dropdown-menu_team',
                        )
                    ],style={"display": "flex", "flexWrap": "wrap"},),
                    html.Div(id='5_heroes'),
                ])
            ]),
        ]),
    ],style=style_center))
    ])
    return app_layout

#------------------ FUNCTIONS
def get_available_players():
    available_players = os.listdir(PLAYER_DIR_PATH)
    available_players.remove(".gitignore")
    return available_players

def get_dota_player(player):
    player_dir = os.path.join(PLAYER_DIR_PATH, player)
    dota_player_files = [os.path.join(player_dir, file) for file in os.listdir(player_dir)]
    dota_player = DotaPlayer()
    dota_player.load_data(dota_player_files)
    return dota_player

def get_team_simplified_matches_df(dota_team):
    simplified_matches = dota_team.matches
    sdf = pd.DataFrame(simplified_matches)
    sdf.index = sdf.date
    sdf["match"]=1
    return sdf

def get_winrate_fig_by_team(team):
    dota_team = []
    for dota_player in team:
        dota_player = dota_player.replace("_team", "")
        if dota_player in ("<Empty>", "All"): continue
        if dota_player in available_players: dota_team.append(dota_player)

    layout = go.Layout(uirevision = 'value', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig = go.Figure(layout = layout)

    if not dota_team: return fig, 0.0

    for idx, player in enumerate(dota_team):
        dota_player = get_dota_player(player)
        dota_team[idx] = dota_player

    global dota_team_obj
    dota_team_obj = DotaTeam(dota_team)
    sdf = get_team_simplified_matches_df(dota_team_obj)
    sdf_month = sdf[["win", "match"]].groupby([lambda x: x.year, lambda x: x.month]).sum()
    sdf_month["winrate"] = 100*sdf_month.win/sdf_month.match
    month = [dtm(date[0], date[1], 1) for date in sdf_month.index]
    fig.add_trace(go.Scatter(x=month, y=sdf_month.winrate))
    fig.layout.xaxis.color = 'white'
    fig.layout.yaxis.color = 'white'

    return fig, dota_team_obj.winrate

def get_most_played_heroes():
    global dota_team_obj
    most_played_heroes_list = dota_team_obj.get_most_played_heroes(heroes_dict)
    most_played_heroes_tables = [[]]*5
    table_header = [
        html.Thead(html.Tr([html.Th("Hero"), html.Th("# Matches")]))
    ]
    for idx, most_played_heroes in enumerate(most_played_heroes_list):
        rows = [html.Tr([html.Td(hero[0]), html.Td(hero[1])]) for hero in most_played_heroes]
        table_body = [html.Tbody(rows)]
        table = dbc.Table(table_header + table_body,
            bordered=True,
            dark=True,
            hover=True,
            responsive=True,
            striped=True,)
        most_played_heroes_tables[idx] = table

    return tuple(most_played_heroes_tables)

#------------------ CALLBACK DEFINITION
@app.callback(
    [
        Output('team_graph_container', 'style'),
        Output('team_winrate_graph', 'figure'),
        Output('team_winrate_percentage', 'children'),
    ]+
    [   Output(str(idx)+"_player-dropdown-menu_team", "label") for idx in range(1,6) ] +
    [   Output(str(idx)+"_heroes", "children") for idx in range(1,6)]
    
    ,

    [   Input(str(idx)+"_player-dropdown-menu_team", "label") for idx in range(1,6) ] +
    [   Input("1_"+player+"_team", "n_clicks") for player in available_players  ] +
    [   Input("2_"+player+"_team", "n_clicks") for player in available_players  ] +
    [   Input("3_"+player+"_team", "n_clicks") for player in available_players  ] +
    [   Input("4_"+player+"_team", "n_clicks") for player in available_players  ] +
    [   Input("5_"+player+"_team", "n_clicks") for player in available_players  ]
)
def plot_winrate_team_dbc(*args):
    players = list(args[0:5])
    ctx = dash.callback_context
    if not ctx.triggered:
        player = "<Empty>"
        display = {'display':'none'}
    else:
        ctx_entry = ctx.triggered[0]["prop_id"].split(".")[0]
        player_id = int(ctx_entry[0])-1
        player = ctx_entry[2:]
        players[player_id] = player
        display = {'display':'block'}
    fig, winrate = get_winrate_fig_by_team(players)
    
    return (display, fig, "{:10.2f}".format(winrate)+" %",
        players[0], players[1], players[2], players[3], players[4])+get_most_played_heroes()
