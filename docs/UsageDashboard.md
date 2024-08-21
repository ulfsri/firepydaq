(Dashboard)=
# Example: Dashboard Usage

This is an example of how to use the dashboard to visualize data derived from acquisition from the NI system and added devices. Here, the usage of the dashboard as a live visualization of the data collected from the acquisition application as well as a standalone way to visualize and post process parquet files is discussed.

## 1. With Acquisition  

As mentioned in Acquisition, the 'Display All' or 'Display Dashboard' options can be chosen to spin out a live dashboard. This dashboard uses the saved data from the parquet file, a configuration file to create plot layouts and optionally a formulae file to visualize obtained data by performing certain operations. 

## 2. Dashboard 

To use parquet files, configuration, formula files to run the dashboard, paste the following lines of code in an empty python file. Simply remove the formulaepath keyword argument if no formula file is needed. 

```
    if __name__ == '__main__':
        from firepydaq.dashboard.app import create_dash_app
        create_dash_app(datapath = [path-to-parquetfile], configpath = [path-to-configfile], formulaepath = [path-to-formulafile])
```

If you wish to use a .json file from a previous experiment, simply replace the keyword arguments as follows:

```
    if __name__ == '__main__':
        from firepydaq.dashboard.app import create_dash_app
        create_dash_app(jsonpath = [path-to-jsonfile])
```

To learn more about the usage of keywords, please refer to [].

## 3. Layout 

This section discusses how the layout for the dashboard is generated. The layout is built using the common columns of the configuration file and formula file. For more information on how to construct those files refer to Example: config anf formula. Firstly, the 'Chart' column is used to organize the total number of graph pages on a website. All entries with the same 'Chart' name fall under the same graph. 'Layout' decides the number of plots on a single graph. 'Position' indicates the position of the particular plot within the graph. For example, a 'Layout' entry of 2 and 'Position' of 1, indicates the top plot among the two plots on the graph. 'Label' is used by the formula file to call for values of a specific field. Lastly, 'Legend' is the name used in the legend to distinguish between multiple values plotted on the same plot and 'Processed Unit' for indicating the Y-axis units.

## 4. Other functionalities:

This section offers insight into some other functionalities offered by the dashboard such as switching display modes, capturing all graphs, other features on the title bar etc. 

### General
The user interface is responsive and can be used on varying desktop or laptops. However, they are not yet suited for phones. The graphs on the dashboard are also interactive in nature and can be zoomed in on for a closer, more detailed look.

### Home Page
The home page is the page the website lands on first after loading. It has a few fields indicating the locations of the parquet, configuration, formula and post processed files that are used up by the application or created by it.

### Navigation
In order to navigate between different graphs more seamlessly, simply chose the desired 'Chart' Type on the sidebar.

### Update Interval
The update intervals for each of the graphs are set to about 3 seconds. This indicates that every 3 seconds data is read from the parquet files, processed, and displayed. 

### Pause updates
On the title bar, the tiny pause button can be used in order to pause the dashboard from updating the dashboard at any given point in time. To resume the dashboard, click the play button.

### Saving graphs
In order to save all plots, simply click on the graph button. All the graphs present will be saved in .html format in the same directory as the parquet files with the following name: [ParquetFileName]_YYMMDD_HHMMSS_[ChartName].html. The graphs also have a camera icon used to capture a single graph. 

### Display Modes
The toggle button on the title bar may be used to switch between light and dark modes such as shown below.

## 5.Logger 
The dashboard_error.log contains all the output printed by the program and while the server was running. It serves as a means to understand the issues or updates that occur through the course of the application.

## 6.Exit
To exit the application, simply navigate to the the window the application is running from and use the key combination "Ctrl + C". The server should come to a halt.

