(Devices)=
# Example: Other Devices


(Alicats)=
## Alicat Devices
The devices supported Alicat devices right now are only mass flow controller and mass flow meter that communicate via serial commuication. There may be a possibilty of including devices that communicate via ethernet. Please raise an issue if you would like to contribute to include such functionaility or would like to see such functionaility in future releases.

(MFCs)=
### Mass Flow Controller (MFC)

You can add an MFC by clicking the "Add MFC" button in the menubar or using the corresponding key-binding for this action.

```{image} assets/Devices/MFC/AddMFCMenu.png
:width: 400px
:align: center
:alt: MFCMenu
```

This will open a dialogbox, as shown below, that will ask for a name for the device. Only unique names will be accepted.
```{image} assets/Devices/MFC/AddMFCPopUp.png
:alt: MFCPop-up
:width: 200px
:align: center
```
Once, the name for the device is accepted, a new tab will open in the main GUI below the input settings. It will have options to select from available COM ports, select a gas for setting on the MFC device, and to finally a set point for the controller. The default setpoint is 0.0 (slpm/sccm).

```{image} assets/Devices/MFC/MFCPane_Propane.png
:alt: MFCPane
:width: 700px
:align: center
```

You can then establish connection with the selected conditions, and control the set-point of the MFC. These updates will be shown in the notificatoin panel, as shown in the example below.

```{image} assets/Devices/MFC/MFCConnection.png
:alt: MFCConnection
:width: 700px
:align: center
```

````{important}
Connection to All MFCs need to be established before acquisition can begin.     
````

```{note}
Currently, acquisition with Alicat device is only supported if acquisitoin from an NI device is setup.
```

```{warning}
MFC device communication could be slower communication with NI devices and could result in data loss above 5Hz NI acquisition. 
```
(MFMs)=
### Mass Flow Meter (MFM)

Mass flow meter interface is similar to that of MFC except for the control set point. The MFM pane will look something like below.

```{image} assets/Devices/MFMPane.png
:alt: MFMPane
:width: 700px
:align: center
```

```{note}
The future scope involves updating the flow-meter value in the area shown in the above snapshot. This is not updated yet. Please raise an issue if this has not been adressed yet.

```

```{warning}
This feature has not been tested entirely on an Alicat MFM device and the data is not currently acquired. Please raise an issue in case you face any problems and if this has not been addressed yet.
```

(Thor)=
## ThorlabsCLD101X

The ThorLabsCLD101X device will show a pane as seen in the figure below. You can select the COM port for the device and establish connection. The P, I, D, and the oscillation period values will be updated to the current values on the device. The placeholder values shown here are not used to set the PID and oscillation period values.

The Set TEC temperature button is only enabled if the connection is established succesfully. 

The Set Laser output button is only enabled if the TEC is on.

```{image} assets/Devices/ThorLabsCLD101XPane.png
:alt: ThorLabsCLD101XPane
:width: 700px
:align: center
```

```{note}
There is currently no acquisition of any data setup for this device during acquisition. There is no plan to acquire data from this device. This is only useful for a setup. If you require acquisition for this device, please send a pull request with your proposed changes to the dev branch or raise an issue.
```

```{warning}
This feature may require additional testing on the CLD101X device.
```