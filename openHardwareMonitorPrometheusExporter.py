from prometheus_client import start_http_server, Gauge, Info
import wmi, time, socket


class OHM_Exporter():

    def __init__(self):
        self.host = socket.gethostname()
        self.wmi_connection = wmi.WMI(namespace="root\\OpenHardwareMonitor")
        # Wait for Open Hardware Monitor
        while True:
            if len(self.wmi_connection.Hardware()) > 0:
                break
            time.sleep(1)
        # Wait for Open Hardware Monitor to collect resources
        time.sleep(5)
        # Start Exporter
        start_http_server(9398)
        self.setupEndpoints()

    def setupEndpoints(self):
        self.cpu_identifier = {}
        self.gpu_identifier = {}
        self.disk_identifier = {}
        for x in self.wmi_connection.Hardware():
            if x.HardwareType== "RAM":
                self.ram_identifier = x.identifier
                ram_name = x.name
            elif x.HardwareType == "Mainboard":
                print(x.parent)
                mainboard_name = x.name
                self.mainboard_identifier = x.identifier
            elif x.HardwareType == "CPU":
                self.cpu_identifier[x.identifier] = x.name
            elif x.HardwareType == "GpuNvidia" or x.HardwareType == "GpuAti":
                self.gpu_identifier[x.identifier] = x.name
            elif x.HardwareType == "HDD":
                self.disk_identifier[x.identifier] = x.name
        total_ram = 0
        vram = {}
        for x in self.wmi_connection.Sensor():
            if x.parent==self.ram_identifier:
                if x.name == "Available Memory" or x.name == "Used Memory":
                    total_ram += x.value*1024
            if x.name == "GPU Memory Total":
                vram[x.parent] = x.value
        total_ram = int(total_ram)

        # Cpu
        self.cpu_info = Info("ohm_cpu", "CPU Info", ["identifier"])
        for x in self.cpu_identifier:
            self.cpu_info.labels(x).info({"host" : self.host, "name" : self.cpu_identifier[x]})
        self.cpu_temperature_gauge = Gauge("ohm_cpu_temperature", "Cpu core temperature", ["host", "identifier","parent", "name"])
        self.cpu_load_gauge = Gauge("ohm_cpu_load", "Cpu core load", ["host", "identifier","parent", "name"])
        self.cpu_power_gauge = Gauge("ohm_cpu_power", "Cpu power usage in Watt", ["host", "identifier","parent", "name"])
        # Mainboard
        self.mainboard_info = Info("ohm_mainboard", "Mainboard Info")
        self.mainboard_info.info({"host" : self.host, "identifier" : self.mainboard_identifier, "name" : mainboard_name})
        # Memmory
        self.ram_info = Info("ohm_ram", "RAM Info")
        self.ram_info.info({"host" : self.host, "identifier" : self.ram_identifier, "name" : ram_name, "total_memory" : str(total_ram)})
        self.ram_available_gauge = Gauge("ohm_ram_available", "RAM available", ["host"])
        self.ram_used_gauge = Gauge("ohm_ram_used", "RAM used", ["host"])
        # GPU
        self.gpu_info = Info("ohm_gpu", "GPU Info", ["identifier"])
        for x in self.gpu_identifier:
            self.gpu_info.labels(x).info({"host" : self.host, "name" : self.gpu_identifier[x], "total_memory" : str(vram[x])})
        self.gpu_temperature_gauge = Gauge("ohm_gpu_temperature", "Gpu core temperature", ["host", "identifier", "parent", "name"])
        self.gpu_load_gauge = Gauge("ohm_gpu_load", "Gpu load", ["host", "identifier", "parent", "name"])
        self.gpu_fans_gauge = Gauge("ohm_gpu_fans", "Gpu fan speed", ["host", "identifier", "parent", "name"])
        self.gpu_vram_available_gauge = Gauge("ohm_gpu_vram_available", "Gpu vram", ["host", "identifier", "parent", "name"])
        self.gpu_vram_used_gauge = Gauge("ohm_gpu_vram_used", "Gpu vram", ["host", "identifier", "parent", "name"])
        # Storage
        self.disk_usage_gauge = Gauge("ohm_disk_usage", "Disk Usage in %", ["host", "identifier", "name"])
        self.disk_temperature_gauge = Gauge("ohm_disk_temperature", "Disk Temperature in °C", ["host", "identifier", "name"])

    def update_metrics(self):
        for x in self.wmi_connection.Sensor():
            if x.parent in self.cpu_identifier:
                if x.SensorType == "Temperature":
                    self.cpu_temperature_gauge.labels(self.host, x.identifier, x.parent, x.name).set(x.value)
                elif x.SensorType == "Load":
                    self.cpu_load_gauge.labels(self.host, x.identifier, x.parent, x.name).set(round(x.value,1))
                elif x.SensorType == "Power":
                    self.cpu_power_gauge.labels(self.host, x.identifier, x.parent, x.name).set(round(x.value,1))
            elif x.parent == self.ram_identifier:
                if x.name == "Available Memory":
                    self.ram_available_gauge.labels(self.host).set(int(x.value*1024))
                elif x.name == "Used Memory":
                    self.ram_used_gauge.labels(self.host).set(int(x.value * 1024))
            elif x.parent in self.gpu_identifier:
                if x.SensorType == "Temperature":
                    self.gpu_temperature_gauge.labels(self.host, x.identifier, x.parent, x.name).set(x.value)
                elif x.SensorType == "Load":
                    self.gpu_load_gauge.labels(self.host, x.identifier, x.parent, x.name).set(x.value)
                elif x.SensorType == "Fan":
                    self.gpu_fans_gauge.labels(self.host, x.identifier, x.parent, x.name).set(x.value)
                elif x.name == "GPU Memory Free":
                    self.gpu_vram_available_gauge.labels(self.host, x.identifier, x.parent, x.name).set(round(x.value,1))
                elif x.name == "GPU Memory Used":
                    self.gpu_vram_used_gauge.labels(self.host, x.identifier, x.parent, x.name).set(round(x.value,1))
            elif x.parent in self.disk_identifier:
                if x.SensorType == "Temperature":
                    self.disk_temperature_gauge.labels(self.host, x.parent, self.disk_identifier[x.parent]).set(x.value)
                elif x.SensorType == "Load":
                    self.disk_usage_gauge.labels(self.host, x.parent, self.disk_identifier[x.parent]).set(round(x.value,2))


if __name__ == "__main__":
    exporter = OHM_Exporter()
    while True:
        exporter.update_metrics()
        time.sleep(2)
