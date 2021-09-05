import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from dash_app import app
from dota_dash_apps import dotanalysis_winrate as app_winrate
from dota_dash_apps import dotanalysis_home as app_home
from dota_dash_apps import dotanalysis_players as app_players

from dota_dash_apps.dotanalysis_winrate import app_layout as winrate_app_layout
from dota_dash_apps.dotanalysis_home import app_layout as home_app_layout
from dota_dash_apps.dotanalysis_players import app_layout as players_app_layout

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
                        dbc.Col(html.A(html.I("Github",className="fa fa-github"),className="nav-link")),
                    ],
                    align="center",
                    no_gutters=True,
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
    else:
        app_home.layout = home_app_layout()
        return app_home.layout

if __name__ == '__main__':
    app.run_server(debug=True)