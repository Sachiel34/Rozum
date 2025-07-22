from pymodbus.client import ModbusTcpClient
import numpy
import time

class PS_control:
    def __init__(self, ip, port, id):
        self.ip = ip
        self.port = port
        self.id = id
        self.client = ModbusTcpClient(ip)
        self.client.connect()
        self.client.write_coil(402, 1, device_id=1) 

    def scale_handler(self, value):
        new_value = (value - 0)/(102 - 0)*(53477 - 0) + 0
        print(new_value)
        return new_value
    
    def change_volt(self, current_volt):
        print('Volt_set')
        self.client.write_register(500, int(self.scale_handler(current_volt)/2))

    def change_current(self, current_current):
        print('Current_set')
        self.client.write_register(501, int(self.scale_handler(current_current)/0.04))

    def change_power(self, current_power):
        print('Power_set')
        self.client.write_register(502, int(self.scale_handler(current_power)/3.2))

    def DC_on(self):
        print('DC_on')
        self.client.write_coil(405, 1)

    def DC_off(self):
        print('DC_off')
        self.client.write_coil(405, 0)

    def power_off(self):
        self.change_power(0)
        self.change_current(0)
        self.change_volt(0)
        self.client.write_coil(402, 0)
        
        self.client.close()

# SU1 = PS_control('192.168.1.134', '502', '1')
# SU1.change_current(2)
# time.sleep(1)
# SU1.change_power(7)
# # time.sleep(5)
# SU1.change_volt(17)
# time.sleep(5)
# # SU1.DC_on()
# # time.sleep(10)
# SU1.DC_off()
# time.sleep(1)
# SU1.power_off()
# #SU1.change_current(15)