# Matthew Riddell
# D00245674
# Data Visualization & Insight CA3
# Shiny app for Bikesharing in Dublin City Center

# Code references:
# Exercise code (shiny part 2 and part 3)
# https://shiny.posit.co/py/docs/overview.html
# https://shiny.posit.co/py/api/express/reactive.calc.html
# https://ipyleaflet.readthedocs.io/en/latest/layers/circle_marker.html
# https://chatgpt.com/share/69f8cbd0-2b4c-83eb-8b7c-246bdec5fd56
# https://chatgpt.com/share/69f8cba2-3cfc-83eb-b194-7fc82f36a9ff

from shiny import App, ui, render, reactive
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from shinywidgets import render_widget, output_widget
from ipyleaflet import Map, CircleMarker, Marker, basemaps, basemap_to_tiles
from ipywidgets import HTML

# load the datasets
hourly = pd.read_csv("hourly.csv")
station_hour = pd.read_csv("station_hour.csv")
daily = pd.read_csv("daily.csv")
station = pd.read_csv("station_summary.csv")
week = pd.read_csv("week.csv")

# interactive map 
# adapted from exercise code
def create_map(df):
    center_lat = df["LATITUDE"].mean()
    center_lon = df["LONGITUDE"].mean()

    df = df.copy()
    df["RATIO"] = df["AVAILABLE_BIKES"] / df["BIKE_STANDS"]

    m = Map(
        center=(center_lat, center_lon),
        zoom=13,
        basemap=basemap_to_tiles(basemaps.OpenStreetMap.Mapnik),
        scroll_wheel_zoom=True
    )

    for _, row in df.iterrows():

        bikes = row["AVAILABLE_BIKES"]
        capacity = row["BIKE_STANDS"]
        ratio = row["RATIO"]

        # # icon is a different colour based on the number of available bikes
        if ratio < 0.3:
            color = "red"
        elif ratio < 0.7:
            color = "orange"
        else:
            color = "green"

        popup_html = HTML(
            f"<b>{row['NAME']}</b><br>"
            f"Available bikes: {int(round(bikes))} / Capacity: {int(capacity)}"
        )

        radius = int(4 + (ratio * 10))

        # https://ipyleaflet.readthedocs.io/en/latest/layers/circle_marker.html
        # creates a cirular marker on the map
        marker = CircleMarker(
            location=(row["LATITUDE"], row["LONGITUDE"]),
            radius=radius,
            color=color,
            fill_color=color,
            fill_opacity=0.8
        )

        marker.popup = popup_html
        m.add_layer(marker)

    return m


# plotly plots
def plot_daily(df):
    fig = px.line(
        df,
        x="DATE",
        y="AVAILABLE_BIKES",
        title="Daily Available Bikes (City-wide)",
        labels={
            "DATE": "Date",
            "AVAILABLE_BIKES": "Available bikes"
        }
    )
    fig.update_layout(template="plotly_white")
    return fig


def plot_hourly(df):
    fig = px.line(
        df,
        x="HOUR",
        y="AVAILABLE_BIKES",
        title="Hourly Pattern",
        labels={
            "HOUR": "Hour of day",
            "AVAILABLE_BIKES": "Available bikes"
        }
    )
    fig.update_layout(template="plotly_white")
    return fig


def plot_station(df):
    fig = px.bar(df, x="NAME", y="AVAILABLE_BIKES",
                 title="Average Bikes per Station",
                 labels={
            "NAME": "Station",
            "AVAILABLE_BIKES": "Available bikes"
        })
    fig.update_layout(template="plotly_white", xaxis_tickangle=-45)
    return fig


# week plot
def plot_week(df):
    fig, ax = plt.subplots()

    df = df.copy()

    for label, g in df.groupby("IS_WEEKEND"):
        name = "Weekend" if label == 1 else "Weekday"
        ax.plot(g["HOUR"], g["AVAILABLE_BIKES"], label=name)

    ax.set_title("Weekday vs Weekend Pattern (City-wide)")
    ax.legend()
    ax.grid(True, alpha=0.3)

    return fig


# UI
app_ui = ui.page_fluid(

    # CSS styling
    ui.tags.style("""
        body {
            background-color: #2c3e50;
            color: white;
        }

        .navbar {
            background-color: #1f2d3a !important;
        }

        .navbar a {
            color: white !important;
        }

        .sidebar {
            background-color: #1f2d3a;
            color: white;
            padding: 20px;
            height: 100%;
            border-radius: 12px;
        }

        .card {
            background: #34495e;
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
            margin-bottom: 20px;
            color: white;
        }

        h1, h2, h3, h4 {
            color: white;
        }
    """),

    ui.page_navbar(

        # home page
        ui.nav_panel(
            "Home",
            ui.div(

                ui.h1("Dublin Bike Sharing Dashboard"),

                ui.p(
                    "This dashboard is designed to help commuters better plan trips through dublin city center using the Bike Sharing Program. "
                    "Using this tools, users can observe bikesharing behavioral trends hourly, daily, weekday vs weekend, city-wide vs station specific. "
                    "Using the map, users can navigate to each station and view the average availability for each time of the day, colour-coded to illustrate which stations have more available bikes at any given time. "
                ),

                ui.p(
                    "This tool will inform commuters and city planning aswell as the bikesharing program. "
                    "Knowing when a station is more available, informs the commuter and allows them to better plan their commute at a time when bikes are more available. "
                    "City planners can use this tool to find areas on the map where coverage is low, allowing them to plan the development of more bike stations in the future. "
                    "The bike sharing program itself can see trends and address availability issues by upgrading bike stations that have low capacity. "
                ),

                ui.hr(),

                ui.h3("Features"), 
                ui.tags.ul( 
                    ui.tags.li("Interactive bike station map"), 
                    ui.tags.li("Observe daily & hourly trends"), 
                    ui.tags.li("Observe weekday vs weekend patterns"), 
                    ui.tags.li("Station by station analysis") 
                    ),

                ui.hr(),

                ui.h3("Data Sources"),

                ui.p(
                    "The data used in this dashboard was modelled and transformed using the Dublin City Center bikesharing Dataset"
                ),

                ui.tags.ul(
                    ui.tags.li(
                        ui.a(
                            "GitHub Repository",
                            href="https://github.com/Matthew-Riddell/Data-Visualization-CA2",
                            target="_blank"
                        )
                    ),
                    ui.tags.li(
                        ui.a(
                            "Dataset Source",
                            href="https://www.kaggle.com/datasets/mexwell/dublinbikes-dcc-dataset",
                            target="_blank"
                        )
                    )
                ),

                ui.hr(),

                ui.p(
                    "Matthew Riddell - Data Visualization & Insight CA2."
                )
            )
        ),

        # dashboard
        ui.nav_panel(
            "Dashboard",

            ui.layout_columns(

                # dashboard side bar
                ui.div(

                    ui.h3("Filters"),

                    ui.input_select(
                        "station_select",
                        "Station",
                        choices=["All"] + sorted(station["NAME"].unique()),
                        selected="All"
                    ),

                    # station table
                    ui.output_table("station_table"),

                    class_="sidebar",
                    width=3
                ),

                # main dashboard
                ui.div(

                    ui.h2("Overview"),

                    ui.layout_columns(
                        ui.div(output_widget("map_dash"), class_="card"),
                        ui.div(output_widget("hourly_dash"), class_="card")
                    ),

                    ui.layout_columns(
                        ui.div(output_widget("daily_dash"), class_="card"),
                        ui.div(ui.output_plot("week_dash"), class_="card")
                    ),

                    ui.div(output_widget("station_dash"), class_="card"),

                    width=9
                )
            )
        ),

        # navbar for the pages
        ui.nav_panel(
            "Map",
            ui.card(

                ui.h3("Bike Availability by Time"),

                ui.input_slider(
                    "hour_slider",
                    "Select Hour",
                    min=0,
                    max=23,
                    value=12,
                    step=1
                ),

                ui.output_text("selected_time"),

                output_widget("map_page")
            )
        ),

        ui.nav_panel("Hourly", ui.card(output_widget("hourly_page"))),
        ui.nav_panel("Daily", ui.card(output_widget("daily_page"))),
        ui.nav_panel("Week", ui.card(ui.output_plot("week_page"))),
        ui.nav_panel("Stations", ui.card(output_widget("station_page")))
    )
)


# server
def server(input, output, session):

    # station dropdown filter
    @reactive.calc
    def filtered_station():
        if input.station_select() == "All":
            return station
        return station[station["NAME"] == input.station_select()]
    
    # hour slider for map
    @output
    @render.text
    def selected_time():
        return f"Selected Time: {input.hour_slider():02d}:00"
    

    @reactive.calc
    def map_data():

        # start from hourly station data
        df = station_hour.copy()

        # filter selected hour
        df = df[df["HOUR"] == input.hour_slider()]

        # aggregate bikes per station at that hour
        df = df.groupby(
            ["STATION ID", "NAME"],
            as_index=False
        )["AVAILABLE_BIKES"].mean()

        # merge with station summary 
        df = df.merge(
            station[["STATION ID", "LATITUDE", "LONGITUDE", "BIKE_STANDS"]],
            on="STATION ID",
            how="left"
        )

        return df
    

    @reactive.calc
    def hourly_data():
        df = station_hour.copy()

        # station-specific 
        if input.station_select() != "All":
            df = df[df["NAME"] == input.station_select()]
            return df.groupby("HOUR", as_index=False)["AVAILABLE_BIKES"].mean()

        # ALL stations
        df = df.groupby("HOUR", as_index=False)["AVAILABLE_BIKES"].mean()

        return df
    
    @reactive.calc
    def daily_data():
        return daily.copy()
        

    # maps
    @output
    @render_widget
    def map_dash():
        return create_map(filtered_station())

    @output
    @render_widget
    def map_page():
        return create_map(map_data())

    # Daily plots
    @output
    @render_widget
    def daily_dash():
        return plot_daily(daily_data())

    @output
    @render_widget
    def daily_page():
        return plot_daily(daily_data())

    # Hourly plots
    @output
    @render_widget
    def hourly_dash():
        return plot_hourly(hourly_data())

    @output
    @render_widget
    def hourly_page():
        return plot_hourly(hourly_data())

    # Week plots
    @output
    @render.plot
    def week_dash():
        return plot_week(week)

    @output
    @render.plot
    def week_page():
        return plot_week(week)

    # Station plots
    @output
    @render_widget
    def station_dash():
        return plot_station(filtered_station())

    @output
    @render_widget
    def station_page():
        return plot_station(filtered_station())


    # reactive function for the table to show times and avg available bikes
    @reactive.calc
    def station_hour_table():
        if input.station_select() == "All":
            return pd.DataFrame()

        df = station_hour.copy()

        # filter selected station
        df = df[df["NAME"] == input.station_select()]

        # merge capacity
        df = df.merge(
            station[["STATION ID", "BIKE_STANDS"]],
            on="STATION ID",
            how="left"
        )

        # group by station + hour
        df = (
            df.groupby(["NAME", "HOUR", "BIKE_STANDS"], as_index=False)
            ["AVAILABLE_BIKES"]
            .mean()
        )

        # format time
        df["TIME"] = df["HOUR"].apply(lambda x: f"{int(x):02d}:00")

        # round values
        df["AVAILABLE_BIKES"] = df["AVAILABLE_BIKES"].round(0).astype(int)
        df["BIKE_STANDS"] = df["BIKE_STANDS"].astype(int)

        # reorder columns
        df = df[["NAME", "TIME", "AVAILABLE_BIKES", "BIKE_STANDS"]]

        df.columns = [
        "Station",
        "Time",
        "Available Bikes",
        "Capacity"
        ]

        return df
    

    # Table for Stations under the dashboard dropdown
    @output
    @render.table
    def station_table():
        return station_hour_table()


# launch the app
app = App(app_ui, server)