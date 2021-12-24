import dash_bootstrap_components as dbc
import logging
from dash import html, dcc
from dash.dependencies import Input, Output

from dash_app import app
from dota_dash_apps import dotanalysis_home
from dota_dash_apps import dotanalysis_players
from dota_dash_apps import dotanalysis_team

# Logging information
logName = "./logs/dotanalysis_index.log"
logging.basicConfig(filename=logName,
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname).1s\t\t%(filename)s[%(lineno)d] : %(message)s',
    datefmt='%d-%m-%y %H:%M:%S',
    filemode='a')

app.title = "DotAnalysis"

app.layout = html.Div([
    dbc.Row([
        dbc.Navbar(
            html.Div([
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=app.get_asset_url('dota.png'), height="40px")),
                        dbc.Col(dbc.NavbarBrand("dotAnalysis", className="ml-2")),
                        dbc.Col(dbc.NavLink("Home", href="/", className="nav-link")),
                        dbc.Col(dbc.NavLink("Team", href="/team", className="nav-link")),
                        dbc.Col(html.A(html.I("Github",className="fa fa-github"),className="nav-link")),
                    ],
                    align="center",
                ),
                href="https://github.com/pedrohonda/dotanalysis",
                className="navbar-brand",
            ),
        ], className="container-fluid"),
        color="bg-primary",
        className="navbar navbar-expand-lg navbar-dark bg-primary"
        )
    ]),
    html.Br(),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if '/players/' in pathname:
        return dotanalysis_players.app_layout(pathname.split("/players/")[1])
    elif '/team' in pathname:
        return dotanalysis_team.app_layout
    else:
        return dotanalysis_home.app_layout

if __name__ == '__main__':
    app.run_server(debug=True)