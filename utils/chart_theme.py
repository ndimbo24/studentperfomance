"""
chart_theme.py
--------------
Single source of truth for Plotly chart styling so every chart in the
app looks consistent (same fonts, colors, hover style) without every
page re-declaring layout options.
"""

import plotly.graph_objects as go

COLORWAY = [
    "#4C6FFF",  # primary blue
    "#22C55E",  # success green
    "#F59E0B",  # warning amber
    "#EC4899",  # pink
    "#06B6D4",  # cyan
    "#8B5CF6",  # violet
    "#EF4444",  # red
]

FONT_FAMILY = "'Inter', 'Segoe UI', system-ui, sans-serif"


def apply_theme(fig: go.Figure, title: str | None = None, height: int = 380) -> go.Figure:
    """Apply consistent layout/theme settings to a Plotly figure in place
    and return it (so it can be used inline: `return apply_theme(fig)`)."""
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, family=FONT_FAMILY, color="#1F2937"))
        if title
        else None,
        font=dict(family=FONT_FAMILY, size=12, color="#4B5563"),
        colorway=COLORWAY,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=20, t=title and 50 or 20, b=40),
        height=height,
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family=FONT_FAMILY,
            bordercolor="#E5E7EB",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11),
        ),
        xaxis=dict(gridcolor="#F1F5F9", zeroline=False),
        yaxis=dict(gridcolor="#F1F5F9", zeroline=False),
        autosize=True,
    )
    return fig


def empty_figure(message: str = "No data available for the selected filters") -> go.Figure:
    """A blank, styled figure with a centered message - used whenever a
    filter combination produces zero rows, instead of an error or a
    confusing blank chart."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=14, color="#9CA3AF", family=FONT_FAMILY),
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return apply_theme(fig, height=320)
