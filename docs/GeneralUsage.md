(GUI)=
# Example: Acquisition Usage
This is an example of how to install and use the acquisition application to collect data from the NI system and added devices and visualize it for each channel and using a dashboard.

## Setting Up the Application
To run the second application, paste the following lines of code in an empty python file: 
'''
if __name__ == "__main__":
    from firepydaq.FIREpyDAQ_Acquisition import FIREpyDAQ_Acquisition
    FIREpyDAQ_Acquisition()
'''
On running the file, the application window would appear. 
![alt text](assets/2024-08-20%2013_32_50-GeneralUsage.md%20-%20firepydaq%20-%20Visual%20Studio%20Code.png)

## Acquisition Settings 
To configure acquisition settings, enter your desired Name, Project Name, Test Name,
Sampling Rate, Experiment Type, and select your Configuration File and optionally the Formulae File (refer to Example: Configuration and Formula File). For Test Name, either provide a name or select a file path. In the case, a Test Name is provided, the acquired data will be saved in a directory with the name of the chosen Experiment Type in the current working directory with the filename in the format `[YYYYMMDD]_[HHMM]_[ProjectName]_[TestName]` with the extensions .parquet and .json for data and settings file respectively. If a file path is specified, the data would be saved at the file path specified with the extensions .parquet and .json for data and settings file respectively.

## Additional Settings
The menu bar presents some extra functionalities such as data display options, light and dark modes, and loading and saving data acquisition configurations. This section serves as a guide through those settings.  

### Display Modes 
To toggle between display modes (light and dark), select the Mode Menu in the main menu and select your desired settings as shown below.

### Dashboard and Tab Display
In order to visualize the saved data collected, select the desired data display option from the Data Display Menu. 
- Display Tab spins out a tab when the Begin Acquisition button is enabled.
- Display Dashboard option spins out a dashboard on a web browser when the Save Button is enabled. 
- Display All enables both tab and dashboard to spin out. 
- Display None allows data collection without any visualization. 

### Loading and Saving DAQ Configuration
The Options under the File Menu enables loading settings from a .json file (refer to Example: JSON File) to repeat data acquisition under similar conditions. The File Menu also presents the option to Save Settings to a .json File enabling a user to save configuration settings to refer to later.

In order to Load Settings, click on 'Load DAQ Configuration' under the File Menu. 

In the dialog box that appears, select the file to load data from. 

Finally, click on Done to load settings from the select file. After loading, desired settings can still be changed.

In order to Save Settings, click on 'Save DAQ Configuration' under the File Menu.

In the dialog box that appears, specify the desired name and directory of the file to save to.

Finally, click on Done to save settings to the selected file path.
### Help
For more information and concerns about the application, visit the Help menu to raise an issue on our Github page or visit the documentation for difficulties with usage.

### Notifications Panel
Additionally, the notifications panel allows you to gain insights into the data acquisition process and if specific steps during the saving and/or acquisition process are successfully completed or run into issues. 

## Acquisition and Saving
After configuring the desired settings, click on Begin Acquisition to establish connection with the NI System or other added devices and create AO/AI tasks. The notifications panel will indicate if the acquisition process has begun or run into any faults.

Once acquisition begins safely, the Save Button is enabled and on clicking it, the data collected is saved into





## Experiment Data and Exiting the Application
