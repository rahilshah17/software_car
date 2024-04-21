plane = sl.Plane() # Structure that stores the estimated plane
coord = sl.uint2() # Fill it with the coordinates taken from the full size image
while zed.grab() == sl.ERROR_CODE.SUCCESS:
  tracking_state = zed.get_position(pose) # Get the tracking state of the camera
  if tracking_state == sl.TRACKING_STATE.OK:  
    # Detect the plane passing by the depth value of pixel coord
    find_plane_status = zed.find_plane_at_hit(coord, plane)