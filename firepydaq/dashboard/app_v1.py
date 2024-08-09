"""
General imports 
"""
import dash                               
from dash import dcc, html, Input, State, Output, Dash, ctx, ALL, clientside_callback
import dash_daq as daq
import plotly.graph_objects as go
import json
from plotly.subplots import make_subplots
import numpy as np
import os
import time
from datetime import datetime
from ..utilities.PostProcessing import PostProcessData
from threading import Timer
import webbrowser
import logging
from contextlib import redirect_stdout




def create_dash_app(**kwargs):
    """
    Imports Post Processing file and data
    """

    processed_obj = PostProcessData(**kwargs)
    app = Dash(__name__, suppress_callback_exceptions=True)

    # log = logging.getLogger('werkzeug')
    # log.setLevel(logging.WARNING)

    """
    Function that creates plot layouts from a data frame based on processed data available
    """
    def make_layout(df):

        #Stores plots to be rendered 
        plot_divs = []
        rendered_plots = []

        #Create and update new plots on the basis of a data frame
        for i in range(len(df.select("Chart"))):
            if df["Chart"][i] not in rendered_plots and df["Position"][i] == 1:
                rendered_plots.append(df["Chart"][i])
                fig = make_subplots(df["Layout"][i], 1)
                fig.update_layout(
                title_text = df["Chart"][i] + " Graphs"
                )
                for j in range(df["Layout"][i]):
                    fig.add_trace(go.Scatter(), row = j + 1, col = 1)
                plot_divs.append(html.Div(id = {'type': 'plot-layout', 'index' : df["Chart"][i]},
                className = 'sub-layout', style = {'display':'none'}, children = 
                    [dcc.Graph(id =  {'type': 'graphs', 'index' : df["Chart"][i]}, figure = fig, className = 'graphs',
                        responsive = True, style={
                            'height': '35vw',
                            'width': '50vw'
                        })]))

        home_screen_info = html.Div(id = "info_container", className = "info-container")
        home_screen_widgets = []
        #Add Home Screen to help users navigate
        for item in processed_obj.pathdict.keys():
            if item == "datapath":
                home_div = html.Div("Parquet File: " + processed_obj.pathdict[item], id = "data-path", className = "sub-info")
                post_processed_file = processed_obj.pathdict[item].split(".parquet")[0] + "_PostProcessed.parquet"
            if item == "configpath":
                home_div = html.Div("Configuration File: " + processed_obj.pathdict[item], id = "conf-path", className = "sub-info")
            if item == "formulaepath":
                home_div =  html.Div("Formulae File: " + processed_obj.pathdict[item], id = "form-path", className = "sub-info")
            home_screen_widgets.append(home_div)
            home_screen_widgets.append(html.Br(className = "info-br"))

        home_div =  html.Div("Post Processed File: " + post_processed_file, id = "post-path", className = "sub-info")
        home_screen_widgets.append(home_div)
        home_screen_widgets.append(html.Br(className = "info-br"))
        home_screen_info.children = home_screen_widgets
        print(home_screen_info.children)

        plot_divs.append(html.Div(id = {'type': 'plot-layout', 'index' : 'Home'},
            className = 'sub-layout-', style = {'display':'block'}, 
            children = [html.H1("Welcome to your experiment dashboard.", id = {'type': 'header', 'index' : 'home'}), 
                        html.P("Files path of the experiment under visualization:", id = {'type': 'paragraph', 'index' : 'home'}),
                        home_screen_info]))


        return html.Div(id = 'central-layout', className = "main-layout", children = plot_divs)

    """
    Function that creates sidebar layout from a data frame based on processed data available
    """
    def make_sidebar(buttons_list):
        
        #Stores buttons to render
        button_divs = [] 

        #Create button for each unique chart layout 
        for button_id in buttons_list:
            button_divs.append(html.Button(button_id, id = {'type': 'sidebar-btn', 'index' : button_id},
                className = 'button'))
            button_divs.append(html.Br())

        button_divs.append(html.Button('Home', id = {'type': 'sidebar-btn', 'index' : 'Home'},
                className = 'button'))
        
        return html.Div(id = 'sidebar', className = 'sidebar', children = button_divs)
    

    def make_title():
        children_div = []
        header = html.Div(id = 'titlebar-head', className = 'titlebar-head', children = "FIREpydaq Dashboard")
        children_div.append(header)
        header = html.Div(id = 'titlebar-func', className = 'titlebar-tool', children = [

            html.Div(id = 'titlebar-snapshot-container', className = 'titlebar-cont', children = [
                html.Button(id = 'snapshot', className = 'titlebar-btn',
                    children = html.Img(id = "snap", src = "/assets/icons8-graph-50.png")
                )]), html.Br(className = 'titlebar-btn-space'),
            
             html.Div(id = 'titlebar-play-container', className = 'titlebar-cont', children = [
                html.Button(id = 'pause-play', className = 'titlebar-btn',
                    children = html.Img(id = "play", src = "/assets/icons8-pause-48.png")
                )]), html.Br(className = 'titlebar-btn-space'),
                
            html.Div(id = 'titlebar-display-container', className = 'titlebar-cont', children = [
            html.Img(id = "light", src = "/assets/icons8-sun-24.png"),
            daq.BooleanSwitch(id = 'display-switch', className = 'titlebar-btn-toggle'),
            html.Img(id = "dark", src = "/assets/icons8-moon-24.png")
            ])        
        ])
        children_div.append(header)
        return html.Div(id = 'titlebar', className = 'titlebar', children = children_div)

    """
    Function that creates main application layout by parsing configuration files
    """
    def serve_layout():

        #Obtain and read files  
        final_df = processed_obj.All_chart_info.sort("Chart")

        #Creates buttons
        buttons_list = np.unique(final_df.select("Chart").to_numpy().flatten()) 
        sidebar = make_sidebar(buttons_list)
        
        #Creates plot layouts 
        main_layout = make_layout(final_df)

        title_bar = make_title()

        return title_bar, sidebar, main_layout, dcc.Interval(id = "refresh", 
            interval = 1 * 3000, n_intervals = 0), html.Div(id = 'para', style = {'display': 'none'})

    """
    Application Layout helper function called to serve layout
    """
    app.layout = serve_layout

    app.clientside_callback(
        """
        function(data) {
            if (data) {
                document.documentElement.style.setProperty("--main-color", "#2b2b2c");
                document.documentElement.style.setProperty("--bg", "#181818");
                document.documentElement.style.setProperty("--highlight", "#167fca");
                document.documentElement.style.setProperty("--hover", "#605F5F");
                document.documentElement.style.setProperty("--txt", "#E5E4E2");
            } else {
                document.documentElement.style.setProperty("--main-color", "white");
                document.documentElement.style.setProperty("--bg", "#f0f0f0");
                document.documentElement.style.setProperty("--highlight", "#167fca");
                document.documentElement.style.setProperty("--hover", "#c3c3c3");
                document.documentElement.style.setProperty("--txt", "black");
                return "#605F5Fs"
            }
            return "#167fca"
        }
        """,
        Output('display-switch', 'color'),
        Input('display-switch', 'on')
    )

    @app.callback(
            Output('play', 'src'),
            Output('refresh', 'disabled'),
            Input('pause-play', 'n_clicks')
    )
    def switch_pictures(clicks):
        print("Switch")
        if clicks == None:
            return "/assets/icons8-pause-48.png", False
        if clicks % 2 == 0:
            return "/assets/icons8-play-50.png", True
        else:
            return "/assets/icons8-pause-48.png", False
        
    
    @app.callback(
            Output('para', 'style'),
            Input('snapshot', 'n_clicks'),
            Input({'type': 'plot-layout', 'index': ALL}, "children")
    )
    def download(clicks, plots):
        if ctx.triggered_id == "snapshot":
            print("Clicked")
            for plot in plots:
                plot_name = plot[0].get('props', {}).get('id').get('index')
                graph = plot[0].get('props', {}).get('figure')
                fig = go.Figure(graph)
                dir = processed_obj.pathdict["datapath"].split(".parquet")[0] 
                now = datetime.now()
                print(dir + "_" + now.strftime("%Y%m%d_%H%M%S"))
                fig.write_html(dir + "_" + plot_name + ".html")

        return {'display': 'none'}
        

    @app.callback(
            Output('snap', 'style'),
            Output('light', 'style'),
            Output('dark', 'style'),
            Output('play', 'style'),
            Input('display-switch', 'on')
    )
    def switch_pictures(value):
        if value:
            return {'filter': 'invert(1)'}, {'filter': 'invert(1)'}, {'filter': 'invert(1)'}, {'filter': 'invert(1)'}
        return {'filter': 'none'}, {'filter': 'none'}, {'filter': 'none'}, {'filter': 'none'}

    """
    Callback to navigate and render images on click
    Output: Visibility & Rendering of certain plot layouts to DOM
    Input: Clicks on the sidebar layout buttons
    Input: Children of central layout that are plot layouts
    """
    @app.callback(Output({'type': 'plot-layout', 'index': ALL}, "style"),
                Input({'type': 'sidebar-btn', 'index': ALL}, "n_clicks"),
                Input('central-layout', 'children')) 
    def navigate(click_list, layout_children):

        #Array holding styles for each plot layout
        display = [] 

        #Returns display for relevant plot on its button being clicked
        if ctx.triggered:
            input_id = ctx.triggered[0]["prop_id"].split(".")[0]
            button_id = json.loads(input_id)["index"]

            for child in layout_children:
                if child.get('props', {}).get('id').get('index') == button_id:
                    display.append({'display': 'block'})
                else:
                    display.append( {'display': 'none'})
        
        #Stays on the Home screen if not updated
        else:
            for child in layout_children:
                if child.get('props', {}).get('id').get('index') == 'Home':
                    display.append( {'display': 'block'})
                else:
                    display.append( {'display': 'none'})

        return display

    """
    Callback to update plots at a specified interval 
    Output: Updated plots with data appended at each interval
    Input: Interval time period to reload the site
    Input: Children of plot layouts that are graphs
    """    
    @app.callback(
        Output({'type': 'graphs', 'index': ALL}, "figure"),
        Input('refresh', 'n_intervals'),
        Input({'type': 'plot-layout', 'index': ALL}, "children")
    )
    def refresh_graphs(intervals, plots):

        #Hold graphs and plot layouts intermediately 
        updates = {}
        processed_obj = PostProcessData(**kwargs)
        print("Refresh")
        
        #Obtain and load live data
        processed_obj.ScaleData()
        processed_obj.UpdateData()
        processed_data = processed_obj.df_processed
        df = processed_obj.All_chart_info.sort("Chart")

        #Plotting for corresponding charts
        for i in range(len(df.select("Chart"))):
            for plot in plots:
                plot_name = plot[0].get('props', {}).get('id').get('index')
                if plot_name == df["Chart"][i]:

                    #If graph not updated before, generate its layout and plot
                    if df["Chart"][i] not in updates:

                        #Create graph Object
                        graph = plot[0].get('props', {}).get('figure') 
                        graph = go.Figure(graph)
                        graph = make_subplots(df["Layout"][i], 1)
                        label = str(df["Label"][i])
                        
                        #Add chart and axes titles
                        graph.update_layout(
                            title_text = df["Chart"][i] + " Graphs"
                        )
                        graph.update_xaxes(title_text = "Time (s)", row = df["Layout"][i])
                        graph.update_yaxes(title_text = df["Processed_Unit"][i], row = df["Position"][i])
                        #Plot points on graph
                        graph.add_trace(
                            go.Scatter(x = processed_data["Time"],
                            y = processed_data[label], name = label 
                            ), row = df["Position"][i], col = 1
                        ) 

                    #If graph updated before, get updated graph and add traces 
                    else:

                        #Add relevant plot data and axes
                        label = str(df["Label"][i])
                        graph = updates.get(df["Chart"][i])
                        graph.add_trace(
                                go.Scatter(x = processed_data["Time"],
                                y = processed_data[label], name = label
                                ), row = df["Position"][i], col = 1
                        )  
                        graph.update_yaxes(title_text = df["Processed_Unit"][i],row = df["Position"][i])

                    #Store new layout
                    updates[plot_name] = graph
        return list(updates.values())
    
    """
    Opens browser to display link
    """
    def open_browser():
        if not os.environ.get("WERKZEUG_RUN_MAIN"):
            webbrowser.open_new('http://127.0.0.1:1222/')

    """
    Opens browser to display link
    """
    if __name__ == "main":
        return app
    else:
        # with open('yourfile.txt', 'w') as f:
        #     with redirect_stdout(f):
        Timer(1, open_browser).start()
        app.run_server(port=1222)

"""
Runs app on Server
"""
if __name__ == "__main__":
    app = create_dash_app()
    app.run_server(port=1222, debug = True)


