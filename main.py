import BlynkLib
import network
from machine import Pin, idle, ADC
from time import sleep, ticks_ms
from gardening import Sector, Sectors, connect_to_wifi

# credentials to connect to Wifi and Blynk IoT
BLYNK_AUTH =
WIFI_SSID = 
WIFI_PASS = 

water_mls1 = 300

pump_speed = [40, 34, 34, 34]
# PIN rundown
pump_pins 		= [16, 2, 19, 5]
moist_pins 		= [36, 39, 34, 35]
sensor_pins 	= [32, 33, 25]

# Sector params
water_mls 		= [water_mls1, 100, 100, 100]
tube_length		= [50, 100, 100, 100]
tube_diam		= [5.5, 5.5, 5.5, 5.5]
moist_lowest 	= [1800, 1800, 1800, 1800] 

led = Pin(27, Pin.OUT)
# button = Pin(#, Pin.IN)

# Sectors definition
# (pump pin, soil moist pin, tube length)
sectors = Sectors(pump_pins, moist_pins, moist_lowest, tube_length, water_mls=water_mls, tube_diam=tube_diam, pump_speed=pump_speed)

#---INIT START---
led.value(1)
#blynk_disconnected = True

# Connecting to Wifi
connect_to_wifi(WIFI_SSID, WIFI_PASS)

# Connecting to Blynk IoT
blynk = BlynkLib.Blynk(BLYNK_AUTH)

#def connect_to_Blynk(b, b_disconnected):
#    while b_disconnected == True:
#        print('trying to reconnect')
#        b.connect()
#        sleep(5)
    
# Blynk event handlings
@blynk.on("connected")
def blynk_connected(ping):
    print('Blynk ready. Ping:', ping, 'ms')
    #---INIT END---
    led.value(0)
    blink_disconnected = False

@blynk.on("disconnected")
def blynk_disconnected():
    print('Blynk disconnected')
    led.value(1)
    blynk_disconnected = True

@blynk.on("V1")
def v0_write_handler(value):
    print('Current slider value: {}'.format(value[0]))
    sectors[0].water_mls = int(value[0])
    print('water_mls: ', sectors[0].water_mls)

@blynk.on("V27")
def v0_write_handler(value):
    print('Current slider value: {}'.format(value[0]))
    slider_state = int(value[0])
   
    if slider_state is 0:
        led.value(0)
    else:
        led.value(1)
    sectors[0].water()
    
def write_analog_value(value):
    # Ensure value is within the range
    if 0 <= value <= 2800:
        blynk.virtual_write(36, value)  # Writing to V36
        print(f"Wrote {value} to V36")
    else:
        print("Value out of range. Must be between 0 and 2500.")
    
led.value(0)
while True:
    # mapping current time
    #current_time = ticks_ms() * 1000 # [s]
    #connect_to_Blynk(blynk, blynk_disconnected)
    
    blynk.run()
    Sector.read_moist(sectors)
    write_analog_value(sectors[0].soil_moist_read)
    sleep(5)

# You can also run blynk in a separate thread (ESP32 only)
#import _thread
#_thread.stack_size(5*1024)
#_thread.start_new_thread(runLoop, ())

