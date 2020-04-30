import win32service
import win32serviceutil
import win32api
import win32event
import openHardwareMonitorPrometheusExporter
import time

class aservice(win32serviceutil.ServiceFramework):
    _svc_name_ = "OpenHardwareMonitorPrometheusExporter"
    _svc_display_name_ = "Open Hardware Monitor Prometheus Exporter"
    _svc_description_ = "Exports Open Hardware Monitor Statistics on localhost:9398/metrics"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.isAlive = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.isAlive = False
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        import servicemanager
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))

        exporter = openHardwareMonitorPrometheusExporter.OHM_Exporter()
        while self.isAlive:
            exporter.update_metrics()
            time.sleep(1)
        win32event.WaitForSingleObject(self.hWaitStop, 200)


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(aservice)
