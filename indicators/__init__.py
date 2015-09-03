"""Package __init__, exposes function to get required device.

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

class NoDeviceError(Exception):
    
    """For when the device can't be found."""
    
    def __init__(self):
        
        Exception.__init__(self, 'Device can not be found - check it is plugged in.')

def get_device(device):
    
    """Find the relevant device (as given by device) and return
    the class.
    
    Arguments:
        device (string): Case-sensitive string for the device - Currently 'dummy' or 'delcom'.
        
    Return:
        Device class as required
    """
    
    if device == 'delcom':
        import indicators.delcom
        return indicators.delcom.Device