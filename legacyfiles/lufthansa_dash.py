#%%
import dash
from dash import dcc, html, dash_table, callback
import pandas as pd
import numpy as np
from pymongo import MongoClient
import plotly.express as px
from dash.dependencies import Output, Input

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

client = MongoClient(host="localhost", port=27017, authSource="admin")

db = client.flight_info
flights = db.flights

df_1 = pd.read_csv("iata_codes_latlon.csv")

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
)
date = None

app.layout = html.Div(
    [
        html.H1(
            "Arrival Codes by City/IATA",
            style={"textAlign": "center", "color": "#120789", "font-family": "calibri"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            "Please enter the date to search for arrivals. 0 Returns All, Date Format must be YYYY-MM-DD",
                            style={
                                "color": "white",
                                "display": "inline-block",
                                "width": "60%",
                            },
                        ),
                        html.Div(
                            dcc.Input(
                                id="Date_entry", value=date, type="text", debounce=True
                            ),
                            style={"display": "inline-block", "width": "20%"},
                        ),
                    ],
                    style={
                        "display": "inline-block",
                        "width": "30%",
                        "verticalAlign": "middle",
                    },
                ),
                html.Div(
                    dcc.Graph(id="Lufthansa_graph", figure={}),
                    style={
                        "display": "inline-block",
                        "width": "60%",
                        "verticalAlign": "middle",
                    },
                ),
            ]
        ),
    ],
    style={"align": "center", "backgroundColor": "#111111"},
)


@app.callback(
    Output(component_id="Lufthansa_graph", component_property="figure"),
    [
        Input(component_id="Date_entry", component_property="value"),
    ],
)
def update_graph(date):
    if (date is None) or (date == "0") or (date == "All"):

        pipeline = [
            {
                "$match": {
                    "Arrival.AirportCode": {"$in": list(df_1["IATA"])},
                    "Arrival.Scheduled.Date": {"$exists": "true"},
                }
            },
            {
                "$group": {
                    "_id": {
                        "IATA": "$Arrival.AirportCode",
                        "Status Code": "$Status.Code",
                    },
                    "count": {"$sum": 1},
                }
            },
            {"$sort": {"_id": 1}},
            {
                "$project": {
                    "_id": 0,
                    "IATA": "$_id.IATA",
                    "Status Code": "$_id.Status Code",
                    "count": 1,
                }
            },
        ]

        df = pd.DataFrame(list(flights.aggregate(pipeline=pipeline)))
        date = "Full date range"
        return draw_fig(df, df_1, date)
    else:
        print("testing update")
        pipeline = [
            {
                "$match": {
                    "Arrival.AirportCode": {"$in": list(df_1["IATA"])},
                    "Arrival.Scheduled.Date": date,
                }
            },
            {
                "$group": {
                    "_id": {
                        "IATA": "$Arrival.AirportCode",
                        "Status Code": "$Status.Code",
                    },
                    "count": {"$sum": 1},
                }
            },
            {"$sort": {"_id": 1}},
            {
                "$project": {
                    "_id": 0,
                    "IATA": "$_id.IATA",
                    "Status Code": "$_id.Status Code",
                    "count": 1,
                }
            },
        ]

        df = pd.DataFrame(list(flights.aggregate(pipeline=pipeline)))
        print(df.head(20))
        return draw_fig(df, df_1, date)


def draw_fig(df1, df2, date):
    ## We now merge the flight details DF with the city/IATA/latlon information
    dfc = pd.merge(df1, df2, on=["IATA"], how="left")

    ## here comes som magic to turn the arrival codes into extra columns for hover tips
    ## Pivot the table around status codes
    dfcpivot = dfc.pivot_table(index="IATA", columns="Status Code", values="count")

    ## Merge the original table with the pivoted table
    dfc_p = pd.merge(dfc, dfcpivot, on=["IATA"], how="left")

    ## drop the original counts and status codes
    dfc_p.drop(["count", "Status Code"], axis=1, inplace=True)

    ## drop duplicates
    dfc_p.drop_duplicates(inplace=True)

    ## fill the empty columns with 0
    dfc_p.fillna(0, inplace=True)

    ## Very dirty code to ensure that there are full columns for every date
    ## This is to ensure that the hover_data can be populated properly
    ## perhaps there is a way to dynamically populate without doing this?
    if "CD" not in dfc_p:
        dfc_p["CD"] = 0
    if "DL" not in dfc_p:
        dfc_p["DL"] = 0
    if "DV" not in dfc_p:
        dfc_p["DV"] = 0
    if "FE" not in dfc_p:
        dfc_p["FE"] = 0
    if "LD" not in dfc_p:
        dfc_p["LD"] = 0
    if "OT" not in dfc_p:
        dfc_p["OT"] = 0

    ## Finally create a total column as we'll need this for the size of points
    dfc_p["Total"] = dfc_p.iloc[:, 5:].sum(axis=1)
    print(dfc_p.head(20))

    fig = px.scatter_geo(
        dfc_p,
        lat="Lat",
        lon="Lon",
        hover_name="City",
        hover_data={
            "Lat": False,
            "Lon": False,
            "City": False,
            "IATA": True,
            "Total": False,
            "LD": True,
            "FE": True,
            "OT": True,
            "CD": True,
            "DL": True,
            "DV": True,
        },
        color="LD",
        range_color=[min(dfc_p["Total"]), max(dfc_p["Total"])],
        color_continuous_scale=px.colors.sequential.Turbo,
        labels={
            "IATA": "IATA",
            "LD": "Landed",
            "DL": "Delayed",
            "DV": "Diverted",
            "FE": "Flight Early",
            "CD": "Cancelled",
            "OT": "On time",
        },
        size=dfc_p["Total"],
        size_max=20,
        title=date,
        projection="orthographic",
    )

    fig.update_layout(
        width=1300,
        height=900,
    )
    fig.update_geos(
        projection_rotation=dict(
            lon=2.550,
            lat=49.013,
        ),
        center=dict(lon=2.550, lat=49.013),
        lataxis_range=[0, 30],
        lonaxis_range=[-30, 30],
        showcountries=True,
    )
    fig.update_layout(title_x=0.5, font=dict(size=18, color="red"))
    fig.update_yaxes(automargin=True)
    fig.update_geos(
        showland=True, landcolor="LightGreen", showocean=True, oceancolor="LightBlue"
    )
    fig.update_layout(autosize=False, paper_bgcolor="#111111")

    return fig


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=5000)
