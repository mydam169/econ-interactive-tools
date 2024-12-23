import dash
from dash import dcc, html, callback, dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import numpy as np
import pandas as pd


dash.register_page(__name__, name='Tax and welfare')

# Layout of the app
layout = html.Div([
    html.H2("Taxation, welfare and market outcomes"),

    dcc.Graph(id='tax-impact-graph'),

    dbc.Row([
        dbc.Col([

            html.Label("Adjust Demand Curve Intercept (a):"),
            dcc.Slider(id='demand-intercept-slider', min=0, max=100, value=80, marks={i: str(i) for i in range(0, 101, 10)}),
            
            html.Label("Adjust Demand Curve Slope (b):"),
            dcc.Slider(id='demand-slope-slider', min=-5, max=-0.1, value=-0.5, step=0.1, marks={i: str(i) for i in range(-5, 1, 1)}),
            
            html.Label("Adjust Supply Curve Intercept (c):"),
            dcc.Slider(id='supply-intercept-slider', min=0, max=100, value=10, marks={i: str(i) for i in range(0, 101, 10)}),
            
            html.Label("Adjust Supply Curve Slope (d):"),
            dcc.Slider(id='supply-slope-slider', min=0.1, max=5, value=0.5, step=0.1, marks={i: str(i) for i in range(1, 6, 1)}),
            
            html.Label("Adjust Tax Size (T):"),
            dcc.Slider(id='tax-slider', min=0, max=50, value=30, marks={i: str(i) for i in range(0, 51, 10)}),
        ], width=5), 
        dbc.Col([], width=1),
        dbc.Col([
            html.H5('Impact of the tax on welfare and market outcomes'),
            dash_table.DataTable(
                id='comparison-df',
                # columns=[],
                # data=[]
            ),
            html.Div(
                '''Note that the equilibrium price after tax depends on who pays the tax.
                If the tax is on the buyers, the post-tax equilibrium price will be lower.
                If the tax is on the sellers, the post-tax equilibrium price will be higher.
                '''
                )


        ], width=5)
    ])
])

# Callback to update the graph
@callback(
    [Output('tax-impact-graph', 'figure'),
    Output('comparison-df', 'data')],
    [Input('demand-intercept-slider', 'value'),
    Input('demand-slope-slider', 'value'),
    Input('supply-intercept-slider', 'value'),
    Input('supply-slope-slider', 'value'),
    Input('tax-slider', 'value')]
)
def update_graph(demand_intercept, demand_slope, supply_intercept, supply_slope, tax):
    # Generate data for demand and supply curves
    quantity = np.linspace(0, 100, 100)
    demand = demand_intercept + demand_slope * quantity  # Demand curve: P = a + bQ
    supply = supply_intercept + supply_slope * quantity  # Supply curve: P = c + dQ

    # Calculate equilibrium price and quantity
    equilibrium_quantity = (supply_intercept - demand_intercept) / (demand_slope - supply_slope)
    equilibrium_price = demand_intercept + demand_slope * equilibrium_quantity

    # Calculate new quantity after tax (supposed imposed on sellers)
    new_supply_intercept = supply_intercept + tax  # Supply curve shifts up by tax amount
    new_equilibrium_quantity = (new_supply_intercept - demand_intercept) / (demand_slope - supply_slope)
    new_equilibrium_price = demand_intercept + demand_slope * new_equilibrium_quantity
    # new prices
    p_high = demand_intercept + demand_slope * new_equilibrium_quantity
    p_low = supply_intercept + supply_slope * new_equilibrium_quantity
    # Calculate deadweight loss (DWL)
    deadweight_loss = 0.5 * tax * (equilibrium_quantity - new_equilibrium_quantity)

    # CS, PS, Public Rev
    pre_cs = 0.5 * (demand_intercept - equilibrium_price) * equilibrium_quantity
    pre_ps = 0.5 * (equilibrium_price - supply_intercept) * equilibrium_quantity
    gov_rev = tax * new_equilibrium_quantity
    post_cs = 0.5 * (demand_intercept - p_high) * new_equilibrium_quantity
    post_ps = 0.5 * (p_low - supply_intercept) * new_equilibrium_quantity
    
    ########### DataTable to document impact of the tax ##########
    df = pd.DataFrame(
        {
            'Metric': ['Quantity', 'CS', 'PS', 'Tax revenu', 'DWL'],
            'Before tax': np.array([equilibrium_quantity, pre_cs, pre_ps, 0., 0.]).round(2), 
            'After tax': np.array([new_equilibrium_quantity, post_cs, post_ps, gov_rev, deadweight_loss]).round(2)
        }
    )

    ########### GRAPH ###########
    fig = go.Figure()

    # Shade the area representing deadweight loss
    fig.add_trace(go.Scatter(
        x=[new_equilibrium_quantity, equilibrium_quantity, new_equilibrium_quantity],
        y=[new_equilibrium_price, equilibrium_price, new_equilibrium_price - tax],
        fill='toself',
        fillcolor='rgba(211, 211, 211, 1)',  # Light gray color for deadweight loss
        line=dict(color='rgba(255, 255, 255, 0)'),
        name='Deadweight Loss'
    ))

    # Shade the area representing consumer surplus
    fig.add_trace(go.Scatter(
        x=[0, new_equilibrium_quantity, 0],
        y=[demand_intercept, new_equilibrium_price, new_equilibrium_price],
        fill='toself',
        fillcolor='rgba(0, 0, 255, 0.2)',  # Light blue color for consumer surplus
        line=dict(color='rgba(255, 255, 255, 0)'),
        name='Consumer Surplus'
    ))

    # Shade the area representing producer surplus
    fig.add_trace(go.Scatter(
        x=[0, new_equilibrium_quantity, 0],
        y=[new_equilibrium_price - tax, new_equilibrium_price - tax, supply_intercept],
        fill='toself',
        fillcolor='rgba(255, 0, 0, 0.2)',  # Light red color for producer surplus
        line=dict(color='rgba(255, 255, 255, 0)'),
        name='Producer Surplus'
    ))

    # Add supply, demand lines
    fig.add_trace(go.Scatter(x=quantity, y=demand, mode='lines', name='Demand Curve', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=quantity, y=supply, mode='lines', name='Supply Curve', line=dict(color='red')))
    
    # Add initial equilibrium point
    fig.add_trace(go.Scatter(x=[equilibrium_quantity], 
                             y=[equilibrium_price], 
                             mode='markers', 
                             name='Initial Equilibrium', 
                             marker=dict(color='green', size=15)))

    # Add new equilibrium point after tax
    # fig.add_trace(go.Scatter(x=[new_equilibrium_quantity], y=[new_equilibrium_price], mode='markers', name='New Equilibrium', marker=dict(color='orange', size=10)))

    # Add dashed lines for initial equilibrium price and quantity
    fig.add_trace(go.Scatter(
        x=[equilibrium_quantity, equilibrium_quantity],
        y=[0, equilibrium_price],
        mode='lines',
        line=dict(color='black', dash='dot'),
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=[0, equilibrium_quantity],
        y=[equilibrium_price, equilibrium_price],
        mode='lines',
        line=dict(color='black', dash='dot'),
        showlegend=False
    ))

    # Update layout
    fig.update_layout(title='', xaxis_title='Quantity', yaxis_title='Price', yaxis_range=[0, 100])
    
    return fig, df.to_dict('records')