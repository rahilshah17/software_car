########################################################################
# Rahil Shah
# 25|1|2024
########################################################################

import pyzed.sl as sl
import cv2
import numpy as np
import math
from camera_geometry import CameraGeometry

#-----------------------------------------------------
# Helper function to calculate 2d pixel to 3d coordinates
def find_3d_coordinates(x_2d, y_2d,zed):
    calibration_params = zed.get_camera_information().camera_configuration.calibration_parameters
    
    h_fov = calibration_params.left_cam.h_fov
    image_size = zed.get_camera_information().camera_configuration.resolution
    image_width = image_size.width
    image_height = image_size.height
    # image_width = 1080
    # image_height = 1920
    # h_fov = 120
    cam_geom = CameraGeometry(height=0.08, yaw_deg=0, pitch_deg=0, roll_deg=0, image_width=image_width, image_height=image_height, field_of_view_deg=h_fov)


    # Define pixel coordinates (u, v)
    u_pixel = x_2d
    v_pixel = y_2d

    # Convert pixel coordinates to 3D coordinates (X, Y, Z) in the road frame
    X, Y, Z = cam_geom.uv_to_roadXYZ_roadframe(u_pixel, v_pixel)
    return X,Y,Z
#-----------------------------------------------------


def main():
    # Create a ZED camera object
    zed = sl.Camera()

    # Set configuration parameters
    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.HD1080
    init_params.camera_fps = 30
    init_params.coordinate_units = sl.UNIT.MILLIMETER # Use millimeter units (for depth measurements)
    init_params.depth_mode = sl.DEPTH_MODE.ULTRA # Use ULTRA depth mode
    # Open the camera
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        exit(-1)

    image = sl.Mat()
    if zed.grab() == sl.ERROR_CODE.SUCCESS:
        # A new image is available if grab() returns SUCCESS
        zed.retrieve_image(image, sl.VIEW.LEFT) # Retrieve the left image
        
        # save image
        # image.save("captured_image.png")
        # Convert the ZED image to a format usable by OpenCV
        
        image_data = image.get_data()
        opencv_image = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)

        # Get the image dimensions
        height, width, _ = opencv_image.shape
        x = 480
        y = 940
        # Draw a filled circle
        opencv_image = cv2.circle(opencv_image, (x, y), radius=10, color=(0, 165, 255), thickness=-1)

        # Find 3D coordinates for the marked point
        point_3d = find_3d_coordinates(x, y, zed)
        if point_3d is not None:
            # Write 3D coordinates on the image
            text = f"({point_3d[0]*100:.2f}, {point_3d[2]*100:.2f})"
            cv2.putText(opencv_image, text, (x + 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 4, cv2.LINE_AA)

        # # Save the modified image
        cv2.imwrite("marked_image_with_coordinates.png", opencv_image)
    # Close the camera
    zed.close()



if __name__ == "__main__":
    main()