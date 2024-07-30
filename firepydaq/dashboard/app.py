"""
General imports 
"""
import dash                                 
from dash import dcc, html, Input, Output, Dash, ctx, ALL
import plotly.graph_objects as go
import json
from plotly.subplots import make_subplots
import numpy as np
import sys
import os
from ..utilities.PostProcessing import PostProcessData
from threading import Timer
import webbrowser



def create_dash_app(**kwargs):
    """
    Imports Post Processing file and data
    """
    my_json_file = kwargs["jsonpath"]
    processed_obj = PostProcessData(jsonpath = my_json_file)
    app = Dash(__name__, suppress_callback_exceptions=True)

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
                title_text = df["Chart"][i] + " Graphs", width= 400, height=300
                )
                for j in range(df["Layout"][i]):
                    fig.add_trace(go.Scatter(), row = j + 1, col = 1)
                plot_divs.append(html.Div(id = {'type': 'plot-layout', 'index' : df["Chart"][i]},
                className = 'sub-layout', style = {'display':'none'}, children = 
                    [dcc.Graph(id =  {'type': 'graphs', 'index' : df["Chart"][i]}, figure = fig, className = 'graphs',
                        responsive = True)]))

        #Add Home Screen to help users navigate
        plot_divs.append(html.Div(id = {'type': 'plot-layout', 'index' : 'Home'},
            className = 'sub-layout-', style = {'display':'block'}, 
            children = [html.H1("Welcome to your experiment dashboard.", id = {'type': 'header', 'index' : 'home'}), 
                        html.P("Please select a quantity to learn more about it.", id = {'type': 'paragraph', 'index' : 'home'})]))
        
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

        return sidebar, main_layout, dcc.Interval(id = "refresh", 
            interval = 1 * 1000, n_intervals = 0)

    """
    Application Layout helper function called to serve layout
    """
    app.layout = serve_layout

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
        processed_obj = PostProcessData(jsonpath = my_json_file)
        #Obtain and load live data
        processed_obj.ScaleData()
        processed_obj.UpdateData()
        processed_data = processed_obj.df_processed
        print(processed_data.shape)
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
                            title_text = df["Chart"][i] + " Graphs", width=400, height=300
                        )
                        graph.update_xaxes(title_text = "Time (s)", row = df["Layout"][i])
                        graph.update_yaxes(title_text = df["Processed_Unit"][i], row = df["Position"][i])
                        print("here")
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
        Timer(1, open_browser).start()
        app.run_server(port=1222)

"""
Runs app on Server
"""
if __name__ == "__main__":
    app = create_dash_app()
    app.run_server(port=1222)


