# Chapter 3. prix plancher / price floor
import dash 
from dash import dcc, html, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc 
import plotly.graph_objects as  go 
import numpy as np 
import pandas as pd 
from .appModules import *
from .theme import *

dash.register_page(__name__, path="/price-floor-ceiling", name="Price floor and ceiling")

layout = html.Div([
    html.H2("Price fixing, welfare and market outcomes"),

    dbc.Row([
        dbc.Col([dcc.Graph(id='price-floor-graph'), 
                 html.Label("Adjust price floor (percent above equilibrium price)"), 
                 dcc.Slider(id='price-floor-slider', min=0, max=0.5, value=0.2, marks={i / 10: f"{i * 10}%" for i in range(0, 11)})], width=6), 
        dbc.Col([dcc.Graph(id='price-ceiling-graph'), 
                 html.Label("Adjust price ceiling (percent of equilibrium price)"),
                 dcc.Slider(id='price-ceiling-slider', min=0, max=1, step=0.01, value=0.5, marks={0: "0", 0.25: "0.25", 0.5: "0.5", 0.75: "0.75", 1: "1"})], width=6)
        ]),
    dbc.Row([
        dbc.Col([
            html.H5('Impact of the price floor on welfare and market outcomes'),
            dash_table.DataTable(
                id='df-floor',
                **TABLE_STYLE
            )
        ], width=6),
        dbc.Col([
            html.H5('Impact of the price ceiling on welfare and market outcomes'),
            dash_table.DataTable(
                id='df-ceiling',
                **TABLE_STYLE
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
        **area('Deadweight Loss', mod.DWL_floor, DWL_FILL)
    ))

    # Shade the area representing consumer surplus
    fig.add_trace(go.Scatter(
        x=[0, mod.q_floor, 0],
        y=[demand_intercept, mod.p_min, mod.p_min],
        **area('Consumer Surplus', mod.CS_floor, CS_FILL)
    ))

    # Shade the area representing producer surplus
    fig.add_trace(go.Scatter(
        x=[0, mod.q_floor, mod.q_floor, 0],
        y=[mod.p_min, mod.p_min, P_s, supply_intercept],
        **area('Producer Surplus', mod.PS_floor, PS_FILL)
    ))

    # Add supply, demand lines
    fig.add_trace(go.Scatter(x=quantity, 
                             y=demand, 
                             mode='lines', 
                             name='Demand Curve', 
                             line=DEMAND_LINE,
                             showlegend=False)
                            )
    fig.add_trace(go.Scatter(x=quantity, 
                             y=supply, 
                             mode='lines', 
                             name='Supply Curve', 
                             line=SUPPLY_LINE,
                             showlegend=False)
                            )
    
    # Add initial equilibrium point
    fig.add_trace(go.Scatter(x=[mod.q_star], 
                             y=[mod.p_star], 
                             mode='markers', 
                             name='Initial Equilibrium', 
                             marker=EQM_MARKER)
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
                   line=POLICY_LINE)
    )

    # Update layout
    fig.update_layout(title='Price floor', xaxis_title='Quantity', yaxis_title='Price', yaxis_range=[0, 100],
                      margin=dict(t=100))
    
    return fig, df.to_dict('records')

@callback(
    [Output('price-ceiling-graph', 'figure'),
    Output('df-ceiling', 'data')],
    Input('price-ceiling-slider', 'value')
)
def update_graph_ceiling(ceiling):
    "floor is percent above the equilibrium price"
    # instantiate a linear DS model with a price floor
    mod = PriceCeiling(demand_intercept, demand_slope, supply_intercept, supply_slope, ceiling)
    # mod.price_ceiling = ceiling
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
        **area('Deadweight Loss', mod.DWL_ceiling, DWL_FILL)
    ))

    # Shade the area representing consumer surplus
    fig.add_trace(go.Scatter(
        x=[0, mod.q_ceiling, mod.q_ceiling, 0],
        y=[demand_intercept, P_d, mod.p_max, mod.p_max],
        **area('Consumer Surplus', mod.CS_ceiling, CS_FILL)
    ))

    # Shade the area representing producer surplus
    fig.add_trace(go.Scatter(
        x=[0, mod.q_ceiling, 0],
        y=[mod.p_max, mod.p_max, supply_intercept],
        **area('Producer Surplus', mod.PS_ceiling, PS_FILL)
    ))

    # Add supply, demand lines
    fig.add_trace(go.Scatter(x=quantity, 
                             y=demand, 
                             mode='lines', 
                             name='Demand Curve', 
                             line=DEMAND_LINE,
                             showlegend=False)
                             )
    fig.add_trace(go.Scatter(x=quantity, 
                             y=supply, 
                             mode='lines', 
                             name='Supply Curve', 
                             line=SUPPLY_LINE,
                             showlegend=False)
                             )
    
    # Add initial equilibrium point
    fig.add_trace(go.Scatter(x=[mod.q_star], 
                             y=[mod.p_star], 
                             mode='markers', 
                             name='Initial Equilibrium', 
                             marker=EQM_MARKER)
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
        line=POLICY_LINE,
        name="Price ceiling"
    ))

    # Update layout
    fig.update_layout(title='Price ceiling', xaxis_title='Quantity', yaxis_title='Price', yaxis_range=[0, 100],
                      margin=dict(t=100))
    
    return fig, df.to_dict('records')

# if __name__ == "__main__":
#   app.run_server(inline=True)
