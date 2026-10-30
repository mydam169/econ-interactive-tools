import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

FONTS = "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap"

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.FLATLY, FONTS],
                suppress_callback_exceptions=True)

server = app.server

sidebar = dbc.Nav(
            [
                dbc.NavLink(
                    page["name"],
                    href=page["path"],
                    active="exact",
                )
                for page in dash.page_registry.values()
            ],
            vertical=True,
            className="sidebar",
)

header = html.Div([
    html.Div("Interactive tools for introductory economics", className="app-title"),
    html.Div("Supply, demand and the welfare effects of market interventions", className="app-subtitle"),
], className="app-header")

app.layout = dbc.Container([
    header,

    dbc.Row(
        [
            dbc.Col(
                [
                    html.Div('Topics', className="sidebar-heading"),
                    sidebar
                ], xs=4, sm=4, md=2, lg=2, xl=2, xxl=2),

            dbc.Col(
                [
                    dash.page_container
                ], xs=8, sm=8, md=10, lg=10, xl=10, xxl=10)
        ]
    )
], fluid=True)


if __name__ == "__main__":
    app.run(debug=True, port=8050)
