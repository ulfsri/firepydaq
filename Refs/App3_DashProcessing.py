# By: Dushyant Chaudhari
# Last updated: Feb 20, 2024

import dash                                    
from dash import dcc, html, Input, Output,dash_table, State
# import dash_daq as daq
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
from random import randrange
import time
from plotly.subplots import make_subplots
import numpy as np
import dash_bootstrap_components as dbc
from dash_auth import BasicAuth

import pandas as pd
import pyarrow.parquet as pq
import numpy as np
import itertools

from utilities.Utils import read_pq

def create_Dashapp():
    def initialize_dashData(file ="DAQsavefilepath.txt"):
        with open(file,'r') as f:
            lines = f.readlines()
        fpath = lines[0].strip()
        configpath = lines[1].strip()

        df = read_pq(fpath)
        return df,fpath,configpath
    
    if __name__ != "__main__":
        time.sleep(4)
    # external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
    
    app = dash.Dash(__name__)#, external_stylesheets=[dbc.themes.BOOTSTRAP])
    df,fpath,configpath = initialize_dashData()
    
    info_file = fpath.split("parquet")[:-1][0]+'info'
    with open(info_file,'r') as f:
        info_contents = f.readlines()
    for n,line in enumerate(info_contents):
        info_contents[n] = [line.split(":")[0],''.join(line.split(":")[1:])]
    info_contents = pd.DataFrame(info_contents, columns=["Type","Path"])
    obs_save_path = ''.join(info_contents.loc[0,"Path"].split(".parquet")[:-1])+"_observations.csv"
    
    def read_config(configpath = configpath):
        config_df= pd.read_csv(configpath)
        return config_df
    config_df = read_config()

    hrr_types = ["ASTM 1354 (Cone calorimeter) - O2 only","ASTM 1354 (Cone calorimeter) - O2,CO2, and CO","Molecular formula based (No calibration needed)"]

    left_float = {      'max-width': '800px',
                        'max-height': '1024px',
                        'width': '100vw',
                        'height': '600px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'solid',
                        'borderRadius': '10px',
                        'textAlign': 'center',
                        'margin': 'auto',
                        'padding':'10px',
                        # 'display':'inline-block',
                        'float':'left'
                        }
    right_float = {
                        'max-width': '768px',
                        'max-height': '1024px',
                        'width': '90vw',
                        'height': '600px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'solid',
                        'borderRadius': '10px',
                        'textAlign': 'center',
                        'margin': 'auto',
                        'padding':'5px',
                        # 'display':'inline-block',
                        'float':'right'
                    }
    # *************************************************************************
    app.layout = html.Div(
        id="dark-light-theme",
        children=[
            html.Div(
                [
                    html.H1("Processed Data Visualizer", style={"textAlign": "center"})
                ],
                ),
                html.Div( children =[
                    html.P("First 10 columns of the saved file will be shown here."),
                    dbc.Label(id="FileViewerLabel",style={'max-width':'300px'}),
                    dbc.Container([
                        dash_table.DataTable(id="DataTable", 
                                            virtualization=True, 
                                            style_table={
                                            'overflowX': 'auto',
                                            'width':'100%',
                                            'height':'550px',
                                            'overflowY':'auto',
                                            'margin':'auto'},
                                            style_cell={
                                                'minWidth': 40, 'maxWidth': 200, 'width': 60, 'padding': '5px'
                                            },
                                            style_data_conditional=[
                                                {
                                                    'if': {'row_index': 'odd'},
                                                    'backgroundColor': 'rgb(220, 220, 220)'},
                                                    {'if': {'column_id': 'Absolute_Time'},
                                                    'width': '200px'},
                                                
                                            ],
                                            style_header={
                                                'backgroundColor': 'white',
                                                'fontWeight': 'bold',
                                                'border': '1px solid red'
                                            },
                                            # style_data={ 'border': '1px solid grey' },
                                            fixed_rows={'headers':True}
                                            ),
                        html.P(id='FileViewer',style={'display': 'inline-block'}),
                    ]),
                    ],style= right_float
                        ),
                    html.Div(id="EventCatcher",children=[
                            html.H6("Info File and space to record observation"),
                            dbc.Container([
                            dash_table.DataTable(id="InfoTable", 
                                                
                                                data = info_contents.to_dict('records'),

                                                virtualization=True, 
                                                style_table={
                                                'overflowX': 'auto',
                                                'width':'100%',
                                                'height':'100px',
                                                'overflowY':'auto',
                                                'margin':'auto'},
                                                style_cell={
                                                    'minWidth': 40, 'width': 60, 'padding': '5px'
                                                },
                                                style_data_conditional=[
                                                    {
                                                        'if': {'row_index': 'odd'},
                                                        'backgroundColor': 'rgb(220, 220, 220)'},
                                                        {'if': {'column_id': 'Path'},
                                                        'width': '200px'},
                                                    
                                                ],
                                                style_header={
                                                    'backgroundColor': 'white',
                                                    'fontWeight': 'bold',
                                                    'border': '1px solid red'
                                                },
                                                # style_data={ 'border': '1px solid grey' },
                                                fixed_rows={'headers':True}
                                                ),
                                ]),
                                html.Button('Add Observation', id='add-row-button', n_clicks=0),
                                html.Button('Save Observations', id='Save-Obs-btn', n_clicks=0),
                                html.P("Save Status",id="SaveStatus"),
                                dbc.Container([
                                    dash_table.DataTable(id="ObsTable", 
                                                columns=[{"name": "#", "id": "#","editable":True},
                                                         {"name": "Time", "id": "Time","editable":True},
                                                         {"name": "Type", "id": "Type","editable":True},
                                                         {"name": "Observation", "id": "Observation","editable":True}],
                                                data = [{"#":0,"Time":0,"Type":"Obs", "Observation":"Test started"}],
                                                editable=True,
                                                row_selectable="multi",
                                                row_deletable =True,
                                                virtualization=True, 
                                                style_table={
                                                    'overflowX': 'auto',
                                                    'width':'100%',
                                                    'height':'200px',
                                                    'overflowY':'auto',
                                                    'margin':'auto'},
                                                style_cell={
                                                    'minWidth': 40, 'width': 60, 'padding': '5px'
                                                },
                                                style_data_conditional=[
                                                    {
                                                        'if': {'row_index': 'odd'},
                                                        'backgroundColor': 'rgb(220, 220, 220)'},
                                                        {'if': {'column_id': 'Observation'},
                                                        'width': '350px'},
                                                        {'if': {'column_id': '#'}, 'editable':False },
                                                    
                                                ],
                                                style_header={
                                                    'backgroundColor': 'white',
                                                    'fontWeight': 'bold',
                                                    'border': '1px solid red'
                                                },
                                                # style_data={ 'border': '1px solid grey' },
                                                fixed_rows={'headers':True}
                                                ),
                                    ]),
                                ], 
                    style=left_float
                        ),
                    html.Div(id="HRRGraphContainer",children=[ 
                                dcc.Dropdown(id="HRRType",options=hrr_types,value=hrr_types[0],clearable =False, searchable=False, 
                                             ),
                                dcc.Graph(id="HRRGraph", figure={"layout": {
                                        "title": "Heat Release Rate",
                                        "height": 400,  # px
                                    }} ), 
                                ],
                    style=right_float),

            html.Div(id="SimpleScatterContainer",children=[
                                                html.Div("X axis:",style={'display':'inline-block', 'padding':'5px'}),
                                                dcc.Dropdown(id="XScatterdd",options=df.columns,value=df.columns[1],clearable =False),
                                                html.Div("Y axis:",style={'display':'inline-block',  'padding':'5px'}),
                                                dcc.Dropdown(id="YScatterdd",options=df.columns,value=df.columns[2],clearable =False),
                                dcc.Graph(id="SimpleScatter", figure={"layout": {
                                        "title": "Individual plots",
                                        "height": 500,  # px
                                    }}), 
                                ], 
                    style=left_float
                        ),
            html.Div(id="PTHScatter",children=[
                                dcc.Graph(id="PTHGraph", figure={"layout": {
                                        "title": "Processed PTH",
                                        "height": 600,  # px
                                    }}), 
                                ], 
                    style=right_float
                        ),
            html.Div(id="BDPScatter",children=[
                                dcc.Graph(id="BDPGraph", figure={"layout": {
                                        "title": "Processed BDP",
                                        "height": 600,  # px
                                    }}), 
                                ], 
                    style=left_float
                        ),
            html.Div(id="LaserScatter",children=[
                                dcc.Graph(id="LaserGraph", figure={"layout": {
                                        "title": "Laser",
                                        "height": 600,  # px
                                    }}), 
                                ], 
                    style=left_float
                        ),
            html.Div(id="FlowScatter",children=[
                    dcc.Graph(id="FlowGraph", figure={"layout": {
                            "title": "Flow",
                            "height": 600,  # px
                        }}), 
                    ], 
                    style=right_float
                        ),
            dcc.Interval(id="timing", interval=1000, n_intervals=0), # interval is in millisecond
        ],
    )
        
    @app.callback(
        Output("DataTable","data"),
        Output("DataTable","columns"),
        Output("FileViewerLabel","children"),
        Input("FileViewerLabel","children"),
    )
    def read_uploaded_contents(label):
        df = read_pq(fpath)

        df.insert(0,"NewIndex",range(0,len(df.iloc[:,0])))
        print(df.head())
        data = df.head(10).to_dict('records')
        columns = [{"name": i, "id": i} for i in df.columns]
        LabelStr = fpath

        return data, columns, LabelStr
    
    @app.callback(
            Output('ObsTable', 'data'),
            Input('add-row-button', 'n_clicks'),
            State('ObsTable', 'data'),
            State('ObsTable', 'columns'),
    )
    def add_row(add_row_click, rows, columns):
        if add_row_click > 0:
            rows.append({c['id']: '' for c in columns})
        return rows
    
    @app.callback(
        Output("SaveStatus","children"),
        Input("Save-Obs-btn", "n_clicks"),
        Input("ObsTable", "data"),
    )
    def download_as_csv(n_clicks, table_data):
        df = pd.DataFrame.from_dict(table_data)
        if n_clicks==0:
            raise PreventUpdate
        df.to_csv(obs_save_path)
        return f"Observations Saved in {obs_save_path}"

    # *************************************************************************
    @app.callback(
        Output("SimpleScatter", "figure"),
        Input("timing", "n_intervals"),
        Input("XScatterdd","value"),
        Input("YScatterdd","value"),
    )
    def PlotSimpleScatter(n_ints,XCol,YCol):
        df = read_pq(fpath)
        xdata = [round(np.float64(val),2) for val in df.loc[:,XCol].values]
        if isinstance(YCol, str):
            YCol = [YCol]
        ## Attempting to plot multiple plots on same plot but will add another html div to plot grouped data
        for col in YCol:
            ydata = df.loc[:,col].values
            fig  = go.Figure(
                [
                    go.Scatter(
                        x=xdata,
                        y=ydata,
                    )
                ]
            )
            fig.update_layout(xaxis_title=XCol,yaxis_title=col)#yaxis={"range": [20, 30]})

        return fig
    
    @app.callback(
            Output('PTHGraph','figure'),
            Input("timing", "n_intervals")
    )
    def PlotPTH(n):
        df = read_pq(fpath)
        xdata = df.loc[:,"Time"].values
        PTH_df = config_df.loc[config_df.Chart=="PTH"]
        if PTH_df.empty:
            raise PreventUpdate
        Humidity_label = PTH_df.loc[PTH_df.Label.str.contains("Hum"),"Label"].values[0]
        Temp_label = PTH_df.loc[PTH_df.Label.str.contains("Temp"),"Label"].values[0]
        Press_label = PTH_df.loc[PTH_df.Label.str.contains("Press"),"Label"].values[0]

        Humidity = df.loc[:,Humidity_label].values
        Temp = df.loc[:,Temp_label].values
        Press = df.loc[:,Press_label].values

        RH_range = [0,100] #%
        Temp_range = [-20,120] #C
        Pressure_range = [750,1100] #mbar

        Volt_range = [1,5] # min, Max for 4 to 20 mA output and 250 ohms resistor

        RH_slope = np.diff(Volt_range)/np.diff(RH_range) # volts/RH percentage
        Temp_slope = np.diff(Volt_range)/np.diff(Temp_range) # volts/Temp C
        Pressure_slope = np.diff(Volt_range)/np.diff(Pressure_range) # volts/pressure

        RH = (Humidity-Volt_range[0])/RH_slope +RH_range[0] #%
        TempC = (Temp-Volt_range[0])/Temp_slope + Temp_range[0]
        Pressure = (Press-Volt_range[0])/Pressure_slope + Pressure_range[0]

        fig = make_subplots(rows=3,cols=1, shared_xaxes=True)

        # Add traces
        fig.add_trace(
            go.Scatter(x=xdata, y=RH, name="Rel. Humidity (%)") ,row=1,col=1,
            
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(x=xdata, y=TempC, name="Temp (C)"), row=2,col=1,
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(x=xdata, y=Pressure, name="Amb Pressure"),row=3,col=1,
            secondary_y=False,
        )

        # Add figure title
        fig.update_layout(
            title_text="<b> Processed ambient PTH </b>", height= 600,
        )

        # Set x-axis title
        fig.update_xaxes(title_text="Time (s)",row=3)

        # Set y-axes titles
        fig.update_yaxes(title_text="<b>Rel. Humidity (%)</b>", secondary_y=False, row=1)
        fig.update_yaxes(title_text="<b>Temmp (C)</b>", secondary_y=False, row=2)
        fig.update_yaxes(title_text="<b>Amb. Press. (mbar)</b>", secondary_y=False, row=3)
        

        return fig
    
    
    @app.callback(
            Output('BDPGraph','figure'),
            Input("timing", "n_intervals")
    )
    def PlotBDP(n):
        df = read_pq(fpath)
        xdata = df.loc[:,"Time"].values
        BDP_config_df = config_df.loc[config_df.Chart.str.contains("BDP"),"Label"].values
        if len(BDP_config_df)==0:
            raise PreventUpdate
        BDP_df = df.loc[:,BDP_config_df]
        BDP1to2_scale = [0, 12.44] #Pa
        BDP4to6_scale = [0, 24.88] #Pa
        BDP_range = [0,5]

        fig = make_subplots(rows=2,cols=2, shared_xaxes=True)
        for i in range(int(len(BDP_df.columns)/2)):
            if i<2:
                BDP_scale = BDP1to2_scale
                coli=1
            else:
                BDP_scale = BDP4to6_scale
                coli=2
            BDP_val = BDP_df.loc[:,f'BDP{i+1}'].values
            BDPT_val = BDP_df.loc[:,f'BDPT{i+1}'].values +273.15 # Convert to K
            if BDPT_val[-1]>1500:
                continue
            else:
                good_vals = BDPT_val<1500
            BDPT_val = BDPT_val[good_vals]
            DeltaBDP = BDP_val[good_vals]*np.diff(BDP_scale)/np.diff(BDP_range) + BDP_scale[0] # Pa
            Baseline = np.mean(DeltaBDP[:10]) 
            DeltaBDP = DeltaBDP - Baseline

            Vel = np.sign(DeltaBDP) * 0.0698*np.sqrt(np.array(abs(DeltaBDP)*BDPT_val).astype('float'))

            # Add traces
            fig.add_trace(
                go.Scatter(x=xdata[good_vals], y=Vel, name=f"Velocity@{i+1}") ,row=i%2+1,col=coli,
                
                )
            # Set x-axis title
            fig.update_xaxes(title_text="Time (s)",row=3)
            fig.update_yaxes(range=[-0.25,0.25], title_text="<b>Velocity (m/s)</b>", secondary_y=False, col=1)
            fig.update_yaxes(range=[-0.25,0.25],col=2)

            # Add figure title
        fig.update_layout(
            title_text="<b> Processed BDPs </b>", height= 600,
        )
        return fig
    
    @app.callback(
        Output("HRRGraph","figure"),
        # Output(component_id='HRRGraphContainer', component_property='style'),
        Input("timing","n_intervals"),
        Input("HRRType","value")
    )
    def PlotHRR(n_ints,hrrtype):
        fig  = go.Figure(
                [
                    go.Scatter(
                        x=[],
                        y=[],
                    )
                ]
            )
        df = read_pq(fpath)
        xdata = df.loc[:,"Time"].values
        if "dPDuctAvg" not in df.columns or "DuctO2" not in df.columns:
            return fig#, {'display': 'none'}
            # raise PreventUpdate
        dP_range = [0,248.84] #Pa
        O2_range = [0,25] #%
        CO2_range=[0,25] #%
        CO_range=[0,5] #%
        Volt_gas_scale = [0,5]
        mA_out_scale = [4,20] # mA
        resistors = [244.7, 244.7] # Ohms
        
        dP_volt_scale = [a*b/1000 for a,b in zip(mA_out_scale,resistors)] # V
        dP_scale = np.diff(dP_range)/np.diff(dP_volt_scale) #config_df.loc[config_df.Label=="dPDuctAvg","Scale"].values # Pa/V
        O2_scale = np.diff(O2_range)/np.diff(Volt_gas_scale) #config_df.loc[config_df.Label=="DuctO2","Scale"].values # (Vol. fraction)/V
        CO2_scale = np.diff(CO2_range)/np.diff(Volt_gas_scale) #config_df.loc[config_df.Label=="DuctCO2","Scale"].values # (Vol. fraction)/V
        CO_scale = np.diff(CO_range)/np.diff(Volt_gas_scale) #config_df.loc[config_df.Label=="DuctCO","Scale"].values # (Vol. fraction)/V

        DuctTCs = df[["DuctTC1","DuctTC2","DuctTC3"]].astype('float')
        
        E = 13100 # kJ/kg Delta_H_c/r_o.
        dP = df.loc[:,"dPDuctAvg"].astype('float').values
        dP_Pa = (dP-dP_volt_scale[0]) * dP_scale + dP_range[0]
        
        O2 = df.loc[:,"DuctO2"].astype('float').values
        O2_frac = O2 * O2_scale/100
        
        CO2 = df.loc[:,"DuctCO2"].astype('float').values
        CO2_frac = CO2 * CO2_scale/100

        CO = df.loc[:,"DuctCO"].astype('float').values
        CO_frac = CO * CO_scale/100

        # mean of first 50 s of data or first 10 samples (1 s data) samples
        O2_baseline = np.mean(O2_frac[:max(50*10,10)]) 
        CO2_baseline = np.mean(CO2_frac[:max(50*10,10)]) 
        CO_baseline = np.mean(CO_frac[:max(50*10,10)])
        # print(O2_frac)
        good_TC=[]
        for i in DuctTCs.columns:
            # Hard coded limit of 700 C to check if TC measures correct values
            if DuctTCs.loc[df.index[-1],i]<700 or DuctTCs.loc[df.index[-1],i]<0:
                good_TC.append(True)
            else:
                good_TC.append(False)
        cols_good_TC = list(itertools.compress(DuctTCs.columns,good_TC))
        T_e = DuctTCs[cols_good_TC].mean(axis=1)+273.15 #K
        if any(dP_Pa<0):
            # print("dP Duct is negative. This must be a positive value")
            raise PreventUpdate
        
        C_factor =1 # HRR correction factor
        K_Flow = 0.6033 # Avg pitot tube flow coefficient
        rho_e = 101315*0.02896/(8.314*T_e)
        vel_e = K_Flow*np.sqrt(2*dP_Pa/rho_e)
        A_duct = np.pi*((17.8*0.0254)**2)/4
        m_e = vel_e*A_duct*rho_e
        
        if hrrtype == hrr_types[0]: # ASTM 1354 O2 only
            O2_depletion = abs((O2_baseline - O2_frac)/(1.105 - 1.5*O2_frac))
            hrr = E*C_factor*1.10*m_e*O2_depletion
        elif hrrtype==hrr_types[1]: #ASTM 1354 O2, CO2, and CO
            O2_depletion = (O2_baseline*(1-CO2_frac-CO_frac) - O2_frac*(1-CO2_baseline))/(O2_baseline*(1-CO2_frac - CO_frac - O2_frac)) # Eq. A.1.5
            H2O_ambient = 0 # Needs to be calculated from ambient PTH sensor
            O2_ambient = O2_baseline*(1-H2O_ambient)
            O2_mult = abs(O2_ambient*(O2_depletion - 0.172*(1-O2_depletion)*CO2_frac/O2_frac)/(1-O2_baseline+1.105*O2_depletion)) # Eq. A.1.5 numerator
            hrr = E*C_factor*1.10*m_e*O2_mult # Eq. A.1.5
        fig  = go.Figure(
                [
                    go.Scatter(
                        x=xdata,
                        y=hrr,
                    )
                ]
            )
        fig.update_layout(xaxis_title="Time (s)",yaxis_title="HRR (kW)")
        return fig#, {'display': 'inline-block'}

    @app.callback(
            Output('LaserGraph','figure'),
            Input("timing", "n_intervals")
    )
    def PlotLaser(n):
        fig  = go.Figure(
                [
                    go.Scatter(
                        x=[],
                        y=[],
                    )
                ]
            )
        
        df = read_pq(fpath)
        xdata = df.loc[:,"Time"].values

        ydata = df[["LaserRef","LaserSig"]]

        for col in ydata.columns:
            fig.add_trace(
                    go.Scatter(
                        x=xdata,
                        y=ydata[col],
                        name=col
                    )
            )
        
        fig.update_layout(xaxis_title="Time (s)",yaxis_title="Laser Ref. and Sig. (V)")

        return fig
    
    @app.callback(
            Output('FlowGraph','figure'),
            Input("timing", "n_intervals")
    )
    def PlotVel(n):
        fig = make_subplots(rows=2,cols=1, shared_xaxes=True)
        
        df = read_pq(fpath)
        xdata = df.loc[:,"Time"].values
        
        dPAvg_range = [0,248.84] #Pa
        dPDwyer_range = [0, 124.42] #Pa
        mA_out_scale = [4,20] # mA
        resistors = [244.7, 244.7] # Ohms
        dPAvg_volt_scale = [a*b/1000 for a,b in zip(mA_out_scale,resistors)] # V
        dPDwyer_volt_scale = dPAvg_volt_scale# [1,5] # V [0, 5]
        # print(dP_volt_scale)
        dPAvg_scale = np.diff(dPAvg_range)/np.diff(dPAvg_volt_scale) ## Pa/V
        dPDwyer_scale = np.diff(dPDwyer_range)/np.diff(dPDwyer_volt_scale) ## Pa/V
        
        dPAvg = df.loc[:,"dPDuctAvg"].astype('float').values
        dPAvg_Pa = (dPAvg-dPAvg_volt_scale[0]) * dPAvg_scale + dPAvg_range[0]
        # print(dPAvg_Pa)
        dPDwyer = abs(df.loc[:,"dPDuctDwyer"].astype('float').values)
        dPDwyer_Pa = (dPDwyer-dPDwyer_volt_scale[0]) * dPDwyer_scale + dPDwyer_range[0]
        # print(np.mean(dPDwyer)-dP_volt_scale[0])
        DuctTCs = df[["DuctTC1","DuctTC2","DuctTC3"]].astype('float')
        good_TC=[]
        for i in DuctTCs.columns:
            # Hard coded limit of 700 C to check if TC measures correct values
            if DuctTCs.loc[df.index[-1],i]<700 or DuctTCs.loc[df.index[-1],i]<0:
                good_TC.append(True)
            else:
                good_TC.append(False)
        cols_good_TC = list(itertools.compress(DuctTCs.columns,good_TC))
        T_e = DuctTCs[cols_good_TC].mean(axis=1)+273.15
        # print(T_e)

        KAvg_Flow = 0.6033 # Avg pitot tube flow coefficient
        KDwyer_Flow = 0.81 # Avg pitot tube flow coefficient
        rho_e = 101315*0.02896/(8.314*T_e)
        vAvg_e = KAvg_Flow*np.sqrt(2*dPAvg_Pa/rho_e) 
        vDwyer_e = KDwyer_Flow*np.sqrt(2*dPDwyer_Pa/rho_e)

        A_duct = np.pi*((17.8*0.0254)**2)/4
        VolAvg_e = vAvg_e * A_duct
        VolDwyer_e = vDwyer_e * A_duct

        mAvg_e = VolAvg_e*rho_e
        mDwyer_e = VolDwyer_e*rho_e

        ydata = pd.DataFrame(data=np.array([mAvg_e,mDwyer_e,vAvg_e,vDwyer_e,VolAvg_e,VolDwyer_e]).T,columns=["m_Avg","m_Local","v_Avg","v_Local","vol_Avg","vol_Local"])
        # print(ydata)

        for col in ydata.columns:
            secondary = ('v_' in col)
            if secondary:
                row = 2
            else:
                row = 1
            fig.add_trace(
                    go.Scatter(
                        x=xdata,
                        y=ydata[col].values,
                        name=col
                    ), row=row, col=1
            )
        fig.update_xaxes(title_text="Time (s)",row=2)
        fig.update_yaxes(title_text="Mass Flow (kg/s)",row=1)
        fig.update_yaxes(title_text="Velocity (m/s)",row=2)

        return fig
    
    if __name__ == "__main__":
        return app
    else:
        USER_PWD = {"fsri":"fsri"}
        BasicAuth(app,USER_PWD)
        app.run_server(debug=False, host="0.0.0.0", port=3030)
        
if __name__ == "__main__":
    app = create_Dashapp()
    app.run_server(debug=True, host="0.0.0.0", port=3030)
    