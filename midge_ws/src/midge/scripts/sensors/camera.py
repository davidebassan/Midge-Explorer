#!/usr/bin/python

import rospy
from std_msgs.msg import String
from sensor_msgs.msg import CameraInfo, Image


class Camera:
    """
        Handle with camera sensor
    """
    def __init__(self):
        """
            Init the object
        """
        self.camera_image = None
        self.camera_info = None
        self.topic_img = '/camera/rgb/image_raw'
        self.topic_camera_info = '/camera/rgb/camera_info'

    def capture(self, info=False):
        """
            Sets camera_info and camera image (takes a photo)
            @param image boolean
        """
        if info:
            self.camera_info = rospy.wait_for_message(self.topic_camera_info, CameraInfo)
        else:
            self.camera_info = None

        self.camera_image = rospy.wait_for_message(self.topic_img, Image)

    def get_camera_info(self):
        """
            @return camera info
        """
        return self.camera_info

    def get_camera_image(self):
        """
            @return camera image
        """
        return self.camera_image

    """
    def stop(self):
        self.subscriber_img.unregister()
        self.subscriber_camera_info.unregister()
    """