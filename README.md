# Open Hardware Monitor Prometheus Exporter
This Script will expose an Prometheus metric endpoint at ```localhost:9398/metrics```

#### Currently exported metrics:

* CPU Information:
    * Name and Identifier
    * Temperature
    * Load
    * Power Usag
* Mainboard Name and Identifier
* RAM Used and available
* GPU Information:
    * Temperature
    * Load
    * Fan speed
    * VRAM Used and Available
* Disk Usage and Temperature


### Requirements
- Open Hardware Monitor Running
- prometheus_client
- wmi

### Installing
**Notes:** Administrative rights might be required.When running as service custom firewall rules might be necessary

There is a Windows Service included which can be used to start the script automatically.
To use the service first install it using:


```
## With Autostart: 
python windowsService.py --startup auto install
## Without
python windowsService.py install
```

Once installed the service can be started/stopped using
```
python windowsService.py start/stop
```

The Service can be removed using

```
python windowsService.py remove
```

## Acknowledgments

* This Project was inspired by [rgl´s Prometheus Exporter](https://github.com/rgl/OpenHardwareMonitorExporter)
