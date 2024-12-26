# Chapter 4. prix plafond / price ceiling
import dash 
from dash import dcc, html, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc 
import plotly.graph_objects as  go 
import numpy as np 
import pandas as pd 
from .appModules import PriceCeiling

# dash.register_page(__name__, name='Price Ceiling')

# app layout
# Layout of the app
layout = html.Div([
    html.H2("Price ceiling, welfare and market outcomes"),

    dbc.Row([dbc.Col([dcc.Graph(id='price-ceiling-graph')], width=11)]),

    dbc.Row([
        dbc.Col([
            html.Label("Adjust Demand Curve Intercept (a):"),
            dcc.Slider(id='demand-intercept-slider', min=50, max=100, value=80, marks={i: str(i) for i in range(50, 101, 10)}),
            
            html.Label("Adjust Demand Curve Slope (b):"),
            dcc.Slider(id='demand-slope-slider', min=-5, max=-0.1, value=-0.5, step=0.1, marks={i: str(i) for i in range(-5, 1, 1)}),
            
            html.Label("Adjust Supply Curve Intercept (c):"),
            dcc.Slider(id='supply-intercept-slider', min=0, max=50, value=10, marks={i: str(i) for i in range(0, 51, 10)}),
            
            html.Label("Adjust Supply Curve Slope (d):"),
            dcc.Slider(id='supply-slope-slider', min=0.1, max=5, value=0.5, step=0.1, marks={i: str(i) for i in range(1, 6)}),
            
            html.Label("Adjust price floor (percent above market price):"),
            dcc.Slider(id='price-ceiling-slider', min=0, max=1, value=0.9, marks={i / 10: str(i / 10) for i in range(0, 11)}),
        ], width=5), 
        dbc.Col([], width=1),
        dbc.Col([
            html.H5('Impact of the price floor on welfare and market outcomes'),
            dash_table.DataTable(
                id='df-ceiling',
                style_cell_conditional=[
                    {
                        'if': {'column_id': 'Metric'}, 
                        'textAlign': 'left'
                    }
                ], 
                style_header={
                    'backgroundColor': '#3366ff', 
                    'fontWeight': 'bold', 
                    'color': 'white'
                }, 
                style_cell={'fontFamily': 'Arial'}, 
                style_as_list_view=True
            )
        ], width=5)
    ])
])

# Callback to update the graph
@callback(
    [Output('price-ceiling-graph', 'figure'),
    Output('df-ceiling', 'data')],
    [Input('demand-intercept-slider', 'value'),
    Input('demand-slope-slider', 'value'),
    Input('supply-intercept-slider', 'value'),
    Input('supply-slope-slider', 'value'),
    Input('price-ceiling-slider', 'value')]
)

def update_graph(demand_intercept, demand_slope, supply_intercept, supply_slope, ceiling):
    "floor is percent above the equilibrium price"
    # instantiate a linear DS model with a price floor
    mod = PriceCeiling(demand_intercept, demand_slope, supply_intercept, supply_slope, ceiling)
    # Generate data for demand and supply curves
    quantity = np.linspace(0, 100, 100)
    demand = mod.get_P_demand(quantity)
    supply = mod.get_P_supply(quantity)

    # eqm surpluses
    pre_cs = mod.get_CS(mod.p_star, mod.q_star)
    pre_ps = mod.get_PS(mod.p_star, mod.q_star)

    ########### DataTable to document impact of the price  floor ##########
    df = pd.DataFrame(
        {
            'Metric': ['Price', 'Quantity', 'CS', 'PS', 'DWL'], 
            'No intervention':  np.array([mod.p_star, mod.q_star, pre_cs, pre_ps, 0.]).round(2), 
            'With price ceiling': np.array([mod.p_max, mod.q_ceiling, mod.CS_ceiling, mod.PS_ceiling, mod.DWL_ceiling]).round(2)
        }
    )

    ########### GRAPH ###########
    fig = go.Figure()

    # Shade the area representing deadweight loss
    P_d = mod.get_P_demand(mod.q_ceiling)
    fig.add_trace(go.Scatter(
        x=[mod.q_ceiling, mod.q_star, mod.q_ceiling],
        y=[P_d, mod.p_star, mod.p_max],
        fill='toself',
        fillcolor='rgba(211, 211, 211, 1)',  # Light gray color for deadweight loss
        line=dict(color='rgba(255, 255, 255, 0)'),
        name='Deadweight Loss'
    ))

    # Shade the area representing consumer surplus
    fig.add_trace(go.Scatter(
        x=[0, mod.q_ceiling, mod.q_ceiling, 0],
        y=[demand_intercept, P_d, mod.p_max, mod.p_max],
        fill='toself',
        fillcolor='rgba(0, 0, 255, 0.2)',  # Light blue color for consumer surplus
        line=dict(color='rgba(255, 255, 255, 0)'),
        name='Consumer Surplus'
    ))

    # Shade the area representing producer surplus
    fig.add_trace(go.Scatter(
        x=[0, mod.q_ceiling, 0],
        y=[mod.p_max, mod.p_max, supply_intercept],
        fill='toself',
        fillcolor='rgba(255, 0, 0, 0.2)',  # Light red color for producer surplus
        line=dict(color='rgba(255, 255, 255, 0)'),
        name='Producer Surplus'
    ))

    # Add supply, demand lines
    fig.add_trace(go.Scatter(x=quantity, y=demand, mode='lines', name='Demand Curve', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=quantity, y=supply, mode='lines', name='Supply Curve', line=dict(color='red')))
    
    # Add initial equilibrium point
    fig.add_trace(go.Scatter(x=[mod.q_star], 
                             y=[mod.p_star], 
                             mode='markers', 
                             name='Initial Equilibrium', 
                             marker=dict(color='green', size=15)))

    # Add new equilibrium point after tax
    # fig.add_trace(go.Scatter(x=[new_equilibrium_quantity], y=[new_equilibrium_price], mode='markers', name='New Equilibrium', marker=dict(color='orange', size=10)))

    # Add dashed lines for initial equilibrium price and quantity
    fig.add_trace(go.Scatter(
        x=[mod.q_star, mod.q_star],
        y=[0, mod.p_star],
        mode='lines',
        line=dict(color='black', dash='dot'),
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=[0, mod.q_star],
        y=[mod.p_star, mod.p_star],
        mode='lines',
        line=dict(color='black', dash='dot'),
        showlegend=False
    ))

    # Update layout
    fig.update_layout(title='', xaxis_title='Quantity', yaxis_title='Price', yaxis_range=[0, 100])
    
    return fig, df.to_dict('records')
