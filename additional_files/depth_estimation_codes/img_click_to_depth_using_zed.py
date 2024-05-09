import pyzed.sl as sl
import cv2
import numpy as np
import csv
# click a pixel on the image and get the 3d coordinates of that point using zed point cloud method

def find_3d_coordinates(x_2d, y_2d, zed):
    depth = sl.Mat()
    point_cloud = sl.Mat()

    zed.retrieve_measure(depth, sl.MEASURE.DEPTH)
    zed.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA)
    err, point_cloud_value = point_cloud.get_value(x_2d, y_2d)
    return point_cloud_value
def mouse_callback(event, x, y, flags, param):
    global zed
    if event == cv2.EVENT_LBUTTONDOWN:
        # Find 3D coordinates for the clicked point
        point_3d = find_3d_coordinates(x, y, zed)
        if point_3d is not None:
            # Print the first three values of the 3D coordinates
            print("Clicked pixel coordinates:", x, y)
            
            print(f"{point_3d[0]/10:.1f}   {point_3d[1]/10:.1f}   {point_3d[2]/10:.1f}\n")  # Extract first three values
            actual = 64.5
            # Save the pixel coordinates and the first three values of 3D coordinates to a CSV file
            with open('pixel_and_3d_coordinates.csv', mode='a') as file:
                file.write(f"{x},{y},{point_3d[2]/10:.1f},{actual}\n")

def main():
    global zed
    # Create a ZED camera object
    zed = sl.Camera()

    # Set configuration parameters
    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.HD1080
    init_params.camera_fps = 30
    init_params.coordinate_units = sl.UNIT.MILLIMETER
    init_params.depth_mode = sl.DEPTH_MODE.ULTRA

    # Open the camera
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        exit(-1)

    cv2.namedWindow("ZED Image", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("ZED Image", mouse_callback)

    while True:
        image = sl.Mat()
        if zed.grab() == sl.ERROR_CODE.SUCCESS:
            zed.retrieve_image(image, sl.VIEW.LEFT)
            image_data = image.get_data()
            opencv_image = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)

            # Display the image
            cv2.imshow("ZED Image", image_data)

        # Check for ESC key press to exit the loop
        if cv2.waitKey(1) & 0xFF == 27:
            break

    # Close the camera
    zed.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
