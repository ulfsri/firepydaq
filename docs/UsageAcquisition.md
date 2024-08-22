(GUI)=
# Acquisition Application

This is an example of how to install and use the acquisition application to collect data from the NI system and added devices and visualize it for each channel and using a dashboard.

## 1. Setting Up the Application

To run the application, paste the following lines of code in an empty python file: 

```
    if __name__ == "__main__":
        from firepydaq.FIREpyDAQ_Acquisition import FIREpyDAQ_Acquisition
        FIREpyDAQ_Acquisition()
```

On running the file, the application window would appear. 
```{image} assets/Acquisition/SetUp1.png
:width: 500px
:align: center
:alt: MFCMenu
```
<br></br>

## 2. Acquisition Settings 

To configure acquisition settings, enter your desired Name, Project Name, Test Name,
Sampling Rate, Experiment Type, and select your Configuration File and optionally the Formulae File (refer to Example: Configuration and Formula File). For Test Name, either provide a name or select a file path. It is recommended to chose a sampling rate compatible with the device data is acquired from. If an incompatible rate is chosen, the application would create a notification.

On running the file, the application window would appear. 
```{image} assets/Acquisition/SetUp2.png
:width: 500px
:align: center
```
<br></br>

## 3. Additional Settings

The menu bar presents some extra functionalities such as data display options, light and dark modes, and loading and saving data acquisition configurations. This section serves as a guide through those settings. All main menu settings have keyboard shortcuts listed on the main menu itself for reference.

On running the file, the application window would appear. 

### Display Modes 
To toggle between display modes (light and dark), select the 'Mode Menu' in the main menu and select your desired settings as shown below.

```{image} assets/Acquisition/Setting1.png
:width: 500px
:align: center
:alt: AcqSettings
```

### Dashboard and Tab Display
In order to visualize the saved data collected, select the desired data display option from the 'Data Display' Menu. 
- Display Tab spins out a tab with graphs for each channel when the Begin Acquisition button is enabled.
- Display Dashboard option spins out a dashboard on a web browser when the Save Button is enabled. 
- Display All enables both tab and dashboard to spin out. 
- Display None allows data collection without any visualization. 

```{image} assets/Acquisition/4.png
:width: 500px
:align: center
:alt: AcqSettings
```

### Loading and Saving DAQ Configuration
The Options under the File Menu enables loading settings from a .json file (refer to Example: JSON File) to repeat data acquisition under similar conditions. The File Menu also presents the option to Save Settings to a .json File enabling a user to save configuration settings to refer to later.

In order to Save Settings, click on 'Save DAQ Configuration' under the File Menu. 
```{image} assets/Acquisition/5.png
:width: 500px
:align: center
:alt: AcqSettings
```

In the dialog box that appears, specify the desired name and directory of the file to save to. Finally, click on 'Done' to save settings to the selected file path.
```{image} assets/Acquisition/6.png
:width: 500px
:align: center
:alt: AcqSettings
```

In order to Load Settings, click on 'Load DAQ Configuration' under the File Menu. 
```{image} assets/Acquisition/7.png
:width: 500px
:align: center
:alt: AcqSettings
```

In the dialog box that appears, select the file to load data from. 
```{image} assets/Acquisition/8.png
:width: 500px
:align: center
:alt: AcqSettings
```

Finally, click on 'Done' to load settings from the select file. After loading, desired settings can still be changed.

```{image} assets/Acquisition/9.png
:width: 500px
:align: center
:alt: AcqSettings
```

### Help
For more information and concerns about the application, visit the 'Help menu' to raise an issue on our Github page or visit the documentation for difficulties with usage.

## 4. Acquisition and Saving

After configuring the desired settings, click on 'Begin Acquisition' to establish connection with the NI System or other added devices and create AO/AI tasks. The notifications panel will indicate if the acquisition process has begun or run into any faults. In the case 'Display Tab or All' is selected, the 'Data Visualizer' Tab in the program is populated. 

```{image} assets/Acquisition/10.png
:width: 500px
:align: center
:alt: AcqSettings
```
<br></br>
```{image} assets/Acquisition/14.png
:width: 500px
:align: center
:alt: AcqSettings
```

Once acquisition begins safely, the 'Save Button' is enabled and on clicking it, the data collected is saved. In the case, a Test Name is provided, the acquired data will be saved in a directory with the name of the chosen Experiment Type in the current working directory with the filename in the format `[YYYYMMDD]_[HHMMSS]_[ProjectName]_[TestName]` with the extensions .parquet and .json for data and settings file respectively. If a file path is specified, the data would be saved at the file path specified with the extensions .parquet and .json for data and settings file respectively. The Dashboard is also spun out if 'Display Dashboard or All' is chosen. Updated dataframe is saved each second. For more information on how to navigate through the dashboard, check out (Dashboard Section). In the case a formula file was selected for the visualizations on the dashboard, a file with '_PostProcessed appended to the parquet file's name is created in the same directory as the parquet file.

```{image} assets/Acquisition/11.png
:width: 500px
:align: center
:alt: AcqSettings
```
<br></br>
```{image} assets/Acquisition/12.png
:width: 500px
:align: center
:alt: AcqSettings
```
<br></br>

## 5. Logger

The application uses a logging system to track any updates or unexpected errors that may occur in the middle of acquisition or saving. All milestones during the process of acquisition and saving are logged in a file 'FirePyDAQLog.log' created in the directory the code is run from. Although similar to notifications, the logger offers more detailed insight into the application. The logging system is renewed every time, a new instance of the application is opened. 

## 6. Notifications Panel
Additionally, the notifications panel allows you to gain insights into the data acquisition process and if specific steps during the saving and/or acquisition process are successfully completed or run into issues. Observations may be added by logging data into the line-edit below and clicking on the 'Log' Button. The text in the notifications panel is colored on degrees of importance:

|   Color     | Importance |
|   --------  | -------    |
|   Warning   | Orange     |
|   Error     | Red        |
|   Success   | Green      |
|   Default   | Grey       |
| Observation | Darkgreen  |
|    Info     | Cyan       |

Finally, the notifications panel has an 'Options' Menu that allows users to either 'Clear' or 'Save' their notifications. On pressing 'Clear', all previous notifications are wiped out. On clicking 'Save', all notifications are saved into the chosen directory.
```{image} assets/Acquisition/15.png
:width: 500px
:align: center
:alt: AcqSettings
```
<br></br>
```{image} assets/Acquisition/16.png
:width: 500px
:align: center
:alt: AcqSettings
```
<br></br>

## 7. Experiment Data and Exiting the Application

Experimental data can be retrieved with the file paths explained above, (see Acquisition and Saving). The correct chronology to exit the application is as follows: stopping Saving; stopping acquisition and finally exiting the application in order to terminate connection with the Dashboard and Hardware Systems safely.