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
image = sl.Mat()
    if zed.grab() == sl.ERROR_CODE.SUCCESS:
    # A new image is available if grab() returns SUCCESS
        zed.retrieve_image(image, sl.VIEW.LEFT)

    #------------------------------------------------------
    # 2. Save the image as center.png
    # """
    image_np = image.get_data()
    cv2.imwrite("image.png", image_np)
