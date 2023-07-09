# pseudocode, don't know how to place this (xd)

# wall_color = N

# blue_wall = (0,0)
# red_wall = (0,0)
# green_wall = (0,0)

# if wall_color == blue color filter
    # if the camera seeing it is the frontal one
        # blue_wall = next_tile
    # elif the camera seeing it is the left one
        # blue_wall = left_tile
    # elif the camera seeing it is the right one
        # blue_wall = right_tile

# if wall_color == green color filter
    # if the camera seeing it is the frontal one
        # green_wall = next_tile
    # elif the camera seeing it is the left one
        # green_wall = left_tile
    # elif the camera seeing it is the right one
        # green_wall = right_tile

# if wall_color == red color filter
    # if the camera seeing it is the frontal one
        # red_wall = next_tile
    # elif the camera seeing it is the left one
        # red_wall = left_tile
    # elif the camera seeing it is the right one
        # red_wall = right_tile

# receive_tile_color(self)
    # if tile_color_received == blue_wall
        # stop random movement, move to the blue wall coordinates
    # elif tile_color_received == red_wall
        # stop random movement, move to the red wall coordinates
    # if tile_color_received == green_wall
        # stop random movement, move to the green wall coordinates