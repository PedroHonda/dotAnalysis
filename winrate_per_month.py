'''
'''
import dash
import dash_core_components as dcc
import dash_html_components as html
import json
import logging
import pandas as pd
import plotly.graph_objects as go
import time
import tkinter as tk
from tkinter import filedialog
from dash.dependencies import Input, Output
from datetime import datetime as dtm
from players.dota_player import DotaPlayer

# Logging information
TIME_TAG = time.strftime("%Y_%m_%d-%H_%M_%S")
logName = "./logs/winrate_dota_log_" + TIME_TAG + ".txt"
logging.basicConfig(filename=logName,
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname).1s\t\t%(filename)s[%(lineno)d] : %(message)s',
    datefmt='%d-%m-%y %H:%M:%S',
    filemode='w')

def winrate_per_month_app(simplified_matches):
    app = dash.Dash(__name__)

    styles = {
        'pre': {
            'border': 'thin lightgrey solid',
            'overflowX': 'scroll'
        }
    }

    # PLOTLY FIG
    layout = go.Layout(uirevision = 'value')

    sdf = pd.DataFrame(simplified_matches)
    sdf.index = sdf.date
    sdf["match"]=1
    sdf_month = sdf[["win", "match"]].groupby([lambda x: x.year, lambda x: x.month]).sum()
    sdf_month["winrate"] = 100*sdf_month.win/sdf_month.match
    month = [dtm(date[0], date[1], 1) for date in sdf_month.index]
    fig = go.Figure(layout = layout)
    fig.add_trace(go.Scatter(x=month, y=sdf_month.winrate))

    # APP LAYOUT
    app.layout = html.Div([

        html.H1("Winrate per Month", style={'text-align': 'center'}),

        html.Div(id='output_container', children=[]),
        html.Br(),

        dcc.Graph(id='my_winrate_graph', figure=fig),

        html.Div([
                dcc.Markdown("""
                    **Click Data**

                    Click on points in the graph.
                """),
                html.Pre(id='click-data', style=styles['pre']),
            ], className='three columns')

    ])

    # CALLBACK DEFINITION
    @app.callback(
        Output('click-data', 'children'),
        Input('my_winrate_graph', 'clickData'))
    def display_click_data(clickData):
        # TODO: need to refactor this callback later on
        # refer to https://dash.plotly.com/sharing-data-between-callbacks
        if clickData:
            date = dtm.strptime(clickData["points"][0]["x"], "%Y-%m-%d")
            date_flt = str(date.year)+"-"+str(date.month)
            matches_month = sdf.loc[date_flt][['match_id', 'kda', 'hero', 'side', 'win']]
            matches_month.index = matches_month.index.strftime("%Y-%m-%d")
            matches_month["date"] = matches_month.index
            matches_month = [aux.to_dict() for aux in matches_month.applymap(str).iloc] 
            return json.dumps(matches_month, indent=2)
        return json.dumps(clickData, indent=2)

    return app

if __name__ == "__main__":
    tk.Tk().withdraw()
    dota_player_files = filedialog.askopenfilenames(
            filetypes=(("Dota Player JSON data", ".json"),),
            title="Select the Dota Player's JSON Data you want to load")
    dota_player = DotaPlayer()
    dota_player.load_data(dota_player_files)
    simplified_matches = dota_player.simplified_matches()

    app = winrate_per_month_app(simplified_matches)
    port = 8050
    app.run_server(port=port, debug=True) 
