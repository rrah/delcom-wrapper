#!/usr/bin/python

"""Module for delcom status lights.
Author: Robert Walker <rrah99@gmail.com>
Copyright (C) 2015 Robert Walker
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; version 2.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

# Builtin imports
import threading
import sys
import logging
from time import sleep


# Does communication to usb. Surprisingly
import usb

PIN_GREEN   = 0b00000001
"""Byte value for green pin"""
PIN_YELLOW  = 0b00000010
"""Byte value for yellow pin"""
PIN_RED     = 0b00000100
"""Byte value for red pin"""

class Device(object):
    '''
    Class for talking to Delcom Products generation 2 USB device 
    Modified from http://permalink.gmane.org/gmane.comp.python.pyusb.user/91
    '''

    # Device Constants
    VENDOR_ID       = 0x0FC5    #: Delcom Product ID
    PRODUCT_ID      = 0xB080    #: Delcom Product ID
    INTERFACE_ID    = 0         #: The interface we use
    allowed_colours = {'green': [0x01, 0xFF], 
                                'yellow': [0x04, 0xFF], 
                                'red': [0x02, 0xFF],
                                'orange': [0x06, 0xFF], 
                                'off': [0x00, 0xFF]}
    """Dict matching colour to byte-values."""
    _colour_pins = { 'green'     : 1,
                    'yellow'    : 4,
                    'red'       : 2
                    }

    def __init__(self):
        '''
        Constructor'''
        
        # Set some default attributes
        self._flashing_pin = None
        self._pressed = False
        self._current_colour = 'off'
        self._been_pressed = False
        
        self.device = usb.core.find(idProduct = self.PRODUCT_ID)
        try:
            self.device.detach_kernel_driver(0)
        except:
            pass
        try:
            self.device.set_configuration()
        except AttributeError:
            raise USBError('Device not connected')
        
        self._force_off()
        
        
        # Turn on event counter and reset
        self._write_data(self._make_packet(101, 38, 0x01))
        self._read_data(0x0008)
        
        self.set_brightness(50)
    
    def _force_off(self):
        
        """
        Make sure flashing/LEDs are definitely turned off"""
        
        self._write_data("\x65\x0C\x00\xFF\x00\x00\x00\x00")
        self._write_data(self._make_packet(101, 20, 1))
        self._write_data(self._make_packet(101, 20, 2))
        self._write_data(self._make_packet(101, 20, 4))        

    def flashing_start(self, flash_speed = 1, colours = 'red'):
        
        """Start the LED's flashing.
        
        Keyword arguements:
            flash_speed (int): Seconds to stay in each state.
                Floored to 0.01 and ceilinged to 2.55
        """
        
        # Get the flash speed in the right range
        if flash_speed > 2.55:
            flash_speed = 2.55
        elif flash_speed < 0.01:
            flash_speed = 0.01
        
        # and change from seconds to value that is given
        # to the device
        flash_speed = int(flash_speed * 100)
        
        # Turn on the relevant LEDs
        self.set_light(colours)
        
        # Set the flash speed and start flashing
        self._write_data(self._make_packet(0x65, 20 + 
                                        self._colour_pins[colours], 
                                        flash_speed, flash_speed))
        self._write_data(self._make_packet(0x65, 20, 0, 
                                            self._colour_pins[colours]))
        
        # Keep track of what pin is flashing
        self._flashing_pin = self._colour_pins[colours]
        
    def flashing_stop(self):
        
        """Check if a pin is actually flashing, and if so
        turn it off and turn off flashing
        """
        
        if self._flashing_pin is not None:
            self.set_light('off')
            self._write_data(self._make_packet(101, 20, 
                                                self._flashing_pin, 0))

    def _make_packet(self, maj_cmd, min_cmd, lsb = 0x00, msb = 0x00):
        
        return [maj_cmd, min_cmd, lsb, msb, 0x00, 0x00, 0x00, 0x00]

    def set_brightness(self, brightness):
        
        """Change brightness of LED's.
        
        Arguements:
            brightness (int): Brightness value between 0 and 100.
        """
        
        self._set_pwr(brightness)

    def _set_pwr(self, pwr):
        
        pwr = int(pwr)
        if pwr > 100:
            pwr = 100
        elif pwr < 0:
            pwr = 0
        self._write_data(self._make_packet(101, 34, 0, pwr))
        self._write_data(self._make_packet(101, 34, 1, pwr))
        self._write_data(self._make_packet(101, 34, 2, pwr))
        
    def _write_data(self, data):

        self.device.ctrl_transfer(0x21, 0x09, 0x0365, 0x0000, data, 100)

    def read_switch(self):
    
        """See if the button has been pressed.
        
        Return: 
            Number of presses
            True if pressed False otherwise.
        """
       
        presses = 0
        counter_data = []
        pressed_data = []
        
        # Sometimes doesn't get a return, so repeat until data is got
        while len(counter_data) != 8:
            counter_data = self._read_data(0x0008)
        while len(pressed_data) != 8:
            pressed_data = self._read_data(0x0064)
        
        counter = int(counter_data[0])
        self._pressed = not bool(int(pressed_data[0]) % 2)
        
        # Count up the number of presses since last read
        while counter > 0:
            presses += 1
            counter -= 1 
        if presses > 0:
            self._been_pressed = True
        return presses, self._pressed
        
    def has_been_pressed(self):
        
        """Check to see if the button has been pressed.
        
        Return:
            True if button has been pressed, else False.
        """
        
        self.read_switch()
        been_pressed = self._been_pressed
        
        # Reset attribute
        self._been_pressed = False
        return been_pressed

    def get_pressed(self):
        
        return self._pressed

    def _read_data(self, cmd):

        data = self.device.ctrl_transfer(0xA1, 0x01, cmd, 0x0000, 8, 100)
        return data
                                    
    def read(self):
        
        """Straight-up read the device buffer.
        
        Return:
            Byte-array of data.
        """
        
        return self._read_data(0x0008)


    def _get_current_colour(self):
        
        return self._current_colour
    
    def _set_light(self, colour):
        
        """Change the colour of the light in the indicator.
        
        Arguements:
            colour (string): Colour to set the LED's to.
            
        Returns:
            None
            
        Raises:
            Exception: Colour isn't allowed by device.
        """
    
        # Check it's a colour we can deal with
        if colour not in self.allowed_colours:
            raise Exception('{} - Not allowed colour'.format(colour))
        if self._get_current_colour() == colour:
            # No change
            return
            
        # Make the call to change the colour
        self._write_data(self._make_packet(0x65, 0x0C, 
                                           self.allowed_colours['off'][0], 
                                           self.allowed_colours['off'][1]))
        self._write_data(self._make_packet(0x65, 0x0C, 
                                           self.allowed_colours[colour][0], 
                                           self.allowed_colours[colour][1]))        
        self._current_colour = colour
        
    def set_light(self, colour):
        
        """Check if flashing and stop flashing, then set colour.
        
        Arguements:
            colour (string): Colour to set the LED's to.
            
        Returns:
            Does not return
        """
        
        if hasattr(self, '_flash_thread'):
            self.flashing_stop()
        self._set_light(colour)

        
    def set_light_red(self):
        
        """Set the LED's to red."""
        
        return self.set_light('red')
        
    def set_light_yellow(self):
        
        """Set the LED's to yellow."""
        
        return self.set_light('yellow')
        
    def set_light_blue(self):
        
        """Set the LED's to blue."""
        
        return self.set_light('blue')
        
    def set_light_green(self):
        
        """Set the LED's to green."""
        
        return self.set_light('green')

    def set_light_off(self):
        
        """Turn off the LED's."""

        return self.set_light('off')
        
    def __del__(self):
        
        """Stop any flashing and set the light to off at destruction."""
        
        self.flashing_stop()
        self.set_light_off()


class DeviceDescriptor(object):
    '''
    Class for defining the USB device
    '''

    def __init__(self, vendor_id, product_id, interface_id):
        '''
        Constructor
        '''
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.interface_id = interface_id

    def getDevice(self):
        '''
        Return the device corresponding to the device descriptor if it is
        available on the USB bus.  Otherwise return None.  Note that the
        returned device has yet to be claimed or opened.
        '''
        # Find all the USB busses
        busses = usb.busses()
        for bus in busses:
            for device in bus.devices:
                if device.idVendor == self.vendor_id and \
                   device.idProduct == self.product_id:
                    return device
        return None
