'''
'''
from dota_lib.dota_team import DotaTeam
import dash
import dash_bootstrap_components as dbc
import logging
import plotly.graph_objects as go
from dash import html, dcc
from dash.dependencies import Input, Output, State
from dota_lib.dota_team import DotaTeam
from dash_app import app
from dota_dash_apps.dotanalysis_dash_components import style_center
from dotanalysis_control.dta import get_available_players, get_dota_player, heroes_dict

################ Logging information
logger = logging.getLogger(__name__)

################ GLOBAL
available_players = get_available_players()
dota_team_obj = DotaTeam()

################ PLOTLY FIG
layout = go.Layout(uirevision = 'value', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
fig = go.Figure(layout = layout)

################ APP LAYOUT
def app_layout():
    app_layout = html.Center(html.Div([
        dbc.Row(
            dbc.Col(
                html.H3("Dota Team", style={'text-align': 'center'}),
                        width={'size': 6, 'offset': 3},
            ),
        ),
        dbc.Row([
            dbc.Col(
                dbc.DropdownMenu(
                    [dbc.DropdownMenuItem(player, id=player+"_team", toggle=True) for player in available_players],
                    label="Add a Player to the Team",
                    id='player-dropdown-menu_team',
                )
            ),
            dbc.Col([
                dcc.Checklist(
                    options=[
                        {"label": "Radiant", "value": 1},
                    ],
                    value=[1],
                    id="radiant-btn",
                    labelClassName="form-check-label",
                    inputClassName="form-check-input",
                    className="form-check form-switch",
                    style={"text-align":"left"}
                ),
                dcc.Checklist(
                    options=[
                        {"label": "Dire", "value": 1},
                    ],
                    value=[1],
                    id="dire-btn",
                    labelClassName="form-check-label",
                    inputClassName="form-check-input",
                    className="form-check form-switch",
                    style={"text-align":"left"}
                ),
            ])
        ]),
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
        # ADDITIONAL INFO
        dbc.Row(
            html.Label("More", id='more')
        ),
        html.Hr(),
        dbc.Row(
            dbc.Collapse(
                dbc.Card([
                    dbc.CardBody(
                        [
                            html.P(
                                [],
                                className="card-text",
                                id="more-card",
                                style={"text-align":"left"}
                            ),
                        ]
                    ),
                ], color='dark'),
                id="more-collapse",
                is_open=False,
            )
        ),
        html.Br(),
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
    return app_layout

################ FUNCTIONS

def get_dota_team(team):
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

    return DotaTeam(dota_team)

def get_most_played_heroes():
    global dota_team_obj
    most_played_heroes_list = dota_team_obj.get_most_played_heroes(heroes_dict)
    table_header = [
        html.Thead(html.Tr([html.Th("Hero"), html.Th("Matches"), html.Th("Winrate")]))
    ]
    table = dbc.Table(table_header,bordered=True,dark=True,hover=True,responsive=True,striped=True)
    most_played_heroes_tables = [[table]]*5
    for idx, most_played_heroes in enumerate(most_played_heroes_list):
        rows = [html.Tr([html.Td(hero[0]),
                html.Td(hero[1][0]),
                html.Td("{:10.2f}".format(100*hero[1][1] / hero[1][0]))])
                for hero in most_played_heroes]
        table_body = [html.Tbody(rows)]
        table = dbc.Table(table_header + table_body,
            bordered=True,
            dark=True,
            hover=True,
            responsive=True,
            striped=True,)
        most_played_heroes_tables[idx] = table

    return tuple(most_played_heroes_tables)

def get_team_info():
    global dota_team_obj
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
    return (team_info,)

################ CALLBACK DEFINITION
@app.callback(
    [
        Output('team_graph_container', 'style'),
        Output('team_winrate_graph', 'figure'),
        Output('team_winrate_percentage', 'children'),
    ]+
    [   Output(str(idx)+"_player-dropdown-menu_team", "label") for idx in range(1,6) ] +
    [   Output(str(idx)+"_heroes", "children") for idx in range(1,6) ] +
    [   Output('more-card', 'children')    ]
    
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
    fig, winrate = dash.no_update, 0.0
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
        global dota_team_obj
        dota_team_obj = get_dota_team(players)
        fig = dota_team_obj.get_winrate_fig()
        winrate = dota_team_obj.get_team_winrate()
    
    return (display, fig, "{:10.2f}".format(winrate)+" %",
        players[0], players[1], players[2], players[3], players[4])+get_most_played_heroes()+get_team_info()

@app.callback(
    Output('more-collapse', 'is_open'),
    Input('more', 'n_clicks'),
    State('more-collapse', 'is_open')
)
def advanced_settings_callback(n, collapse_is_open):
    if n is not None:
        return not collapse_is_open
    return dash.no_update
