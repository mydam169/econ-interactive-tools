# Shared palette, Plotly template and table style for all pages
import plotly.graph_objects as go
import plotly.io as pio

FONT_FAMILY = "Inter, 'Segoe UI', Arial, sans-serif"

COLORS = {
    'navy': '#0B2545',
    'background': '#F7F8FA',
    'text': '#1F2933',
    'muted': '#6B7280',
    'grid': '#E5E7EB',
    'demand': '#1F5FAD',
    'supply': '#C2410C',
    'dwl': '#6B7280',
    'tax': '#B8860B',
    'policy': '#111827',
}


def rgba(hex_color, alpha):
    "convert a hex color to an rgba string with the given opacity"
    h = hex_color.lstrip('#')
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f'rgba({r}, {g}, {b}, {alpha})'


# Fill styles for the shaded welfare areas, passed to area(...)
NO_LINE = dict(color='rgba(0, 0, 0, 0)')
CS_FILL = dict(fill='toself', fillcolor=rgba(COLORS['demand'], 0.15), line=NO_LINE)
PS_FILL = dict(fill='toself', fillcolor=rgba(COLORS['supply'], 0.15), line=NO_LINE)
TAX_FILL = dict(fill='toself', fillcolor=rgba(COLORS['tax'], 0.25), line=NO_LINE)
DWL_FILL = dict(
    fill='toself',
    fillcolor=rgba(COLORS['dwl'], 0.12),
    fillpattern=dict(shape='/', fgcolor=COLORS['dwl'], size=6, solidity=0.15),
    line=NO_LINE,
)


def area(name, value, fill_style):
    "kwargs for a shaded area that shows 'name: value' when hovered, e.g. go.Scatter(x=.., y=.., **area(...))"
    return dict(fill_style, name=name, mode='lines', hoveron='fills', hoverinfo='text',
                text=f'{name}: {value:.2f}')

DEMAND_LINE = dict(color=COLORS['demand'], width=2.5)
SUPPLY_LINE = dict(color=COLORS['supply'], width=2.5)
POLICY_LINE = dict(color=COLORS['policy'], width=1.5, dash='dash')
GUIDE_LINE = dict(color=COLORS['muted'], width=1, dash='dot')
EQM_MARKER = dict(color=COLORS['policy'], size=9, line=dict(color='white', width=1.5))


# Plotly template applied to every figure by default.
# Only the shaded areas show hover labels (see area()); lines and points are skipped.
pio.templates['econ'] = go.layout.Template(
    data=dict(scatter=[go.Scatter(hoverinfo='skip')]),
    layout=go.Layout(
        font=dict(family=FONT_FAMILY, size=13, color=COLORS['text']),
        title=dict(font=dict(size=15, color=COLORS['navy'], weight='bold'), x=0.5, xanchor='center',
                   y=0.98, yanchor='top'),
        paper_bgcolor='white',
        plot_bgcolor='white',
        colorway=[COLORS['demand'], COLORS['supply'], COLORS['tax'], COLORS['muted']],
        xaxis=dict(gridcolor=COLORS['grid'], linecolor=COLORS['muted'], zeroline=False,
                   ticks='outside', tickcolor=COLORS['grid']),
        yaxis=dict(gridcolor=COLORS['grid'], linecolor=COLORS['muted'], zeroline=False,
                   ticks='outside', tickcolor=COLORS['grid']),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0,
                    bgcolor='rgba(0, 0, 0, 0)', font=dict(size=12)),
        hovermode='closest',
        hoverlabel=dict(font=dict(family=FONT_FAMILY)),
        margin=dict(l=60, r=20, t=60, b=50),
    )
)
pio.templates.default = 'plotly_white+econ'


# Shared DataTable styling, passed to dash_table.DataTable(**TABLE_STYLE)
TABLE_STYLE = dict(
    style_as_list_view=True,
    style_header={
        'backgroundColor': COLORS['navy'],
        'color': 'white',
        'fontWeight': '600',
        'border': 'none',
        'textAlign': 'right',
    },
    style_cell={
        'fontFamily': FONT_FAMILY,
        'fontSize': 14,
        'color': COLORS['text'],
        'padding': '8px 12px',
        'textAlign': 'right',
        'fontVariantNumeric': 'tabular-nums',
        'borderBottom': f"1px solid {COLORS['grid']}",
    },
    style_cell_conditional=[
        {'if': {'column_id': 'Metric'}, 'textAlign': 'left', 'fontWeight': '500'}
    ],
    style_header_conditional=[
        {'if': {'column_id': 'Metric'}, 'textAlign': 'left'}
    ],
)
