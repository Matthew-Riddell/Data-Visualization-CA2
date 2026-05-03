# Matthew Riddell
# D00245674
# Data Visualization & Insight CA3
# Sjiny app for Bikesharing in Dublin City Center

# Code sourced from:
# Exercise code (shiny part 2 and part 3)
# https://shiny.posit.co/py/docs/overview.html
# https://shiny.posit.co/py/api/express/reactive.calc.html

from shiny import App, ui, render, reactive
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from shinywidgets import render_widget, output_widget
from ipyleaflet import Map, Marker, basemaps, basemap_to_tiles
from ipywidgets import HTML

# load the datasets
hourly = pd.read_csv("C:/Users/Matty/Documents/College Notes & Assignments/Year 5/Data Visualisation and Insight/CAs/CA2/Data-Visualization-CA2/code/hourly.csv")
station_hour = pd.read_csv("C:/Users/Matty/Documents/College Notes & Assignments/Year 5/Data Visualisation and Insight/CAs/CA2/Data-Visualization-CA2/code/station_hour.csv")
daily = pd.read_csv("C:/Users/Matty/Documents/College Notes & Assignments/Year 5/Data Visualisation and Insight/CAs/CA2/Data-Visualization-CA2/code/daily.csv")
station = pd.read_csv("C:/Users/Matty/Documents/College Notes & Assignments/Year 5/Data Visualisation and Insight/CAs/CA2/Data-Visualization-CA2/code/station_summary.csv")
week = pd.read_csv("C:/Users/Matty/Documents/College Notes & Assignments/Year 5/Data Visualisation and Insight/CAs/CA2/Data-Visualization-CA2/code/week.csv")

# interactive map 
# adapted from exercise code
def create_map(df):
    center_lat = df["LATITUDE"].mean()
    center_lon = df["LONGITUDE"].mean()

    m = Map(
        center=(center_lat, center_lon),
        zoom=12,
        basemap=basemap_to_tiles(basemaps.OpenStreetMap.Mapnik),
        scroll_wheel_zoom=True
    )

    for _, row in df.iterrows():
        popup_html = HTML(
            f"<b>{row['NAME']}</b><br>"
            f"Avg bikes: {round(row['AVAILABLE_BIKES'], 0)}"
        )

        marker = Marker(location=(row["LATITUDE"], row["LONGITUDE"]))
        marker.popup = popup_html
        m.add_layer(marker)

    return m


# plotly plots
def plot_daily():
    fig = px.line(daily, x="DATE", y="AVAILABLE_BIKES",
                  title="Daily Available Bikes")
    fig.update_layout(template="plotly_white")
    return fig


def plot_hourly():
    fig = px.line(hourly, x="HOUR", y="AVAILABLE_BIKES",
                  title="Hourly Pattern")
    fig.update_layout(template="plotly_white")
    return fig


def plot_station(df):
    fig = px.bar(df, x="NAME", y="AVAILABLE_BIKES",
                 title="Average Bikes per Station")
    fig.update_layout(template="plotly_white", xaxis_tickangle=-45)
    return fig


# week plot
def plot_week(df):
    fig, ax = plt.subplots()

    df = df.copy()

    for label, g in df.groupby("IS_WEEKEND"):
        name = "Weekend" if label == 1 else "Weekday"
        ax.plot(g["HOUR"], g["AVAILABLE_BIKES"], label=name)

    ax.set_title("Weekday vs Weekend Pattern")
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
                ui.h1("Matthew's Dublin Bikesharing Dashboard"),
                ui.p("A quick tool to see if there are any bikes available near you!"),

                ui.hr(),

                ui.h3("Features"),
                ui.tags.ul(
                    ui.tags.li("Interactive bike station map"),
                    ui.tags.li("Observe daily & hourly trends"),
                    ui.tags.li("Observe weekday vs weekend patterns"),
                    ui.tags.li("Station by station analysis")
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
                        ui.div(output_widget("daily_dash"), class_="card")
                    ),

                    ui.layout_columns(
                        ui.div(output_widget("hourly_dash"), class_="card"),
                        ui.div(ui.output_plot("week_dash"), class_="card")
                    ),

                    ui.div(output_widget("station_dash"), class_="card"),

                    width=9
                )
            )
        ),

        # navbar for the pages
        ui.nav_panel("Map", ui.card(output_widget("map_page"))),
        ui.nav_panel("Daily", ui.card(output_widget("daily_page"))),
        ui.nav_panel("Hourly", ui.card(output_widget("hourly_page"))),
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

    # maps
    @output
    @render_widget
    def map_dash():
        return create_map(filtered_station())

    @output
    @render_widget
    def map_page():
        return create_map(filtered_station())

    # Daily plots
    @output
    @render_widget
    def daily_dash():
        return plot_daily()

    @output
    @render_widget
    def daily_page():
        return plot_daily()

    # Hourly plots
    @output
    @render_widget
    def hourly_dash():
        return plot_hourly()

    @output
    @render_widget
    def hourly_page():
        return plot_hourly()

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


    # Table for Stations under the dashboard dropdown
    @output
    @render.table
    def station_table():
        if input.station_select() == "All":
            return pd.DataFrame()  # hides the table if none are selected

        df = filtered_station()[["NAME", "AVAILABLE_BIKES", "LATITUDE", "LONGITUDE"]]
        return df


# launch the app
app = App(app_ui, server)