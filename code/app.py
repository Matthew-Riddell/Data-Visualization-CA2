from shiny import App, ui, render, reactive
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

hourly = pd.read_csv("C:/Users/Matty/Documents/College Notes & Assignments/Year 5/Data Visualisation and Insight/CAs/CA2/Data-Visualization-CA2/code/hourly.csv")
station_hour = pd.read_csv("C:/Users/Matty/Documents/College Notes & Assignments/Year 5/Data Visualisation and Insight/CAs/CA2/Data-Visualization-CA2/code/station_hour.csv")
daily = pd.read_csv("C:/Users/Matty/Documents/College Notes & Assignments/Year 5/Data Visualisation and Insight/CAs/CA2/Data-Visualization-CA2/code/daily.csv")
station = pd.read_csv("C:/Users/Matty/Documents/College Notes & Assignments/Year 5/Data Visualisation and Insight/CAs/CA2/Data-Visualization-CA2/code/station_summary.csv")
week = pd.read_csv("C:/Users/Matty/Documents/College Notes & Assignments/Year 5/Data Visualisation and Insight/CAs/CA2/Data-Visualization-CA2/code/week.csv")

app_ui = ui.page_navbar(
    ui.nav_panel("Daily Trend", ui.output_plot("daily_plot")),
    ui.nav_panel("Hourly Pattern", ui.output_plot("hourly_plot")),
    ui.nav_panel("Week Effect", ui.output_plot("week_plot")),
    ui.nav_panel("Station Overview", ui.output_plot("station_plot")),
    ui.nav_panel("Station Hour Detail", ui.output_table("station_table"))
)

def server(input, output, session):

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
        return station_hour

app = App(app_ui, server)