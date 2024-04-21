# --------------------------------------------
# main file
# Author: Rahil Amit Shah
# Roll No: EE20B104
# Guide: Dr. Ramkrishna Pasumarthy
# Date written: 7|12|23 - 5|6|24
# --------------------------------------------

"""
Description --------------------------------
This file is the heart of the project. It does the following
1. Capture image from zed 
2. Saves this image to C:\segmentation\code\YOLOP\inference\images
3. Calls the YOLOP model to process the image
4. Finds the next way point
5. Estimates the 3D coordinates
6. Sends this 3d coordinates to control module
--------------------------------------------- 
"""

# Import libraries------------------------------------
import cv2
import pyzed.sl as sl
import subprocess
import math
import numpy as np
import csv
import socket
from camera_geometry import CameraGeometry
import time
from datetime import datetime
import os
#-----------------------------------------------------


#-----------------------------------------------------
# Helper function to calculate 2d pixel to 3d coordinates
def find_3d_coordinates(x_2d, y_2d):
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


# ----------------------------------------------------
# 1. Capturing the image from the zed 
# Create a ZED camera object
# """
zed = sl.Camera()

# Set configuration parameters
init_params = sl.InitParameters()
init_params.camera_resolution = sl.RESOLUTION.HD1080
init_params.camera_fps = 30
init_params.depth_mode = sl.DEPTH_MODE.ULTRA
init_params.coordinate_units = sl.UNIT.MILLIMETER

# Open the camera
err = zed.open(init_params)
if err != sl.ERROR_CODE.SUCCESS:
    print("Error while opening the camera")
    exit(-1)

# ------------------------------------------------------
# the below variables show the current position of the car
curr_x = 0
curr_y = 0
iteration = 0

# The below list shows the list of the global waypoints
# considering the origin as where the car started to move
global_waypoints = []
# Define the CSV file path
csv_file_path = "global_waypoints.csv"
# ------------------------------------------------------

while True:
    print("\n\n\n-------------------------------------------------------")
    print("-------------------------------------------------------")
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Iteration number ",iteration)
    print("Current image taken at the time: ",current_time)
    print("Current position is: [",curr_x,", ",curr_y,"]",sep="")
    start_time = time.time()
    # capture image
    image = sl.Mat()
    if zed.grab() == sl.ERROR_CODE.SUCCESS:
    # A new image is available if grab() returns SUCCESS
        zed.retrieve_image(image, sl.VIEW.LEFT)

    #------------------------------------------------------
    # 2. Save the image as center.png
    # """
    image_np = image.get_data()
    cv2.imwrite("C:\\segmentation\\code\\YOLOP\\inference\\images\\center.png", image_np)
    # """
    #------------------------------------------------------
        


    #------------------------------------------------------
    # 3. Calls the YOLOP model to process the image

    # Run the command in a new process
    print("------------------Segmentation Starts------------------")
    subprocess.run(["python", "C:\\segmentation\\code\\YOLOP\\tools\\demo.py", "--source", "inference/images"])
    #------------------------------------------------------



    #------------------------------------------------------
    # 4. Finding the next way points from reading the pixel values of the drivable area

    
    image_path_out = r'inference\output\center.png'
    image_out = cv2.imread(image_path_out)

    # Convert BGR to RGB
    image_rgb = cv2.cvtColor(image_out, cv2.COLOR_BGR2RGB)
    image_np = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)

    # Resize the other image to match the size of the ZED camera image
    image_rgb = cv2.resize(image_rgb, (image_np.shape[1], image_np.shape[0]), interpolation=cv2.INTER_LINEAR)


    diff_image = cv2.absdiff(image_np, image_rgb)
    diff_gray = cv2.cvtColor(diff_image, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to retain non-black pixels
    _, thresholded_diff = cv2.threshold(diff_gray, 1, 255, cv2.THRESH_BINARY)

    # Save the resulting image
    # cv2.imwrite("diff_non_black.png", thresholded_diff)


    #------------------------------------------------------



    #------------------------------------------------------
    # Getting the way points
    height, width = thresholded_diff.shape
    left = []
    right = []
    vert = []

    for y in range(int((3*height)/5),height,5):
        cnt = 0
        flag = 0
        for x in range(width):
            if thresholded_diff[y,x] == 255:
                cnt+=1
            else:
                cnt = 0
            if cnt == 5 and flag == 0:
                left.append(x)
                right.append(x)
                flag = 1
                vert.append(y)
            if cnt > 5 and flag == 1:
                right[-1]+=1
    l = np.array(left)
    r = np.array(right)
    midx = (l+r)/2
    midy = np.array(vert)
    # Convert midx and midy to integers
    midx = midx.astype(int)
    midy = midy.astype(int)
    #------------------------------------------------------


    #------------------------------------------------------
    # Marking the way points on the image
    # Create a copy of the image to draw on
    image_with_dots = image_rgb.copy()

    # Draw blue dots at midx and midy coordinates
    dot_color = (0, 0, 255)  # Blue color in BGR format
    dot_radius = 10  # Radius of the dots
    for x, y in zip(midx, midy):
        cv2.circle(image_with_dots, (int(x), int(y)), dot_radius, dot_color, -1)  # Draw filled circle

    # The way points image
    # cv2.imwrite("way_points.png", image_with_dots)
    #------------------------------------------------------

    #------------------------------------------------------
    # Getting the depth value of way points
    way_points = []
    for i in range(len(midx)):
        way_points.append(find_3d_coordinates(int(midx[i]), int(midy[i])))
        global_waypoints.append([way_points[-1][0]+x,way_points[-1][2]+y])
    
    for i in range(min(len(way_points),20)):
        print("[%.2f, %.2f]" % (way_points[i][0]*100, way_points[i][2]*100),end=" ")

    with open(csv_file_path, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        for point in way_points:
            csv_writer.writerow(point)
    #------------------------------------------------------


    #------------------------------------------------------
    # Storing the outputs
    # Concatenate images horizontally
    combined_image = np.concatenate((image_np, image_with_dots), axis=1)
    
    # Create the folder if it doesn't exist
    folder_path = "combined_images"
    os.makedirs(folder_path, exist_ok=True)

    # Inside the loop
    combined_image_path = os.path.join(folder_path, f"combined_image_{iteration}.png")
    cv2.imwrite(combined_image_path, combined_image)
    iteration += 1
    #------------------------------------------------------

    #------------------------------------------------------
    # Wait for 10 s before next iteration
    # curr_time = time.time()
    # elapsed_time = curr_time - start_time
    # while elapsed_time < 10:
    #     time.sleep(10)
    #     elapsed_time += 10
    #------------------------------------------------------
    curr_x += 25
    curr_y += 40

#------------------------------------------------------ 








# -----------------------------------------------------
# Closing the files

# Close the camera
zed.close()
#------------------------------------------------------