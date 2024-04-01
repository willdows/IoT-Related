# MicroPython version of gpiozero library
# version 1.3
# by Lubos Kuzma, School of SADT, SAIT
#
# This is a replica (not a port) of gpiozero library. 
# It only replicates SOME functionality of full gpiozero library
# Currently implemented classes:
#
# LED(pin, *, active_high=True, initital_value=False)
# PWMLED(pin, *, initital_value=0.0, frequency=100)
# Button(pin, *, pull_up=True, bounce_time=None)


from machine import Pin, PWM, Timer

class LED():
    def __init__(self, pin, *, active_high=True, initital_value=False):
        self.pin = pin
        self.led = Pin(pin, Pin.OUT)
        self.active_high = active_high
        self.initial_value = initital_value
        if initital_value == False:
            self.instance_value = 0
            self.led.off()
        else:
            self.instance_value = 1
            self.led.on()
           
    def on(self):
        if self.active_high == True:
            self.led.value(1)
            self.instance_value = 1
        else:
            self.led.value(0)
            self.instance_value = 0

    def off(self):
        if self.active_high == True:
            self.led.value(0)
            self.instance_value = 0
        else:
            self.led.value(1)
            self.instance_value = 1

    @property    
    def value(self):
        return self.instance_value
    
    @value.setter
    def value(self, newValue):
        self.led.value(newValue)
        self.instance_value = newValue

class PWMLED():
    def __init__(self, pin, *, initital_value=0.0, frequency=100):
       
        self.pin = pin
        self._led = Pin(pin, Pin.OUT)
        self.freq = frequency
        self.pwmled = PWM(self._led)
        self.instance_value = initital_value
        self.duty_u16 = int(self.instance_value * 65535)
        self.pwmled.freq(self.freq)
        self.pwmled.duty_u16(self.duty_u16)
   
    def on(self):
        
        self.pwmled.duty_u16(65535)
        self.instance_value = 1
        
    def off(self):
        self.pwmled.duty_u16(0)
        self.instance_value = 0.0

    @property    
    def value(self):
        return self.instance_value
    
    @value.setter
    def value(self, newValue):
        self.pwmled.duty_u16(int(newValue * 65535))
        self.instance_value = newValue

class Button():
    btnList = {}
    def __init__(self, pin, *, pull_up=True, bounce_time=None):
        global btnList
        self.pin = pin
        if pull_up == True:
            self.pull_up = Pin.PULL_UP
        elif pull_up == False:
            self.pull_up = Pin.PULL_DOWN
        else:
            self.pull_up = None
        
        self.btn = Pin(pin, Pin.IN, pull_up)
        
        self.state = self.btn.value()
        self._when_pressed  = None
        self._when_released = None

        self._bounce_time = bounce_time
        self._bounces = 0
        self._fire_rising_edge = 0
        self._bounce_timer = Timer(-1)
        
        Button.btnList[pin] = self
    
    @property
    def value(self):
        return self.btn.value()

    @property
    def when_pressed(self):
        return self._when_pressed

    @when_pressed.setter
    def when_pressed(self, def_handler):
        if self._when_pressed == None:
            self._when_pressed = def_handler
        Button.set_trigger_handler(self.pin)

    @property
    def when_released(self):
        return self._when_released

    @when_released.setter
    def when_released(self, def_handler):
        if self._when_released == None:
            self._when_released = def_handler
        Button.set_trigger_handler(self.pin)
    


    def trigger_fire(self, edge):

        if self._bounce_time is not None:
            self._bounce_timer.init(mode=Timer.ONE_SHOT, period=self._bounce_time, callback=lambda a:Button.debounce_timer_end(self))
        
        if edge == 0 and self.pull_up == Pin.PULL_UP \
            and self._when_pressed != None:
                self._when_pressed()

        elif edge == 0 and self.pull_up == Pin.PULL_DOWN \
            and self._when_released != None:
                self._when_released()

        elif edge == 1 and self.pull_up == Pin.PULL_UP \
            and self._when_released != None:
                self._when_released()

        elif edge == 1 and self.pull_up == Pin.PULL_DOWN \
            and self._when_pressed != None:
                self._when_pressed()
    
    @staticmethod
    def set_trigger_handler(pin_num):
        Button.btnList[pin_num].btn.irq(handler=Button.trigger_handler, trigger=Pin.IRQ_FALLING|Pin.IRQ_RISING)
    
    @staticmethod
    def debounce_timer_end(whole_object):
        whole_object._bounces = 0

    @staticmethod
    def trigger_handler(btn_object):
                
        id = Button.PinId(btn_object)
        whole_object = Button.btnList[id]
        
        fire_edge = btn_object.value()

        # debounce logic
        if whole_object._bounce_time == None:
            # if Bounce = None
            Button.trigger_fire(whole_object, fire_edge)

        elif whole_object._bounces == 0:
            # first round of debounce
            whole_object._bounces += 1
            Button.trigger_fire(whole_object, fire_edge)
            
        elif whole_object._bounces != 0:
            # consequent rounds of debounce
            whole_object._bounces += 1

    @staticmethod
    def PinId(pin):
        # there is no way to get pin# from Pin object, so this is a very aquard way of doing it
        # uncomment for troubleshooting. below:
        # print(f"Pin String: {str(pin)}")
        new_pin =  int(str(pin) [8:10].rstrip(","))
        # uncomment for troubleshooting. below:
        #print(f"New Pin: {new_pin}")
        return new_pin