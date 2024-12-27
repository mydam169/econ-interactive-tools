# Chapter 3. prix plancher / price floor
import dash 
from dash import dcc, html, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc 
import plotly.graph_objects as  go 
import numpy as np 
import pandas as pd 
from .appModules import *

dash.register_page(__name__, name='Price Floor and Ceiling')

layout = html.Div([
    html.H2("Price fixing, welfare and market outcomes"),

    dbc.Row([
        dbc.Col([dcc.Graph(id='price-floor-graph'), 
                 html.Label("Adjust price floor (percent above equilibrium price)"), 
                 dcc.Slider(id='price-floor-slider', min=0, max=0.5, value=0.2, marks={i / 10: f"{i * 10}%" for i in range(0, 11)})], width=6), 
        dbc.Col([dcc.Graph(id='price-ceiling-graph'), 
                 html.Label("Adjust price ceiling (percent of equilibrium price)"),
                 dcc.Slider(id='price-ceiling-slider', min=0, max=1, value=0.7, marks={i / 10: f"{i * 10}%" for i in range(0, 11)})], width=6)
        ]),
    dbc.Row([
        dbc.Col([
            html.H5('Impact of the price floor on welfare and market outcomes'),
            dash_table.DataTable(
                id='df-floor',
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
        ], width=6),
        dbc.Col([
            html.H5('Impact of the price ceiling on welfare and market outcomes'),
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
        ], width=6)
    ])
])

# Set values for demand and supply curves
demand_intercept, demand_slope, supply_intercept, supply_slope = 100, -1, 5, 2


# Callback to update the graph
@callback(
    [Output('price-floor-graph', 'figure'),
    Output('df-floor', 'data')], 
    Input('price-floor-slider', 'value')
)
def update_graph_floor(floor_percent):
    "floor is percent above the equilibrium price"
    # instantiate a linear DS model with a price floor
    mod = PriceFloor(demand_intercept, demand_slope, supply_intercept, supply_slope)
    mod.price_floor = floor_percent
    # Generate data for demand and supply curves
    quantity = np.linspace(0, 100, 100)
    demand = mod.get_P_demand(quantity)
    supply = mod.get_P_supply(quantity)

    # eqm surpluses
    pre_cs = mod.get_CS(mod.q_star, mod.p_star)
    pre_ps = mod.get_PS(mod.q_star, mod.p_star)

    ########### DataTable to document impact of the price  floor ##########
    df = pd.DataFrame(
        {
            'Metric': ['Price', 'Quantity', 'CS', 'PS', 'DWL'], 
            'No intervention':  np.array([mod.p_star, mod.q_star, pre_cs, pre_ps, 0.]).round(2), 
            'With price floor': np.array([mod.p_min, mod.q_floor, mod.CS_floor, mod.PS_floor, mod.DWL_floor]).round(2)
        }
    )

    ########### GRAPH ###########
    fig = go.Figure()

    # Shade the area representing deadweight loss
    P_s = mod.get_P_supply(mod.q_floor)
    fig.add_trace(go.Scatter(
        x=[mod.q_floor, mod.q_star, mod.q_floor],
        y=[mod.p_min, mod.p_star, P_s],
        fill='toself',
        fillcolor='rgba(211, 211, 211, 1)',  # Light gray color for deadweight loss
        line=dict(color='rgba(255, 255, 255, 0)'),
        name='Deadweight Loss'
    ))

    # Shade the area representing consumer surplus
    fig.add_trace(go.Scatter(
        x=[0, mod.q_floor, 0],
        y=[demand_intercept, mod.p_min, mod.p_min],
        fill='toself',
        fillcolor='rgba(0, 0, 255, 0.2)',  # Light blue color for consumer surplus
        line=dict(color='rgba(255, 255, 255, 0)'),
        name='Consumer Surplus'
    ))

    # Shade the area representing producer surplus
    fig.add_trace(go.Scatter(
        x=[0, mod.q_floor, mod.q_floor, 0],
        y=[mod.p_min, mod.p_min, P_s, supply_intercept],
        fill='toself',
        fillcolor='rgba(255, 0, 0, 0.2)',  # Light red color for producer surplus
        line=dict(color='rgba(255, 255, 255, 0)'),
        name='Producer Surplus'
    ))

    # Add supply, demand lines
    fig.add_trace(go.Scatter(x=quantity, 
                             y=demand, 
                             mode='lines', 
                             name='Demand Curve', 
                             line=dict(color='blue'), 
                             showlegend=False)
                            )
    fig.add_trace(go.Scatter(x=quantity, 
                             y=supply, 
                             mode='lines', 
                             name='Supply Curve', 
                             line=dict(color='red'), 
                             showlegend=False)
                            )
    
    # Add initial equilibrium point
    fig.add_trace(go.Scatter(x=[mod.q_star], 
                             y=[mod.p_star], 
                             mode='markers', 
                             name='Initial Equilibrium', 
                             marker=dict(color='green', size=15))
                            )


    # Add dashed lines for initial equilibrium price and quantity
    # fig.add_trace(go.Scatter(
    #     x=[mod.q_star, mod.q_star],
    #     y=[0, mod.p_star],
    #     mode='lines',
    #     line=dict(color='black', dash='dot'),
    #     showlegend=False
    # ))

    # fig.add_trace(go.Scatter(
    #     x=[0, mod.q_star],
    #     y=[mod.p_star, mod.p_star],
    #     mode='lines',
    #     line=dict(color='black', dash='dot'),
    #     showlegend=False
    # ))

    # Add price floor line
    fig.add_trace(
        go.Scatter(x=quantity, y=np.ones(len(quantity))*mod.p_min, 
                   mode='lines', 
                   name='Price floor', 
                   line=dict(color='black'))
    )

    # Update layout
    fig.update_layout(title='Price floor', xaxis_title='Quantity', yaxis_title='Price', yaxis_range=[0, 100])
    
    return fig, df.to_dict('records')

@callback(
    [Output('price-ceiling-graph', 'figure'),
    Output('df-ceiling', 'data')],
    Input('price-ceiling-slider', 'value')
)
def update_graph_ceiling(ceiling):
    "floor is percent above the equilibrium price"
    # instantiate a linear DS model with a price floor
    mod = PriceCeiling(demand_intercept, demand_slope, supply_intercept, supply_slope)
    mod.price_ceiling = ceiling
    # Generate data for demand and supply curves
    quantity = np.linspace(0, 100, 100)
    demand = mod.get_P_demand(quantity)
    supply = mod.get_P_supply(quantity)

    # eqm surpluses
    pre_cs = mod.get_CS(mod.q_star, mod.p_star)
    pre_ps = mod.get_PS(mod.q_star, mod.p_star)

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
    fig.add_trace(go.Scatter(x=quantity, 
                             y=demand, 
                             mode='lines', 
                             name='Demand Curve', 
                             line=dict(color='blue'), 
                             showlegend=False)
                             )
    fig.add_trace(go.Scatter(x=quantity, 
                             y=supply, 
                             mode='lines', 
                             name='Supply Curve', 
                             line=dict(color='red'), 
                             showlegend=False)
                             )
    
    # Add initial equilibrium point
    fig.add_trace(go.Scatter(x=[mod.q_star], 
                             y=[mod.p_star], 
                             mode='markers', 
                             name='Initial Equilibrium', 
                             marker=dict(color='green', size=15))
                             )
    

    # Add new equilibrium point after tax
    # fig.add_trace(go.Scatter(x=[new_equilibrium_quantity], y=[new_equilibrium_price], mode='markers', name='New Equilibrium', marker=dict(color='orange', size=10)))

    # Add dashed lines for initial equilibrium price and quantity
    # fig.add_trace(go.Scatter(
    #     x=[mod.q_star, mod.q_star],
    #     y=[0, mod.p_star],
    #     mode='lines',
    #     line=dict(color='black', dash='dot'),
    #     showlegend=False
    # ))

    # fig.add_trace(go.Scatter(
    #     x=[0, mod.q_star],
    #     y=[mod.p_star, mod.p_star],
    #     mode='lines',
    #     line=dict(color='black', dash='dot'),
    #     showlegend=False
    # ))

    # Add price ceiling line
    fig.add_trace(go.Scatter(
        x=quantity, 
        y=np.ones(len(quantity)) * mod.p_max, 
        mode="lines", 
        line=dict(color='gray'), 
        name="Price ceiling"
    ))

    # Update layout
    fig.update_layout(title='Price ceiling', xaxis_title='Quantity', yaxis_title='Price', yaxis_range=[0, 100])
    
    return fig, df.to_dict('records')

# if __name__ == "__main__":
#   app.run_server(inline=True)
