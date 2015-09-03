"""Indicator intended to be subclassed.

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

class Indicator(object):
    
    """Indicator class displaying the methods that are expected by
    the pyliteco service. Subclass this class and overload all the
    methods with the required code.
    
    Attributes:
        None
    
    Methods:
        flashing_start: Start the indicator flashing.
        flashing_stop: Stop the indicator flashing.
        read_switch: Check if something's been pressed.
        set_light: Turn the indicator on to a static colour. 
    """
    
    def flashing_start(self, flash_speed = None, colours = None):
        
        """Whatever code to make the indicator flash one or more colours.
        
        Arguments:
            flash_speed (int): Seconds to stay in each state.
            colours (list): Colours to flash between
                
        Returns:
            None.
        """
        
        pass
    
    def flashing_stop(self):
        
        """Whatever code to make the indicator stop flashing.
        
        Arguments:
            None.
        
        Return:
            None.
        """
        
        pass
    
    def read_switch(self):
        
        """Return whether the switch/button/whatever has been pressed since
        last time this method was called.
        
        Arguments:
            None.
            
        Return:
            True or False.
        """
        
        return False
    
    def set_light(self, colour):
        
        """Whatever code to make the indicator turn on to a certain colour.
        'off' should be included as a valid colour, along with 'red', 'green'
        and 'yellow'.
        
        Arguments:
            colour (string): The colour to light up.
        
        Return:
            None.
        """
        
        pass