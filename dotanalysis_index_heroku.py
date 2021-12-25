import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output

from dash_app import app, server
from dota_dash_apps import dotanalysis_team

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
    if '/team' in pathname:
        return dotanalysis_team.app_layout
    else:
        return html.H1("Ask your Master to add new players or update existing ones!")

if __name__ == '__main__':
    app.run_server(debug=False)
