SG_MIN_LATITUDE = 1.34
SG_MAX_LATITUDE = 1.35
SG_MIN_LONGITUDE = 1.7
SG_MAX_LONGITUDE = 1.8


class GeoCoordsMapper:
    def __init__(self, min_long, max_long, min_lat, max_lat, min_x, max_x, min_y, max_y):
        self.min_long, self.max_long = min_long, max_long
        self.min_lat, self.max_lat = min_lat, max_lat
        self.min_x, self.max_x = min_x, max_x
        self.min_y, self.max_y = min_y, max_y

    def convert_to_geo_coords(self, scene_x, scene_y):
        raise NotImplementedError()

    def convert_to_scene_coords(self, geo_x, geo_y):
        raise NotImplementedError()
