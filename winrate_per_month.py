'''
'''
import dash
import dash_core_components as dcc
import dash_html_components as html
import json
import logging
import os
import pandas as pd
import plotly.graph_objects as go
import time
from dash.dependencies import Input, Output
from datetime import datetime as dtm
from players.dota_player import DotaPlayer

#------------------ Logging information
TIME_TAG = time.strftime("%Y_%m_%d-%H_%M_%S")
logName = "./logs/winrate_dota_log_" + TIME_TAG + ".txt"
logging.basicConfig(filename=logName,
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname).1s\t\t%(filename)s[%(lineno)d] : %(message)s',
    datefmt='%d-%m-%y %H:%M:%S',
    filemode='w')

app = dash.Dash(__name__)

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

#------------------ STATIC DB QUERIES
cwd = os.getcwd()
available_players = os.listdir(os.path.join(cwd, "dota_db", "players"))
available_players.remove(".gitignore")

#------------------ PLOTLY FIG
layout = go.Layout(uirevision = 'value')
fig = go.Figure(layout = layout)

#------------------ APP LAYOUT
app.layout = html.Div([

    html.H1("Winrate per Month", style={'text-align': 'center'}),

    html.Div([
            dcc.Dropdown(
                id='player',
                options=[{'label': i, 'value': i} for i in available_players],
                value=available_players[0]
            )
        ],style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),

    html.Br(),
    html.Div(id='output_container', children=[]),
    html.Br(),

    dcc.Graph(id='my-winrate-graph', figure=fig),

    html.Div([
        dcc.Markdown("""
            **Matches' details per month**

            Click on points in the graph.
        """),
        html.Pre(id='click-data', style=styles['pre']),
    ], className='three columns')

])

#------------------ FUNCTIONS
def get_dota_player(player):
    player_dir = os.path.join(cwd, 'dota_db', 'players', player)
    dota_player_files = [os.path.join(player_dir, file) for file in os.listdir(player_dir)]
    dota_player = DotaPlayer()
    dota_player.load_data(dota_player_files)
    return dota_player

def get_simplified_matches_df(dota_player):
    simplified_matches = dota_player.simplified_matches()
    sdf = pd.DataFrame(simplified_matches)
    sdf.index = sdf.date
    sdf["match"]=1
    return sdf

def get_match_details_per_month_by_player(date, player):
    dota_player = get_dota_player(player)
    sdf = get_simplified_matches_df(dota_player)
    date_flt = str(date.year)+"-"+str(date.month)

    matches_month = sdf.loc[date_flt][['match_id', 'kda', 'hero', 'side', 'win']]
    matches_month.index = matches_month.index.strftime("%Y-%m-%d")
    matches_month["date"] = matches_month.index
    matches_month = [aux.to_dict() for aux in matches_month.applymap(str).iloc]

    for match in matches_month:
        match["match_id"] = "https://www.opendota.com/matches/"+match["match_id"]

    return json.dumps(matches_month, indent=2)

def get_winrate_fig_by_player(player):
    dota_player = get_dota_player(player)
    sdf = get_simplified_matches_df(dota_player)
    sdf_month = sdf[["win", "match"]].groupby([lambda x: x.year, lambda x: x.month]).sum()
    sdf_month["winrate"] = 100*sdf_month.win/sdf_month.match
    month = [dtm(date[0], date[1], 1) for date in sdf_month.index]
    
    layout = go.Layout(uirevision = 'value')
    fig = go.Figure(layout = layout)
    fig.add_trace(go.Scatter(x=month, y=sdf_month.winrate))
    return fig


#------------------ CALLBACK DEFINITION
@app.callback(
    Output('click-data', 'children'),
    Input('my-winrate-graph', 'clickData'),
    Input('player', 'value')
)
def display_click_data(clickData, player):
    if clickData:
        date = dtm.strptime(clickData["points"][0]["x"], "%Y-%m-%d")
        return get_match_details_per_month_by_player(date, player)
    return json.dumps(clickData, indent=2)

@app.callback(
    Output('my-winrate-graph', 'figure'),
    Input('player', 'value')
)
def plot_winrate_player(player):
    return get_winrate_fig_by_player(player)

if __name__ == "__main__":
    port = 8050
    app.run_server(port=port, debug=True) 
