'''
'''
import dash
import dash_core_components as dcc
import dash_html_components as html
import logging
import time
from dota_dash_apps.dotanalysis_winrate_per_month import app as winrate_per_month_app
from dash.dependencies import Input, Output

#------------------ Logging information
TIME_TAG = time.strftime("%Y_%m_%d-%H_%M_%S")
logName = "./logs/winrate_dota_log_" + TIME_TAG + ".txt"
logging.basicConfig(filename=logName,
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname).1s\t\t%(filename)s[%(lineno)d] : %(message)s',
    datefmt='%d-%m-%y %H:%M:%S',
    filemode='w')

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/team_winrate':
        return winrate_per_month_app.layout
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(debug=True)