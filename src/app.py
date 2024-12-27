import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
load_figure_template('ZEPHYR')

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.ZEPHYR], 
                suppress_callback_exceptions=True)
server = app.server

sidebar = dbc.Nav(
            [
                dbc.NavLink(
                    [
                        html.Div(page["name"], className="ms-2"),
                    ],
                    href=page["path"],
                    active="exact",
                )
                for page in dash.page_registry.values()
            ],
            vertical=True,
            pills=True,
            # style={'background-color': '#003366', 'color': 'white'},
            className="bg-light",
)

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(width=2),
        dbc.Col(html.Div("Interactive tools for introductory economics",
                         style={'fontSize':45, 'textAlign':'left'}))
    ]),

    html.Hr(),

    dbc.Row(
        [
            dbc.Col(
                [
                    html.H4('Topics'),
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
    app.run(debug=False)
