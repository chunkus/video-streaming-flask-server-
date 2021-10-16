#!/usr/bin/env python
from importlib import import_module
import os
from flask import Flask, render_template, Response
import sys
from PIL import Image
import io
from rpi_ws281x import PixelStrip, Color
import time
import sys
import signal

# LED strip configuration:
LED_COUNT      = 16      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels.
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz
LED_DMA        = 10      # DMA channel to use for generating signal
LED_BRIGHTNESS = 255
LED_INVERT     = False  
LED_CHANNEL    = 0
LED_ON = False

def handler(signal, frame):
    global strip
    print('CTRL-C pressed!')
    colorWipe(strip, Color(0,0,0))

    sys.exit(0)
    
signal.signal(signal.SIGINT, handler)

strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

# import camera driver
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera_pi import Camera



app = Flask(__name__)


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def gen(camera):
    global led_on
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        brightness = calculate_brightness(frame)

        if not LED_ON and brightness < 0.4:
            LED_ON = True
            enable_led()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def calculate_brightness(image):
    imageStream = io.BytesIO(image)
    imageFile = Image.open(imageStream)
    greyscale_image = imageFile.convert('L')
    histogram = greyscale_image.histogram()
    pixels = sum(histogram)
    brightness = scale = len(histogram)

    for index in range(0, scale):
        ratio = histogram[index] / pixels
        brightness += ratio * (-scale + index)

    return 1 if brightness == 255 else brightness / scale

def enable_led():
    global strip
    colorWipe(strip, Color(255, 255, 255))

def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)





if __name__ == '__main__':
    app.run(host='0.0.0.0',threaded=True)
