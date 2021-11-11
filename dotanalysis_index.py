import dash_bootstrap_components as dbc
import logging
from dash import html, dcc
from dash.dependencies import Input, Output

from dash_app import app
from dota_dash_apps import dotanalysis_winrate as app_winrate
from dota_dash_apps import dotanalysis_home as app_home
from dota_dash_apps import dotanalysis_players as app_players
from dota_dash_apps import dotanalysis_team as app_team

from dota_dash_apps.dotanalysis_winrate import app_layout as winrate_app_layout
from dota_dash_apps.dotanalysis_home import app_layout as home_app_layout
from dota_dash_apps.dotanalysis_players import app_layout as players_app_layout
from dota_dash_apps.dotanalysis_team import app_layout as team_app_layout

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
                        dbc.Col(dbc.NavLink("Winrate", href="/winrate", className="nav-link")),
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
    if pathname == '/winrate':
        app_winrate.layout = winrate_app_layout()
        return app_winrate.layout
    elif '/players/' in pathname:
        app_players.layout = players_app_layout(pathname.split("/players/")[1])
        return app_players.layout
    elif '/team' in pathname:
        app_team.layout = team_app_layout()
        return app_team.layout
    else:
        app_home.layout = home_app_layout()
        return app_home.layout

if __name__ == '__main__':
    app.run_server(debug=True)