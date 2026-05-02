from shiny import App, ui, render, reactive
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from shinywidgets import render_widget, output_widget
from ipyleaflet import Map, Marker, basemaps, basemap_to_tiles
from ipywidgets import HTML

hourly = pd.read_csv("C:/Users/Matty/Documents/College Notes & Assignments/Year 5/Data Visualisation and Insight/CAs/CA2/Data-Visualization-CA2/code/hourly.csv")
station_hour = pd.read_csv("C:/Users/Matty/Documents/College Notes & Assignments/Year 5/Data Visualisation and Insight/CAs/CA2/Data-Visualization-CA2/code/station_hour.csv")
daily = pd.read_csv("C:/Users/Matty/Documents/College Notes & Assignments/Year 5/Data Visualisation and Insight/CAs/CA2/Data-Visualization-CA2/code/daily.csv")
station = pd.read_csv("C:/Users/Matty/Documents/College Notes & Assignments/Year 5/Data Visualisation and Insight/CAs/CA2/Data-Visualization-CA2/code/station_summary.csv")
week = pd.read_csv("C:/Users/Matty/Documents/College Notes & Assignments/Year 5/Data Visualisation and Insight/CAs/CA2/Data-Visualization-CA2/code/week.csv")

def create_map(station):
    center_lat = station["LATITUDE"].mean()
    center_lon = station["LONGITUDE"].mean()

    m = Map(
        center=(center_lat, center_lon),
        zoom=12,
        basemap=basemap_to_tiles(basemaps.OpenStreetMap.Mapnik),
        scroll_wheel_zoom=True
    )

    for _, row in station.iterrows():
        lat = row["LATITUDE"]
        lon = row["LONGITUDE"]
        bikes = round(row["AVAILABLE_BIKES"], 0)
        names = row["NAME"]

        popup_html = HTML(
            f"<b>Bike Station:</b> {names} <br>"
            f"<b>Available bikes (Avg):</b> {bikes}"
        )

        marker = Marker(
            location=(lat, lon),
            draggable=False
        )
        marker.popup = popup_html

        m.add_layer(marker)

    return m

app_ui = ui.page_navbar(
    ui.nav_panel("Bike Stations Map", output_widget("map_widget")),
    ui.nav_panel("Daily Trend", ui.output_plot("daily_plot")),
    ui.nav_panel("Hourly Pattern", ui.output_plot("hourly_plot")),
    ui.nav_panel("Week Effect", ui.output_plot("week_plot")),
    ui.nav_panel("Station Overview", ui.output_plot("station_plot")),
    ui.nav_panel("Station Hour Detail", ui.output_table("station_table"))
)

def server(input, output, session):

    @output
    @render_widget
    def map_widget():
        return create_map(station)

    @output
    @render.plot
    def daily_plot():
        fig, ax = plt.subplots()
        ax.plot(pd.to_datetime(daily["DATE"]), daily["AVAILABLE_BIKES"])
        ax.set_title("Daily Available Bikes")
        return fig
    
    
    @output
    @render.plot
    def hourly_plot():
        fig, ax = plt.subplots()
        ax.plot(hourly["HOUR"], hourly["AVAILABLE_BIKES"])
        ax.set_title("Hourly Pattern")
        return fig
    

    @output
    @render.plot
    def week_plot():
        fig, ax = plt.subplots()

        for label, df in week.groupby("IS_WEEKEND"):
            ax.plot(df["HOUR"], df["AVAILABLE_BIKES"], label=str(label))

        ax.legend()
        ax.set_title("Weekday vs Weekend Pattern")
        return fig
    
    @output
    @render.plot
    def station_plot():
        fig, ax = plt.subplots()
        ax.bar(station["NAME"], station["AVAILABLE_BIKES"])
        ax.set_title("Average Bikes per Station")
        ax.tick_params(axis='x', rotation=90)
        return fig
    
    
    
    @output
    @render.table
    def station_table():
        df = station_hour.copy()
        df["AVAILABLE_BIKES"] = df["AVAILABLE_BIKES"].astype(int)
        return df

app = App(app_ui, server)