# floor_mapper.py, line 20

class FloorMapper:
    def __init__(self, pixel_grid: CompoundExpandablePixelGrid, tile_resolution, tile_size, camera_distance_from_center) -> None:
        self.blue_color_filter = ColorFilter((240, 73, 17), (240, 81, 87))
        self.red_color_filter = ColorFilter((0, 72, 20), (0, 78, 94))
        self.green_color_filter = ColorFilter((120, 82, 18), (120, 88, 92))


# pseudocode, don't know how to place this (xd)

# tile_color_sent = N
# if tile_color == blue color filter:
    # tile_color_sent = B
# if tile_color == red color filter:
    # tile_color_sent = R
# if tile_color == green color filter:
    # tile_color_sent = G


# communicator.py, line 8

class Comunicator(Sensor):

    def send_tile_color(self, tile_color_sent):
        if self.do_get_world_info:
            message = struct.pack('c', tile_color_sent)
            self.emmiter.send(message)

    def receive_tile_color(self):
        if self.do_get_world_info:
            self.request_game_data()
            if self.receiver.getQueueLength() > 0:
                received_data = self.receiver.getBytes()
                tup = struct.unpack('c', received_data)
                if tup[0].decode("utf-8") in ('R', 'G', 'B') :
                    tile_color_received = tup [0]


# don't know where to put this

if tile_color_sent != N:
    send_tile_color(self, tile_color_sent)
