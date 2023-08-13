"""

M5Stack Core 2 regulated thermostat
===================================

Author:     X. Mayeur
Version:    v1.0

Hardware:   M5Stack Core2
            DHT22 on pin 33
            mini relay module on pin 32

"""
import json
import time

import nvs
import unit
import wifiCfg
from easyIO import *
from esp import dht_readinto
from m5mqtt import M5mqtt
from m5stack import *
from m5stack import touch
from m5stack_ui import *
from uiflow import *
from machine import WDT 

screen = M5Screen()
screen.clean_screen()
screen.set_screen_bg_color(0xf9f5f5)
relay0 = unit.get(unit.RELAY, unit.PORTA)

# Default global variable initialisation
on = None
cmd_temp = None
week_schedule = None
d = None
temp = None
mode = None
edit_night = None
day_temp = None
edit_day = None
night_temp = None
brightness_flip = None
curr_day_schedule = None
curr_hrmin = None
curr_temp = None
prev_time_exit = None
curr_period = None
timeout_on = None
prev_weekday = None
prev_time_clock = None
prev_time_publish = None
prev_time_regu = None
prev_time_on = None
X = None
prev_time_screen = None
Y = None
timeout_screen = None
time_zone = 2
config = {}
relay_state = False
prev_relay_state = False

# Load UI screen
moon = M5Img("res/moon.png", x=163, y=87, parent=None)
sun = M5Img("res/sun.png", x=45, y=80, parent=None)
line0 = M5Line(x1=0, y1=80, x2=320, y2=80, color=0x0000ff, width=3, parent=None)
t = M5Label('20.00', x=35, y=13, color=0x0b0b0b, font=FONT_MONT_48, parent=None)
t_day = M5Label('18', x=65, y=145, color=0x000, font=FONT_MONT_28, parent=None)
t_night = M5Label('14', x=163, y=145, color=0x000, font=FONT_MONT_28, parent=None)
state = M5Switch(x=218, y=19, w=90, h=40, bg_c=0x390ba4, color=0x2bc25d, parent=None)
plus = M5Label('+', x=151, y=215, color=0x000, font=FONT_MONT_30, parent=None)
touch_day = M5Btn(text='JOUR', x=55, y=180, w=70, h=30, bg_c=0xf1e99d, text_c=0x000000, font=FONT_MONT_14, parent=None)
minus = M5Label('-', x=50, y=206, color=0x000, font=FONT_MONT_44, parent=None)
clock_lbl = M5Label('2021/01/01', x=35, y=59, color=0x1407a3, font=FONT_MONT_18, parent=None)
touch_night = M5Btn(text='NUIT', x=149, y=180, w=70, h=30, bg_c=0xf1e99d, text_c=0x000000, font=FONT_MONT_14,
                    parent=None)
OK = M5Label('OK', x=255, y=220, color=0x000, font=FONT_MONT_18, parent=None)
relay_btn = M5Btn(text='   .', x=7, y=61, w=15, h=15, bg_c=0xf60202, text_c=0xfa0303, font=FONT_MONT_14, parent=None)
touch_onoff = M5Btn(text='OFF', x=238, y=180, w=70, h=30, bg_c=0xf1e99d, text_c=0x000000, font=FONT_MONT_14,
                    parent=None)
line1 = M5Line(x1=0, y1=215, x2=320, y2=215, color=0x0000ff, width=1, parent=None)
battery_lbl = M5Label('Bat. 100 %', x=240, y=3, color=0x817c7c, font=FONT_MONT_14, parent=None)
label0 = M5Label('o', x=169, y=13, color=0x000, font=FONT_MONT_18, parent=None)
label1 = M5Label('o', x=195, y=145, color=0x000, font=FONT_MONT_14, parent=None)
mode_label = M5Label('ON', x=222, y=21, color=0x07b440, font=FONT_MONT_38, parent=None)
label2 = M5Label('o', x=100, y=145, color=0x000, font=FONT_MONT_14, parent=None)
thermometer = M5Img("res/thermometer.png", x=-7, y=13, parent=None)
auto_txt = M5Label('AUTO', x=274, y=30, color=0xffffff, font=FONT_MONT_12, parent=None)
start_lbl = M5Label('0630', x=25, y=102, color=0x000, font=FONT_MONT_14, parent=None)
end_lbl = M5Label('2230', x=123, y=102, color=0x000, font=FONT_MONT_14, parent=None)

from numbers import Number

print('load config')
try:
    config = json.load(open('config.json', 'r'))
    day_temp = config['day_temp']
    night_temp = config['night_temp']
    timeout_screen = config['timeout_screen']
    time_zone = config['time_zone']
    wifi_ssid = config['wifi_ssid']
    mqtt_host = config['mqtt_host']
    mqtt_user = config['mqtt_user']

except OSError:
    config = {
        'day_temp': 20,
        'night_temp': 14,
        'timeout_screen': 120000,
        'time_zone': 2,
        'wifi_ssid': 'Proximus-Home-385603',
        'mqtt_host': '192.168.129.5',
        'mqtt_user': 'IoT'
    }
    json.dump(config, open('config.json', 'w'))

nvs.write(str('wifi_pwd'), '6xd3nf2yrbcaan6u')
# nvs.write(str('mqtt_pwd'), 'Bretzel58')
print('Connect to wifi')
wifiCfg.doConnect(wifi_ssid, (nvs.read_str('wifi_pwd')))
print('set up real-time clock')
rtc.settime('ntp', host='de.pool.ntp.org', tzone=time_zone)

# Connect to DHT22 temperature /  humidity sensor
DHT_PIN = 33
buf = bytearray(5)


def humidity():
    try:
        dht_readinto(DHT_PIN, buf)
        return (buf[0] << 8 | buf[1]) * 0.1
    except:
        return 0


def temperature():
    try:
        dht_readinto(DHT_PIN, buf)
        t = ((buf[2] & 0x7F) << 8 | buf[3]) * 0.1
        if buf[2] & 0x80:
            t = -t
        # print ('temp: ', t)
        return t
    except:
        return 0


# Global variable initialization with default values
def init():
    global on, cmd_temp, week_schedule, d, temp, mode, edit_night, day_temp, edit_day, night_temp, brightness_flip
    global curr_day_schedule, curr_hrmin, curr_temp, prev_time_exit, curr_period, timeout_on, prev_weekday
    global prev_time_clock, prev_time_publish, prev_time_regu, prev_time_on, X, prev_time_screen, Y, timeout_screen
    global config
    print('load schedule')
    try:
        week_schedule = json.load(open('weekSchedule.json', 'r'))
    except:
        week_schedule = [[{'start': '0630', 'end': '2330'}], [{'start': '0631', 'end': '2330'}],
                         [{'start': '0632', 'end': '2200'}], [{'start': '0633', 'end': '2330'}],
                         [{'start': '0635', 'end': '0853'}, {'start': '0855', 'end': '2330'}],
                         [{'start': '0636', 'end': '2330'}], [{'start': '0637', 'end': '2330'}]]
        json.dump(week_schedule, open('weekSchedule.json', 'w'))

    print('init variables')
    t_night.set_text(str(night_temp))
    t_day.set_text(str(day_temp))
    brightness_flip = False
    edit_day = False
    edit_night = False
    curr_temp = 0
    mode = 'AUTO'
    prev_time_clock = time.ticks_ms()
    prev_time_regu = time.ticks_ms()
    prev_time_exit = time.ticks_ms()
    prev_time_publish = time.ticks_ms()
    prev_time_screen = 0
    prev_time_on = 0
    prev_weekday = -1
    timeout_on = 0
    curr_hrmin = 0
    t.set_text(str(curr_temp))
    mode_label.set_hidden(True)
    show_plus_minus(False)
    set_AUTO()


# Use the week schedule object to know what is the current temperature command for the thermostat
def set_cmd_temp_auto():
    global on, cmd_temp, week_schedule, d, temp, mode, edit_night, day_temp, edit_day, night_temp, brightness_flip
    global curr_day_schedule, curr_hrmin, curr_temp, prev_time_exit, curr_period, timeout_on, prev_weekday
    global prev_time_clock, prev_time_regu, prev_time_on, X, prev_time_screen, Y, timeout_screen
    d = (rtc.datetime()[3]) + 1
    # ("rtc day is " + str(d))
    curr_day_schedule = week_schedule[int(d - 1)]
    curr_hrmin = (rtc.datetime()[5]) + (rtc.datetime()[4]) * 100

    for curr_period in curr_day_schedule:
        try:
            if int((curr_period['start'])) <= curr_hrmin < int((curr_period['end'])):
                temp = day_temp
                print(curr_period['start'])
                start_lbl.set_text(str(curr_period['start']))
                print(curr_period['end'])
                end_lbl.set_text(str(curr_period['end']))
                state.set_on()
                auto_txt.set_pos(226, 34)
                break
        except:
            _msg = 'error in weekschedule config'
            log(_msg)

    if temp != day_temp:
        temp = night_temp
        start_lbl.set_text(' ')
        end_lbl.set_text(' ')
        auto_txt.set_pos(272, 34)
        state.set_off()

    return temp


# Force the thermostat to stay on regulated DAY mode (until next day)
def DAY():
    global on, cmd_temp, week_schedule, d, temp, mode, edit_night, day_temp, edit_day, night_temp, brightness_flip, \
        curr_day_schedule, curr_hrmin, curr_temp, prev_time_exit, curr_period, timeout_on, prev_weekday, \
        prev_time_clock, prev_time_regu, prev_time_on, X, prev_time_screen, Y, timeout_screen
    mode = 'DAY'
    mode_label.set_hidden(True)
    state.set_on()
    state.set_hidden(False)
    touch_onoff.set_btn_text('AUTO')
    cmd_temp = day_temp
    timeout_on = 0
    auto_txt.set_hidden(True)


# # Force the thermostat to stay on NIGHT regulated mode (until next day)
def NIGHT():
    global on, cmd_temp, week_schedule, d, temp, mode, edit_night, day_temp, edit_day, night_temp, brightness_flip, curr_day_schedule, curr_hrmin, curr_temp, prev_time_exit, curr_period, timeout_on, prev_weekday, prev_time_clock, prev_time_regu, prev_time_on, X, prev_time_screen, Y, timeout_screen
    mode = 'NIGHT'
    mode_label.set_hidden(True)
    state.set_off()
    state.set_hidden(False)
    touch_onoff.set_btn_text('AUTO')
    cmd_temp = night_temp
    timeout_on = 0
    auto_txt.set_hidden(True)


# Force th thermostat to be always ON for the next 5 minutes
def set_ON():
    global on, cmd_temp, week_schedule, d, temp, mode, edit_night, day_temp, edit_day, night_temp, brightness_flip, \
        urr_day_schedule, curr_hrmin, curr_temp, prev_time_exit, curr_period, timeout_on, prev_weekday, prev_time_clock, \
        prev_time_regu, prev_time_on, X, prev_time_screen, Y, timeout_screen
    mode = 'ON'
    mode_label.set_hidden(False)
    mode_label.set_text_color(0x006600)
    mode_label.set_text('ON')
    cmd_temp = 100
    touch_onoff.set_btn_text('AUTO')
    state.set_hidden(True)
    relay_btn.set_hidden(False)
    relay0.on()
    prev_time_on = time.ticks_ms()
    timeout_on = 60000
    auto_txt.set_hidden(True)


# Switch off the thermostat function
def set_OFF():
    global on, cmd_temp, week_schedule, d, temp, mode, edit_night, day_temp, edit_day, night_temp, brightness_flip, curr_day_schedule, curr_hrmin, curr_temp, prev_time_exit, curr_period, timeout_on, prev_weekday, prev_time_clock, prev_time_regu, prev_time_on, X, prev_time_screen, Y, timeout_screen
    mode = 'OFF'
    mode_label.set_hidden(False)
    mode_label.set_text_color(0xff0000)
    mode_label.set_text('OFF')
    state.set_hidden(True)
    touch_onoff.set_btn_text('ON')
    cmd_temp = 0
    relay_btn.set_hidden(True)
    relay0.off()
    timeout_on = 0
    auto_txt.set_hidden(True)


# set the thermostat in automatic & regulated more, according to week schedule
def set_AUTO():
    global on, cmd_temp, week_schedule, d, temp, mode, edit_night, day_temp, edit_day, night_temp, brightness_flip, curr_day_schedule, curr_hrmin, curr_temp, prev_time_exit, curr_period, timeout_on, prev_weekday, prev_time_clock, prev_time_regu, prev_time_on, X, prev_time_screen, Y, timeout_screen
    mode = 'AUTO'
    mode_label.set_hidden(True)
    state.set_hidden(False)
    touch_onoff.set_btn_text('OFF')
    cmd_temp = set_cmd_temp_auto()
    timeout_on = 0
    auto_txt.set_hidden(False)


# Show the day/night temperture edit button
def show_plus_minus(on):
    global cmd_temp, week_schedule, d, temp, mode, edit_night, day_temp, edit_day, night_temp, brightness_flip, curr_day_schedule, curr_hrmin, curr_temp, prev_time_exit, curr_period, timeout_on, prev_weekday, prev_time_clock, prev_time_regu, prev_time_on, X, prev_time_screen, Y, timeout_screen
    if on:
        plus.set_hidden(False)
        minus.set_hidden(False)
        OK.set_hidden(False)
    else:
        plus.set_hidden(True)
        minus.set_hidden(True)
        OK.set_hidden(True)


# Hide the day/night temperture edit button
def hide_edit_button():
    global on, cmd_temp, week_schedule, d, temp, mode, edit_night, day_temp, edit_day, night_temp, brightness_flip, curr_day_schedule, curr_hrmin, curr_temp, prev_time_exit, curr_period, timeout_on, prev_weekday, prev_time_clock, prev_time_regu, prev_time_on, X, prev_time_screen, Y, timeout_screen
    edit_night = False
    edit_day = False
    show_plus_minus(False)


# Regulate the temperature around the command +/- 1°c
def regu():
    global cmd_temp, curr_temp, relay_state, prev_relay_state, m5mqtt

    if curr_temp > float(cmd_temp) + 0.5:
        relay0.off()
        relay_state = False
        relay_btn.set_hidden(True)
    else:
        if curr_temp < float(cmd_temp) - 0.5:
            relay0.on()
            relay_state = True
            relay_btn.set_hidden(False)
    if prev_relay_state != relay_state:
        m5mqtt.publish('thermostat/relay', str(relay_state))
    prev_relay_state = relay_state


# Assign the different buttons of the UI
def state_off():
    global cmd_temp, week_schedule, d, temp, mode, edit_night, day_temp, edit_day, night_temp, brightness_flip, curr_day_schedule, on, curr_hrmin, curr_temp, prev_time_exit, timeout_on, prev_weekday, prev_time_clock, curr_period, prev_time_regu, prev_time_on, X, prev_time_screen, Y, timeout_screen
    NIGHT()
    auto_txt.set_hidden(True)
    publish_state()


state.off(state_off)


def state_on():
    global cmd_temp, week_schedule, d, temp, mode, edit_night, day_temp, edit_day, night_temp, brightness_flip, curr_day_schedule, on, curr_hrmin, curr_temp, prev_time_exit, timeout_on, prev_weekday, prev_time_clock, curr_period, prev_time_regu, prev_time_on, X, prev_time_screen, Y, timeout_screen
    DAY()
    auto_txt.set_hidden(True)
    publish_state()


state.on(state_on)


def touch_day_pressed():
    global cmd_temp, week_schedule, d, temp, mode, edit_night, day_temp, edit_day, night_temp, brightness_flip, curr_day_schedule, on, curr_hrmin, curr_temp, prev_time_exit, timeout_on, prev_weekday, prev_time_clock, curr_period, prev_time_regu, prev_time_on, X, prev_time_screen, Y, timeout_screen
    cmd_temp = day_temp
    edit_day = True
    show_plus_minus(True)
    prev_time_exit = time.ticks_ms()
    publish_state()


touch_day.pressed(touch_day_pressed)


def touch_night_pressed():
    global cmd_temp, edit_night, prev_time_exit
    cmd_temp = night_temp
    edit_night = True
    show_plus_minus(True)
    prev_time_exit = time.ticks_ms()
    pass


touch_night.pressed(touch_night_pressed)


def touch_onoff_pressed():
    global mode
    show_plus_minus(False)
    auto_txt.set_hidden(True)
    if mode == 'AUTO':
        set_OFF()
    elif mode == 'ON':
        set_AUTO()
        auto_txt.set_hidden(False)
    elif mode == 'NIGHT':
        set_AUTO()
    elif mode == 'DAY':
        set_AUTO()
    else:
        set_ON()
    publish_state()


touch_onoff.pressed(touch_onoff_pressed)


def buttonA_wasPressed():
    global cmd_temp, week_schedule, d, temp, mode, edit_night, day_temp, edit_day, night_temp, brightness_flip, curr_day_schedule, on, curr_hrmin, curr_temp, prev_time_exit, timeout_on, prev_weekday, prev_time_clock, curr_period, prev_time_regu, prev_time_on, X, prev_time_screen, Y, timeout_screen
    if edit_night:
        night_temp = (night_temp if isinstance(night_temp, Number) else 0) + -1
        t_night.set_text(str(night_temp))
        cmd_temp = night_temp
    else:
        if edit_day:
            day_temp = (day_temp if isinstance(day_temp, Number) else 0) + -1
            t_day.set_text(str(day_temp))
            cmd_temp = day_temp
        else:
            pass
    pass


btnA.wasPressed(buttonA_wasPressed)


def buttonB_wasPressed():
    global cmd_temp, week_schedule, d, temp, mode, edit_night, day_temp, edit_day, night_temp, brightness_flip, curr_day_schedule, on, curr_hrmin, curr_temp, prev_time_exit, timeout_on, prev_weekday, prev_time_clock, curr_period, prev_time_regu, prev_time_on, X, prev_time_screen, Y, timeout_screen
    if edit_night:
        night_temp = (night_temp if isinstance(night_temp, Number) else 0) + 1
        t_night.set_text(str(night_temp))
        cmd_temp = night_temp
    else:
        if edit_day:
            day_temp = (day_temp if isinstance(day_temp, Number) else 0) + 1
            t_day.set_text(str(day_temp))
            cmd_temp = day_temp
        else:
            pass
    pass


btnB.wasPressed(buttonB_wasPressed)


def buttonC_wasPressed():
    global cmd_temp, week_schedule, d, temp, mode, edit_night, day_temp, edit_day, night_temp, brightness_flip, curr_day_schedule, on, curr_hrmin, curr_temp, prev_time_exit, timeout_on, prev_weekday, prev_time_clock, curr_period, prev_time_regu, prev_time_on, X, prev_time_screen, Y, timeout_screen
    hide_edit_button()
    config['night_temp'] = night_temp
    config['day_temp'] = day_temp
    json.dump(config, open('config.json', 'w'))
    publish_state()


btnC.wasPressed(buttonC_wasPressed)


def log(msg):
   global time, m5mqtt
   log_msg = {
    "time": time.ticks_ms(),
    "message": msg
   }
   m5mqtt.publish('/thermostat/log', json.dumps(log_msg))


def publish_state():
    global config, week_schedule, mode, cmd_temp, day_temp, night_temp, curr_temp, relay_state, m5mqtt
    _state = {
        "config": config,
        "week_schedule": week_schedule,
        "mode": mode,
        "curr_temp": curr_temp,
        "cmd_temp": cmd_temp,
        "day_temp": day_temp,
        "night_temp": night_temp,
        "relay": relay_state
    }
    m5mqtt.publish('thermostat/state', json.dumps(_state))


# Call back function for the subscription to mqtt topic thermostat/weekSchedule
def cb_schedule(topic_data):
    global week_schedule
    print('Got new schedule!')
    week_schedule = json.loads(topic_data)
    json.dump(topic_data, open('weekSchedule.json', 'w'))


def cb_day_temp(topic_data):
    global day_temp, config
    print('Got new day_temp')
    day_temp = int(topic_data)
    config['day_temp'] = day_temp
    json.dump(config, open('config.json', 'w'))
    t_day.set_text(str(day_temp))
    publish_state()


def cb_night_temp(topic_data):
    global night_temp, config
    print('Got new night_temp')
    night_temp = int(topic_data)
    config['night_temp'] = night_temp
    json.dump(config, open('config.json', 'w'))
    t_night.set_text(str(night_temp))
    publish_state()


def cb_timeout_screen(topic_data):
    global timeout_screen, config
    print('Got new timeout_screen')
    timeout_screen = int(topic_data) * 1000
    config['timeout_screen'] = timeout_screen
    json.dump(config, open('config.json', 'w'))


def cb_time_zone(topic_data):
    global time_zone, config
    print('Got new time_zone')
    time_zone = int(topic_data)
    config['time_zone'] = time_zone
    json.dump(config, open('config.json', 'w'))


def cb_mode(topic_data):
    print('Switch to mode ' + topic_data)
    if topic_data == 'AUTO':
        set_AUTO()
    elif topic_data == 'OFF':
        set_OFF()
    elif topic_data == 'ON':
        set_ON()
    elif topic_data == 'DAY':
        DAY()
    elif topic_data == 'NIGHT':
        NIGHT()
    else:
        print('Unknown mode')
        log('Unknown mode')
        
    publish_state()


def cb_state(topic_data):
    global m5mqtt

    try:
        publish_state()
    except:
        print('Cannot publish state!')
        wifiCfg.doConnect(wifi_ssid, (nvs.read_str('wifi_pwd')))
        m5mqtt = M5mqtt('Thermostat', mqtt_host, 1883, mqtt_user, (nvs.read_str('mqtt_pwd')), 300)
        m5mqtt.start()
        log('Reconnecting!')


# Start the main program

# All initiatilizations
init()
wdt = WDT(timeout = 360000) # start the system watch dog 
print('Start mqtt client')
m5mqtt = M5mqtt('Thermostat', mqtt_host, 1883, mqtt_user, (nvs.read_str('mqtt_pwd')), 300)
print('subscribe to topics')
m5mqtt.subscribe('thermostat/weekSchedule', cb_schedule)
m5mqtt.subscribe('thermostat/dayTemp', cb_day_temp)
m5mqtt.subscribe('thermostat/nightTemp', cb_night_temp)
m5mqtt.subscribe('thermostat/timeoutScreen', cb_timeout_screen)
m5mqtt.subscribe('thermostat/timeZone', cb_time_zone)
m5mqtt.subscribe('thermostat/mode', cb_mode)
m5mqtt.subscribe('thermostat/getState', cb_state)
print('start listening to events')
m5mqtt.start()
publish_state()

# always loop
while True:
    # Resync the real time clock every day, and force automatic mode unless OFF
    if (rtc.datetime()[3]) != prev_weekday:
        print('new day - schedule reset')
        try:
            rtc.settime('ntp', host='de.pool.ntp.org', tzone=time_zone)
        except:
            wifiCfg.doConnect(wifi_ssid, (nvs.read_str('wifi_pwd')))
            rtc.settime('ntp', host='de.pool.ntp.org', tzone=time_zone)
            log('Reconnecting...')

        if mode != 'OFF':
            mode = 'AUTO'

        try:
            week_schedule = json.load(open('weekSchedule.json', 'r'))
        except:
            pass
        
        prev_weekday = rtc.datetime()[3]

    # publish the temperature every 5 min
    if (time.ticks_ms()) > prev_time_publish + 300000:
        try:
            m5mqtt.publish('thermostat/temperature', str(curr_temp))
            _humidity = 0
            # _humidity = humidity()
            if _humidity != 0:
                m5mqtt.publish('thermostat/humidity', str(_humidity))
                print('Temp is ' + str(curr_temp) + 'C - Humidity is ' + str(_humidity) + '%')
            else:
                print('Temp is ' + str(curr_temp) + 'C')
            prev_time_publish = time.ticks_ms()
        except:
            print('Cannot publish!')
            wifiCfg.doConnect(wifi_ssid, (nvs.read_str('wifi_pwd')))
            m5mqtt = M5mqtt('Thermostat', mqtt_host, 1883, mqtt_user, (nvs.read_str('mqtt_pwd')), 300)
            m5mqtt.start()
            prev_time_publish = time.ticks_ms() + 290000
            log('Reconnecting!')
            
        wdt.feed()

    # Adjust displayed time each second
    if (time.ticks_ms()) > prev_time_clock + 1000:
        clock_lbl.set_text(str(rtc.printRTCtime()))
        prev_time_clock = time.ticks_ms()

    # regulate every 5 sec
    if (time.ticks_ms()) > prev_time_regu + 5000:
        curr_temp = float(temperature())
        t.set_text(str(curr_temp))
        if mode == 'AUTO':
            cmd_temp = set_cmd_temp_auto()
        elif mode == 'DAY':
            cmd_temp = day_temp
        elif mode == 'NIGHT':
            cmd_temp = night_temp
        regu()
        battery_lbl.set_text(
            str((str((str('Bat. ') + str((map_value((power.getBatVoltage()), 3.7, 4.1, 0, 100))))) + str('%'))))
        prev_time_regu = time.ticks_ms()

    # Switch from ON to AUTO mode if mode was ON for more than 5 min
    if (time.ticks_ms()) > prev_time_on + timeout_on and mode == 'ON':
        set_AUTO()

    # Read the touch screen
    if touch.status():
        X = touch.read()[0]
        Y = touch.read()[1]

        # A touch in the middle toggle screen brightness
        if 10 < X < 310 and 80 < Y < 150:
            screen.set_screen_brightness((100 if brightness_flip else 15))
            prev_time_screen = time.ticks_ms()
            brightness_flip = not brightness_flip
            wait_ms(300)

    # Exit edit mode after 30 sec
    if (time.ticks_ms()) > prev_time_exit + 30000 and (edit_day or edit_night):
        hide_edit_button()

    # Exit screen brightness at 100% after timeout
    if (time.ticks_ms()) > prev_time_screen + timeout_screen:
        screen.set_screen_brightness(15)

    wait_ms(25)

