from m5stack import *
from m5stack_ui import *
from uiflow import *
import wifiCfg
import nvs
from m5mqtt import M5mqtt
import time
from m5stack import touch
from easyIO import *
import unit
from machine import Pin
from esp import dht_readinto

screen = M5Screen()
screen.clean_screen()
screen.set_screen_bg_color(0xf9f5f5)
relay0 = unit.get(unit.RELAY, unit.PORTA)

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
prev_time_regu = None
prev_time_on = None
X = None
prev_time_screen = None
Y = None
timeout_screen = None

wifiCfg.doConnect('WiFi-2.4-CC88', (nvs.read_str('wifi_pwd')))
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
touch_nigth = M5Btn(text='NUIT', x=149, y=180, w=70, h=30, bg_c=0xf1e99d, text_c=0x000000, font=FONT_MONT_14,
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

DHT_PIN = 33
buf = bytearray(5)


def humidity():
    dht_readinto(DHT_PIN, buf)
    return (buf[0] << 8 | buf[1]) * 0.1


def temperature():
    dht_readinto(DHT_PIN, buf)
    t = ((buf[2] & 0x7F) << 8 | buf[3]) * 0.1
    if buf[2] & 0x80:
        t = -t
    # print ('temp: ', t)
    return t


# Describe this function...
def init():
    global on, cmd_temp, week_schedule, d, temp, mode, edit_night, day_temp, edit_day, night_temp, brightness_flip, curr_day_schedule, curr_hrmin, curr_temp, prev_time_exit, curr_period, timeout_on, prev_weekday, prev_time_clock, prev_time_regu, prev_time_on, X, prev_time_screen, Y, timeout_screen
    week_schedule = [[{'start': '0630', 'end': '2330'}], [{'start': '0631', 'end': '2330'}],
                     [{'start': '0632', 'end': '2200'}], [{'start': '0633', 'end': '2330'}],
                     [{'start': '0635', 'end': '0853'}, {'start': '0855', 'end': '2330'}],
                     [{'start': '0636', 'end': '2330'}], [{'start': '0637', 'end': '2330'}]]
    brightness_flip = False
    day_temp = 20
    night_temp = 14
    edit_day = False
    edit_night = False
    curr_temp = 0
    mode = 'AUTO'
    prev_time_clock = time.ticks_ms()
    prev_time_regu = time.ticks_ms()
    prev_time_exit = time.ticks_ms()
    prev_time_screen = 0
    prev_time_on = 0
    prev_weekday = -1
    timeout_on = 0
    curr_hrmin = 0
    timeout_screen = 120000
    curr_temp = temperature()
    t.set_text(str(str(cmd_temp)))
    mode_label.set_hidden(True)
    show_plus_minus(False)
    set_AUTO()


# Describe this function...
def set_cmd_temp_auto():
    global on, cmd_temp, week_schedule, d, temp, mode, edit_night, day_temp, edit_day, night_temp, brightness_flip, curr_day_schedule, curr_hrmin, curr_temp, prev_time_exit, curr_period, timeout_on, prev_weekday, prev_time_clock, prev_time_regu, prev_time_on, X, prev_time_screen, Y, timeout_screen
    d = (rtc.datetime()[3]) + 1
    curr_day_schedule = week_schedule[int(d - 1)]
    curr_hrmin = (rtc.datetime()[5]) + (rtc.datetime()[4]) * 100
    for curr_period in curr_day_schedule:
        if curr_hrmin >= int((curr_period['start'])) and curr_hrmin < int((curr_period['end'])):
            temp = day_temp
            start_lbl.set_text(str(curr_period['start']))
            end_lbl.set_text(str(curr_period['end']))
            state.set_on()
            auto_txt.set_pos(226, 34)
            break
    if temp != day_temp:
        temp = night_temp
        start_lbl.set_text(' ')
        end_lbl.set_text(' ')
        auto_txt.set_pos(272, 34)
        state.set_off()
    return temp


# Describe this function...
def DAY():
    global on, cmd_temp, week_schedule, d, temp, mode, edit_night, day_temp, edit_day, night_temp, brightness_flip, curr_day_schedule, curr_hrmin, curr_temp, prev_time_exit, curr_period, timeout_on, prev_weekday, prev_time_clock, prev_time_regu, prev_time_on, X, prev_time_screen, Y, timeout_screen
    mode = 'DAY'
    mode_label.set_hidden(True)
    state.set_hidden(False)
    touch_onoff.set_btn_text('AUTO')
    cmd_temp = day_temp
    timeout_on = 0
    auto_txt.set_hidden(True)


# Describe this function...
def NIGHT():
    global on, cmd_temp, week_schedule, d, temp, mode, edit_night, day_temp, edit_day, night_temp, brightness_flip, curr_day_schedule, curr_hrmin, curr_temp, prev_time_exit, curr_period, timeout_on, prev_weekday, prev_time_clock, prev_time_regu, prev_time_on, X, prev_time_screen, Y, timeout_screen
    mode = 'NIGHT'
    mode_label.set_hidden(True)
    state.set_hidden(False)
    touch_onoff.set_btn_text('AUTO')
    cmd_temp = night_temp
    timeout_on = 0
    auto_txt.set_hidden(True)


# Describe this function...
def set_ON():
    global on, cmd_temp, week_schedule, d, temp, mode, edit_night, day_temp, edit_day, night_temp, brightness_flip, curr_day_schedule, curr_hrmin, curr_temp, prev_time_exit, curr_period, timeout_on, prev_weekday, prev_time_clock, prev_time_regu, prev_time_on, X, prev_time_screen, Y, timeout_screen
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


# Describe this function...
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


# Describe this function...
def set_AUTO():
    global on, cmd_temp, week_schedule, d, temp, mode, edit_night, day_temp, edit_day, night_temp, brightness_flip, curr_day_schedule, curr_hrmin, curr_temp, prev_time_exit, curr_period, timeout_on, prev_weekday, prev_time_clock, prev_time_regu, prev_time_on, X, prev_time_screen, Y, timeout_screen
    mode = 'AUTO'
    mode_label.set_hidden(True)
    state.set_hidden(False)
    touch_onoff.set_btn_text('OFF')
    cmd_temp = set_cmd_temp_auto()
    timeout_on = 0
    auto_txt.set_hidden(False)


# Describe this function...
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


# Describe this function...
def hide_edit_button():
    global on, cmd_temp, week_schedule, d, temp, mode, edit_night, day_temp, edit_day, night_temp, brightness_flip, curr_day_schedule, curr_hrmin, curr_temp, prev_time_exit, curr_period, timeout_on, prev_weekday, prev_time_clock, prev_time_regu, prev_time_on, X, prev_time_screen, Y, timeout_screen
    edit_night = False
    edit_day = False
    show_plus_minus(False)


# Describe this function...
def regu():
    global on, cmd_temp, week_schedule, d, temp, mode, edit_night, day_temp, edit_day, night_temp, brightness_flip, curr_day_schedule, curr_hrmin, curr_temp, prev_time_exit, curr_period, timeout_on, prev_weekday, prev_time_clock, prev_time_regu, prev_time_on, X, prev_time_screen, Y, timeout_screen
    if curr_temp > float(cmd_temp) + 0.5:
        relay0.off()
        relay_btn.set_hidden(True)
    else:
        if curr_temp < float(cmd_temp) - 0.5:
            relay0.on()
            relay_btn.set_hidden(False)
        else:
            pass


def state_off():
    global cmd_temp, week_schedule, d, temp, mode, edit_night, day_temp, edit_day, night_temp, brightness_flip, curr_day_schedule, on, curr_hrmin, curr_temp, prev_time_exit, timeout_on, prev_weekday, prev_time_clock, curr_period, prev_time_regu, prev_time_on, X, prev_time_screen, Y, timeout_screen
    NIGHT()
    auto_txt.set_hidden(True)
    pass


state.off(state_off)


def state_on():
    global cmd_temp, week_schedule, d, temp, mode, edit_night, day_temp, edit_day, night_temp, brightness_flip, curr_day_schedule, on, curr_hrmin, curr_temp, prev_time_exit, timeout_on, prev_weekday, prev_time_clock, curr_period, prev_time_regu, prev_time_on, X, prev_time_screen, Y, timeout_screen
    DAY()
    auto_txt.set_hidden(True)
    pass


state.on(state_on)


def touch_day_pressed():
    global cmd_temp, week_schedule, d, temp, mode, edit_night, day_temp, edit_day, night_temp, brightness_flip, curr_day_schedule, on, curr_hrmin, curr_temp, prev_time_exit, timeout_on, prev_weekday, prev_time_clock, curr_period, prev_time_regu, prev_time_on, X, prev_time_screen, Y, timeout_screen
    cmd_temp = day_temp
    edit_day = True
    show_plus_minus(True)
    prev_time_exit = time.ticks_ms()
    pass


touch_day.pressed(touch_day_pressed)


def touch_nigth_pressed():
    global cmd_temp, week_schedule, d, temp, mode, edit_night, day_temp, edit_day, night_temp, brightness_flip, curr_day_schedule, on, curr_hrmin, curr_temp, prev_time_exit, timeout_on, prev_weekday, prev_time_clock, curr_period, prev_time_regu, prev_time_on, X, prev_time_screen, Y, timeout_screen
    cmd_temp = night_temp
    edit_night = True
    show_plus_minus(True)
    prev_time_exit = time.ticks_ms()
    pass


touch_nigth.pressed(touch_nigth_pressed)


def touch_onoff_pressed():
    global cmd_temp, week_schedule, d, temp, mode, edit_night, day_temp, edit_day, night_temp, brightness_flip, curr_day_schedule, on, curr_hrmin, curr_temp, prev_time_exit, timeout_on, prev_weekday, prev_time_clock, curr_period, prev_time_regu, prev_time_on, X, prev_time_screen, Y, timeout_screen
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
    pass


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
    pass


btnC.wasPressed(buttonC_wasPressed)

init()
m5mqtt = M5mqtt('Thermostat', '192.168.0.22', 1883, 'IoT', (nvs.read_str('mqtt_pwd')), 300)

rtc.settime('ntp', host='de.pool.ntp.org', tzone=2)
while True:
    if (rtc.datetime()[3]) != prev_weekday:
        rtc.settime('ntp', host='de.pool.ntp.org', tzone=2)
        mode = 'AUTO'
        prev_weekday = rtc.datetime()[3]
    if (time.ticks_ms()) > prev_time_clock + 1000:
        clock_lbl.set_text(str(rtc.printRTCtime()))
        prev_time_clock = time.ticks_ms()
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
            str((str(((str('Bat. ') + str((map_value((power.getBatVoltage()), 3.7, 4.1, 0, 100)))))) + str('%'))))
        prev_time_regu = time.ticks_ms()
    if (time.ticks_ms()) > prev_time_on + timeout_on and mode == 'ON':
        set_AUTO()
    if touch.status():
        X = touch.read()[0]
        Y = touch.read()[1]
        if X > 10 and X < 310 and Y > 80 and Y < 150:
            screen.set_screen_brightness((100 if brightness_flip else 15))
            prev_time_screen = time.ticks_ms()
            brightness_flip = not brightness_flip
            wait_ms(300)
    if (time.ticks_ms()) > prev_time_exit + 30000 and (edit_day or edit_night):
        hide_edit_button()
    if (time.ticks_ms()) > prev_time_screen + timeout_screen:
        screen.set_screen_brightness(15)
    wait_ms(2)
