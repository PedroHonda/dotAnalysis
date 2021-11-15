'''
'''
from dota_lib.dota_team import DotaTeam
import dash
import dash_bootstrap_components as dbc
import logging
import pandas as pd
import plotly.graph_objects as go
from dash import html, dcc
from dash.dependencies import Input, Output
from datetime import datetime as dtm
from dota_lib.dota_team import DotaTeam
from dash_app import app
from dota_dash_apps.dotanalysis_dash_components import style_center
from dotanalysis_control.dta import get_dota_player, get_available_players

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
    app_layout = html.Div([
        
    html.Center(html.Div([
        dbc.Row(
            dbc.Col(
                html.H3("Winrate per Month", style={'text-align': 'center'}),
                        width={'size': 6, 'offset': 3},
            ),
        ),
        dbc.Row([
            dbc.Col(
                html.Div([
                    dbc.DropdownMenu(
                        [dbc.DropdownMenuItem(player, id="1_"+player, toggle=True) for player in available_players],
                        label="Player 1",
                        id='1_player-dropdown-menu',
                    )
                ],style={"display": "flex", "flexWrap": "wrap"},),
            ),
            dbc.Col(
                html.Div([
                    dbc.DropdownMenu(
                        [dbc.DropdownMenuItem(player, id="2_"+player, toggle=True) for player in available_players],
                        label="Player 2",
                        id='2_player-dropdown-menu',
                    )
                ],style={"display": "flex", "flexWrap": "wrap"},),
            ),
            dbc.Col(
                html.Div([
                    dbc.DropdownMenu(
                        [dbc.DropdownMenuItem(player, id="3_"+player, toggle=True) for player in available_players],
                        label="Player 3",
                        id='3_player-dropdown-menu',
                    )
                ],style={"display": "flex", "flexWrap": "wrap"},),
            ),
            dbc.Col(
                html.Div([
                    dbc.DropdownMenu(
                        [dbc.DropdownMenuItem(player, id="4_"+player, toggle=True) for player in available_players],
                        label="Player 4",
                        id='4_player-dropdown-menu',
                    )
                ],style={"display": "flex", "flexWrap": "wrap"},),
            ),
            dbc.Col(
                html.Div([
                    dbc.DropdownMenu(
                        [dbc.DropdownMenuItem(player, id="5_"+player, toggle=True) for player in available_players],
                        label="Player 5",
                        id='5_player-dropdown-menu',
                    )
                ],style={"display": "flex", "flexWrap": "wrap"},),
            ),
            dbc.Col(html.H3(["Winrate: ", dbc.Badge(" %", className="ml-1", id="winrate_percentage")]),),
            ]),
        dbc.Row(
            dbc.Col(
                html.Div(id='team-graph-container',
                    children=[dcc.Graph(id='team-winrate-graph', figure=fig),],
                    style={'display':'none'})
            )
        ),
        dbc.Row(
            dbc.Col(
                html.Div(id='team-matches-month-dbc')
            )
        ),
    ],style=style_center))
    ])
    return app_layout

################ FUNCTIONS
def get_team_simplified_matches_df(dota_team):
    simplified_matches = dota_team.matches
    sdf = pd.DataFrame(simplified_matches)
    sdf.index = sdf.date
    sdf["match"]=1
    return sdf

def get_winrate_fig_by_team(team):
    dota_team = []
    for dota_player in team:
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

def get_team_match_details_per_month_by_player_table_dbc(date):
    global dota_team_obj
    sdf = get_team_simplified_matches_df(dota_team_obj)
    date_flt = str(date.year)+"-"+str(date.month)

    matches_month = sdf.loc[date_flt][['match_id', 'side', 'win']]
    matches_month.index = matches_month.index.strftime("%Y-%m-%d")
    matches_month["date"] = matches_month.index
    #return dbc.Table.from_dataframe(matches_month)
    simplified_matches_columns = ["#", "date", "match_id", "side", "win"]
    table_header = [
        html.Thead(html.Tr([html.Th(h) for h in simplified_matches_columns]))
    ]
    matches_month = [aux.to_dict() for aux in matches_month.applymap(str).iloc]

    rows = []
    for idx, match in enumerate(matches_month):
        match["#"] = idx
        match_id_link = "https://www.opendota.com/matches/"+match["match_id"]
        match["match_id"] = match_id_link
        rows.append(html.Tr([
                html.Td(idx),
                html.Td(match["date"]),
                html.Td(dcc.Link(match_id_link, href=match_id_link)),
                html.Td(match["side"]),
                html.Td(match["win"])
            ]))

    table_body = [html.Tbody(rows)]

    table = dbc.Table(table_header + table_body,
        bordered=True,
        dark=True,
        hover=True,
        responsive=True,
        striped=True,)
    return table

################ CALLBACK DEFINITION
@app.callback(
    [
        Output('team-graph-container', 'style'),
        Output('team-winrate-graph', 'figure'),
        Output('winrate_percentage', 'children'),
        Output('1_player-dropdown-menu', 'label'),
        Output('2_player-dropdown-menu', 'label'),
        Output('3_player-dropdown-menu', 'label'),
        Output('4_player-dropdown-menu', 'label'),
        Output('5_player-dropdown-menu', 'label')
    ],
    [   Input(str(idx)+"_player-dropdown-menu", "label") for idx in range(1,6) ] +
    [   Input("1_"+player, "n_clicks") for player in available_players  ] +
    [   Input("2_"+player, "n_clicks") for player in available_players  ] +
    [   Input("3_"+player, "n_clicks") for player in available_players  ] +
    [   Input("4_"+player, "n_clicks") for player in available_players  ] +
    [   Input("5_"+player, "n_clicks") for player in available_players  ]
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
    return display, fig, "{:10.2f}".format(winrate)+" %", players[0], players[1], players[2], players[3], players[4]

@app.callback(
    Output('team-matches-month-dbc', 'children'),
    Input('team-winrate-graph', 'clickData'),
)
def display_click_data_table_dbc(clickData):
    if clickData:
        logging.debug("team_clickData=%s", clickData)
        date = dtm.strptime(clickData["points"][0]["x"], "%Y-%m-%d")
        return get_team_match_details_per_month_by_player_table_dbc(date)
    return []

if __name__ == "__main__":
    port = 8050
    app.run_server(port=port, debug=True) 
