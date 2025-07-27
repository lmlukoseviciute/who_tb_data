import os
import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

# === Load Data ===
df = pd.read_csv("data/who_tb_data_agg.csv")

# === Feature Labels for Display ===
feature_labels = {
    "c_newinc": "New Cases Reported",
    "c_per_100k": "Cases per 100k Population",
    "new_ep": "New Extrapulmonary Cases",
    "ret_rel": "Relapse Cases",
    "newrel_hivpos": "New HIV+ TB Cases",
    "c_new_female": "New Female Cases",
    "c_new_male": "New Male Cases",
    "c_new_un": "New Cases Unknown Sex",
    "c_new_female_0_24": "New Female Cases (0–24)",
    "c_new_female_25_44": "New Female Cases (25–44)",
    "c_new_female_45_64": "New Female Cases (45–64)",
    "c_new_female_65": "New Female Cases (65+)",
    "c_new_male_0_24": "New Male Cases (0–24)",
    "c_new_male_25_44": "New Male Cases (25–44)",
    "c_new_male_45_64": "New Male Cases (45–64)",
    "c_new_male_65": "New Male Cases (65+)",
    "c_new_unknown_0_24": "New Cases Unknown Sex (0–24)"
}

# === Plot Function ===
def plot_world_map(df, locations, color, hover_name, animation_frame,
                   title="Global Map", colorbar_title="Cases",
                   color_scale="Viridis", projection_type="natural earth",
                   slider_x=0.2, slider_len=0.6, colorbar_len=0.5,
                   colorbar_thickness=10, colorbar_x=0.9,
                   width=1200, height=700, vmin=None, vmax=None):
    fig = px.choropleth(
        df,
        locations=locations,
        color=color,
        hover_name=hover_name,
        animation_frame=animation_frame,
        color_continuous_scale=color_scale,
        projection=projection_type,
        title=title,
        range_color=(vmin, vmax) if vmin is not None and vmax is not None else None
    )

    fig.update_layout(
        width=width,
        height=height,
        margin=dict(l=0, r=20, t=50, b=0),
        sliders=[{
            "active": 0,
            "x": slider_x,
            "len": slider_len,
        }],
        coloraxis_colorbar=dict(
            title=colorbar_title,
            ticks="outside",
            len=colorbar_len,
            thickness=colorbar_thickness,
            x=colorbar_x
        ),
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type=projection_type,
            landcolor="lightgray"
        ),
        title=dict(
            text=title,
            x=0.5,
            xanchor="center"
        )
    )

    return fig

# === Dash App ===
external_stylesheets = [
    "/assets/main.css",
    "/assets/fontawesome-all.min.css",
    "/assets/noscript.css"
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server  # for Render

app.title = "TB Dashboard"

app.layout = html.Div(
    className="dashboard-container",
    children=[
        html.H1("Global Tuberculosis Dashboard", className="main-title"),

        html.Label("Select TB Feature:", className="select-label"),
        dcc.Dropdown(
            id="feature-dropdown",
            options=[{"label": label, "value": col} for col, label in feature_labels.items()],
            value="c_newinc",
            className="dropdown"
        ),

        dcc.Loading(
            dcc.Graph(id="world-map"),
            type="circle",
            className="loading-spinner"
        )
    ]
)

@app.callback(
    Output("world-map", "figure"),
    Input("feature-dropdown", "value")
)
def update_world_map(selected_feature):
    valid_years = (
        df.groupby("year")[selected_feature]
        .apply(lambda x: x.notna().any())
    )
    filtered_df = df[df["year"].isin(valid_years[valid_years].index)]

    if filtered_df.empty:
        return px.scatter(title="No data available for selected feature.")

    vmin = 0
    vmax = filtered_df[selected_feature].dropna().quantile(0.99)
    readable_title = feature_labels[selected_feature]

    fig = plot_world_map(
        df=filtered_df,
        locations="iso3",
        color=selected_feature,
        hover_name="country",
        animation_frame="year",
        title=f"Global TB Map for {readable_title}",
        vmin=vmin,
        vmax=vmax,
        colorbar_title=readable_title
    )
    return fig

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8050)))
