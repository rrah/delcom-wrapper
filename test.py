import indicators
import logging
from time import sleep

device = indicators.get_device('delcom')()

while True:
        
        for colour in device.allowed_colours:
            logging.info('steady {}'.format(colour))
            device.set_light(colour)
            sleep(1)
        
        logging.info('flash fast red for 5 seconds')
        device.set_light_red()
        device.flashing_start(0.2, 'red')
        sleep(5)
        device.flashing_stop()
        
        logging.info('flash slow green for 5 seconds')
        device.set_light_red()
        device.flashing_start(1, 'green')
        sleep(5)
        device.flashing_stop()
