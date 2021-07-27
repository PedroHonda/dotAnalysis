'''
'''
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import json
import logging
import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
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

theme =  {
    'dark': True,
    'detail': '#007439',
    'primary': '#00EA64',
    'secondary': '#6E6E6E',
}


#------------------ STATIC DB QUERIES
cwd = os.getcwd()
available_players = os.listdir(os.path.join(cwd, "dota_db", "players"))
available_players.remove(".gitignore")
available_players.append("All")

simplified_matches_columns = ["#", "date", "match_id", "kda", "side", "hero", "win"]

with open(os.path.join(cwd, "dota_db", "heroes", "heroes_dict.json")) as content:
    heroes_dict = json.load(content)

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

    dash_table.DataTable(
        id='matches-month',
        columns=[{"name": i, "id": i} for i in simplified_matches_columns],
        data=[],
        editable=True
    )

])

#------------------ FUNCTIONS
def get_dota_player(player):
    player_dir = os.path.join(cwd, 'dota_db', 'players', player)
    dota_player_files = [os.path.join(player_dir, file) for file in os.listdir(player_dir)]
    dota_player = DotaPlayer()
    dota_player.load_data(dota_player_files)
    return dota_player

def get_simplified_matches_df(dota_player):
    simplified_matches = dota_player.simplified_matches(heroes_dict)
    sdf = pd.DataFrame(simplified_matches)
    sdf.index = sdf.date
    sdf["match"]=1
    return sdf

def get_winrate_fig_by_player(player):
    if player == "All": players_id = available_players
    else:   players_id = [player]

    layout = go.Layout(uirevision = 'value')
    fig = go.Figure(layout = layout)
    for player_id in players_id:
        if player_id == "All": continue
        dota_player = get_dota_player(player_id)
        sdf = get_simplified_matches_df(dota_player)
        sdf_month = sdf[["win", "match"]].groupby([lambda x: x.year, lambda x: x.month]).sum()
        sdf_month["winrate"] = 100*sdf_month.win/sdf_month.match
        month = [dtm(date[0], date[1], 1) for date in sdf_month.index]
        fig.add_trace(go.Scatter(x=month, y=sdf_month.winrate, name=player_id))
        #fig.add_trace(px.scatter(x=month, y=sdf_month.winrate, template="plotly_dark"))
    return fig

def get_match_details_per_month_by_player_table(date, player):
    if player == "All": return []
    dota_player = get_dota_player(player)
    sdf = get_simplified_matches_df(dota_player)
    date_flt = str(date.year)+"-"+str(date.month)

    matches_month = sdf.loc[date_flt][['match_id', 'kda', 'hero', 'side', 'win']]
    matches_month.index = matches_month.index.strftime("%Y-%m-%d")
    matches_month["date"] = matches_month.index
    matches_month = [aux.to_dict() for aux in matches_month.applymap(str).iloc]

    for idx, match in enumerate(matches_month):
        match["#"] = idx
        match_id_link = "https://www.opendota.com/matches/"+match["match_id"]
        match["match_id"] = match_id_link

    return matches_month

#------------------ CALLBACK DEFINITION
@app.callback(
    Output('my-winrate-graph', 'figure'),
    Input('player', 'value')
)
def plot_winrate_player(player):
    return get_winrate_fig_by_player(player)

@app.callback(
    Output('matches-month', 'data'),
    Input('my-winrate-graph', 'clickData'),
    Input('player', 'value')
)
def display_click_data_table(clickData, player):
    if clickData:
        logging.debug("clickData=%s", clickData)
        date = dtm.strptime(clickData["points"][0]["x"], "%Y-%m-%d")
        return get_match_details_per_month_by_player_table(date, player)
    return []

if __name__ == "__main__":
    port = 8050
    app.run_server(port=port, debug=True) 
