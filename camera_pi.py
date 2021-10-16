import io
import time
import picamera
from base_camera import BaseCamera


class Camera(BaseCamera):
    @staticmethod
    def frames():
        with picamera.PiCamera() as camera:
            # let camera warm up
            #camera.resolution = (352,240)
            camera.resolution = (480,360)
            #camera.resolution = (858,480)
            #camera.resolution = (1280,720)
            #camera.resolution = (1920,1080)

            time.sleep(5)

            stream = io.BytesIO()
            for _ in camera.capture_continuous(stream, 'jpeg',
                                                 use_video_port=True):
                # return current frame
                stream.seek(0)
                yield stream.read()

                # reset stream for next frame
                stream.seek(0)
                stream.truncate()
