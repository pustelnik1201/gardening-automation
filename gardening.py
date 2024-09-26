import network
from machine import Pin, ADC
from time import ticks_ms
PI = 3.1416

# used if params not given in constructors
PUMP_SPEED 	= 34 # [ml/s]
TUBE_DIAM	= 5  # [mm]
WATER_MLS	= 50 # [ml]

class Sector:	
    # constructor
    def __init__(self, pump_pin, soil_moist_pin, soil_moist_to_water, tube_length, water_mls=WATER_MLS, tube_diam=TUBE_DIAM, pump_speed=PUMP_SPEED):
        # init sector's pump
        self.pump = Pin(pump_pin, Pin.OUT)
        self.pump.value(0)
        
        # init sector's sensor
        self.soil_moist = ADC(Pin(soil_moist_pin))
        self.soil_moist.atten(ADC.ATTN_11DB)
        self.soil_moist_read = self.soil_moist.read()
        
        # moisture indicating a need for watering
        self.soil_moist_low = soil_moist_to_water 
        
        self.water_mls = water_mls
        # V = PI * r^2 * length [mm^3] -> *0.001 -> [ml]
        self.tube_volume = (tube_diam/2) * (tube_diam/2) * tube_length * 0.001
        self.pump_speed = pump_speed
        # used for watering automatically
        self.needs_watering = False
    
    def Sectors(self, pump_pins, moist_pins, water_mls, tube_length, tube_diam=None, pump_speed=None):
        # assign global lib tube diameter if not given
        if tube_diam is None:
            tube_diam = [TUBE_DIAM] * len(pump_pins)  
        # assign global lib pump speed if not given
        if pump_speed is None:
            pump_speed = [PUMP_SPEED] * len(pump_pins)
        # construct a list of Sector objects
        sectors = [
            Sector(pump_pins[i], moist_pins[i], water_mls[i], tube_length[i], tube_diam=tube_diam[i], pump_speed=pump_speed[i])
            for i in range(len(pump_pins))
            ]
        return sectors
    
    # reading moisture and checking whether watering needed
    def read_moist(sectors):
        # checking if sectors is a single Sector:
        if isinstance(sectors, Sector):
            sectors.soil_moist_read = self.soil_noist.read()
            if sectors.soil_moist_read > sectors.soil_moist_low:
                sectors.needs_watering = True
        # checking if sectors is a list of Sectors
        elif isinstance(sectors, list):
            for x in sectors:
                sectors[x].soil_moist_read = self.soil_moist.read()
                if sectors[x].soil_moist_read > sectors[x].soil_moist_low:
                    sectors[x].needs_watering = True
    
    #  watering every time when called
    def water(self, water_mls=None):
        # taking object mls as a default
        if water_mls is None:
            water_mls = self.water_mls
        
        # time for controlling watering time
        water_current_time = ticks_ms()
        water_prev_time = water_current_time
        
        print('volume: ', self.tube_volume, ' [mm^3]')
        print('water amount: ', water_mls, ' [mL]')
        # calculating how long to pump water
        water_time = float((self.tube_volume + water_mls)) / float(self.pump_speed)
        
        print('watering for: ', water_time, ' [s]')
        # powering pump for calculated period
        while water_current_time - water_prev_time < water_time * 1000:
            self.pump.value(1)
            water_current_time = ticks_ms()
            #print('...watering: ', water_current_time - water_prev_time, ' [s]')
        print('watering done!')
        self.pump.value(0)
    
    # watering when sector needs it
    def water_automatically(sectors):
        # checking if sectors is a single Sector
        if isinstance(sectors, Sector):
            #watering sector if water needed
            if sectors.needs_watering:
                sectors.water()
                print('Sector watered!')
        # checking if sectors is a list of Sectors
        elif isinstance(sectors, list):
            # watering all sectors needing water
            for x in sectors:
                if sectors[x].needs_watering:   
                    sectors[x].water()
                    print('Sector ', x, ' watered!')

# initialising wifi connection
def connect_to_wifi(WIFI_SSID, WIFI_PASS):
    wifi = network.WLAN(network.STA_IF)
    if not wifi.isconnected():
        print("Connecting to WiFi...")
        wifi.active(True)
        wifi.connect(WIFI_SSID, WIFI_PASS)
        while not wifi.isconnected():
            pass
    print('IP:', wifi.ifconfig()[0])
    


