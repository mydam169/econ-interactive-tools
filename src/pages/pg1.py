# Chapter 1. Basic supply and demand
import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go 
import numpy as np
from .markdown_texts import intro_md

dash.register_page(__name__, path='/', name='Supply and demand')

layout = dbc.Container(
    [
        # dbc.Row(
        #     dbc.Col(
        #         html.H1(
        #             "Perfectly competitive market", 
        #             className="text-center bg-primary text-white p-2"
        #             )
        #     )
        # ),
        dbc.Row(
            html.Div(
                dcc.Markdown(intro_md(), mathjax=True)
            )
        ),
        dbc.Row(
            dbc.Col(dcc.Graph(id='supply-demand-graph'), width=11)
        ), 
        dbc.Row(
            [
                dbc.Col(
                    html.Div([
                        html.Label("Adjust Demand Curve Intercept (a):"),
                        dcc.Slider(id='demand-intercept-slider', min=50, max=100, value=80, marks={i: str(i) for i in range(50, 101, 10)}),
                        
                        html.Label("Adjust Demand Curve Slope (b):"),
                        dcc.Slider(id='demand-slope-slider', min=-5, max=-0.1, value=-0.5, step=0.1, marks={i: str(i) for i in range(-5, 1, 1)}),
                        
                        html.Label("Adjust Supply Curve Intercept (c):"),
                        dcc.Slider(id='supply-intercept-slider', min=0, max=50, value=10, marks={i: str(i) for i in range(0, 51, 10)}),
                        
                        html.Label("Adjust Supply Curve Slope (d):"),
                        dcc.Slider(id='supply-slope-slider', min=0.1, max=5, value=0.5, step=0.1, marks={i: str(i) for i in range(1, 6, 1)}),
                    ]), 
                    width=5, 
                    style={'margin-right': '30px'}
                ), 
                dbc.Col([], width=1),
                dbc.Col(
                    html.Div([
                        html.Ul([
                            html.Li(dcc.Markdown(id='demand-eqn', mathjax=True)),
                            html.Li(dcc.Markdown(id='supply-eqn', mathjax=True)),
                            html.Li(dcc.Markdown(id='eqm-price', mathjax=True)), 
                            html.Li(dcc.Markdown(id='eqm-qty', mathjax=True)), 
                            html.Li(dcc.Markdown(id='consumer-surplus', mathjax=True)), 
                            html.Li(dcc.Markdown(id='producer-surplus', mathjax=True))
                        ])
                    ]), 
                    width=5
                )
            ]
        )

    ]
)

@callback(
    [Output('supply-demand-graph', 'figure'), 
     Output('demand-eqn', 'children'), 
     Output('supply-eqn', 'children'), 
     Output('eqm-price', 'children'), 
     Output('eqm-qty', 'children'), 
     Output('consumer-surplus', 'children'), 
     Output('producer-surplus', 'children')],
    [Input('demand-intercept-slider', 'value'),
    Input('demand-slope-slider', 'value'),
    Input('supply-intercept-slider', 'value'),
    Input('supply-slope-slider', 'value')]
)

def update_graph(demand_intercept, demand_slope, supply_intercept, supply_slope):
    demand_eqn = f'Demand equation: $P = {demand_intercept} - {-demand_slope}Q$'
    supply_eqn = f'Supply equation: $P = {supply_intercept} + {supply_slope}Q$'
    quantity = np.linspace(0, 100, 100)

    ############### EQM outcomes ##################
    eqm_qty = (supply_intercept - demand_intercept) / (demand_slope - supply_slope)
    eqm_price = demand_intercept + demand_slope * eqm_qty
    consumer_surplus = 0.5 * (demand_intercept - eqm_price) * eqm_qty
    producer_surplus = 0.5 * (eqm_price - supply_intercept) * eqm_qty
    Q_star = f'Equilibrium quantity: $Q^* = {round(eqm_qty, 2)}$'
    P_star = f'Equilibrium price: $P^* = {round(eqm_price, 2)}$'
    CS_star = f'Consumer surplus: $SC = {round(consumer_surplus, 2)}$'
    PS_star = f'Producer surplus: $PS = {round(producer_surplus, 2)}$'

    ############## GRAPH ##########################
    demand = demand_intercept + demand_slope * quantity 
    supply = supply_intercept + supply_slope * quantity
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=quantity, y=demand, mode='lines', name='Demand', line=dict(color='blue'))
    )
    fig.add_trace(
        go.Scatter(x=quantity, y=supply, mode='lines', name='Supply', line=dict(color='red'))
    )

    # Add equilibrium point
    fig.add_trace(go.Scatter(x=[eqm_qty], y=[eqm_price], mode='markers', name='Equilibrium', marker=dict(color='green', size=15)))

    # Shade the area representing consumer surplus
    fig.add_trace(go.Scatter(
        x=[0, eqm_qty, 0],
        y=[demand_intercept, eqm_price, eqm_price],
        fill='toself',
        fillcolor='rgba(0, 0, 255, 0.2)',  # Light blue color for consumer surplus
        line=dict(color='rgba(255, 255, 255, 0)'),
        name='Consumer Surplus'
    ))

    # Shade the area representing producer surplus
    fig.add_trace(go.Scatter(
        x=[0, eqm_qty, 0],
        y=[eqm_price, eqm_price, supply_intercept],
        fill='toself',
        fillcolor='rgba(255, 0, 0, 0.2)',  # Light red color for producer surplus
        line=dict(color='rgba(255, 255, 255, 0)'),
        name='Producer Surplus'
    ))

    # Update layout
    fig.update_layout(xaxis_title='Quantity', 
                      yaxis_title='Price', yaxis_range=[0, 100])

    return fig, demand_eqn, supply_eqn, P_star, Q_star, CS_star, PS_star
