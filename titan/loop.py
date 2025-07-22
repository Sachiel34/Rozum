from modbus_PSEA import PS_control
import math
import time 

SU1 = PS_control('192.168.1.134', '502', '1')
SU1.DC_on()
SU1.change_current(2)
SU1.change_power(5)

steps = 0 # задать количество шагов
start_volt = 0
second = 0

# count_step = round(steps * 42.025 + 1)
count_step = round(steps * 41.7 + 1)
while count_step!= 0:
    # const = 0.0238 # константа смещения
    const = 0.024
    SU1.change_volt(start_volt)
    start_volt +=const
    time.sleep(1)
    print('v =', start_volt)
    count_step = count_step - 1
    print('count_step =', count_step)

print('-------------pause---------------')

for i in range(second, 0, -1):
    min = i//60
    sec = i % 60
    time.sleep(1)
    print('Осталось времени:', min , 'мин', sec, 'сек')


count_step = steps
# count_step = round(steps * 42.025)
count_step = round(steps * 41.7)

# steps = steps * 0,25
while count_step!= 0:
    SU1.change_volt(start_volt)
    start_volt = start_volt - const
    time.sleep(1)
    print('v =', start_volt)
    count_step = count_step - 1
    print('count_step =', count_step)

SU1.change_volt(0)
time.sleep(10)
SU1.DC_off()
SU1.power_off()  






