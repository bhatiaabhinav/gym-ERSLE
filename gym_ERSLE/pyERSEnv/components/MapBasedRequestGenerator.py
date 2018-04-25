import numpy as np
import imageio
import gymGame
from typing import List  # noqa: F401
import gym_ERSLE.pyERSEnv


class RPHMapUtils:
    def scale_to_max_requests_per_hour(rph_map, new_max_rph):
        return new_max_rph * rph_map / np.max(rph_map)

    def scale_to_total_requests_per_hour(rph_map, new_total_rph):
        return new_total_rph * rph_map / np.sum(rph_map)

    def load_from_image(file_path, scale=1.0, convert_to_grayscale=True):
        im = imageio.imread(file_path)  # type: np.ndarray
        im = im.astype(np.float32)
        if len(im.shape) == 3:
            if im.shape[2] == 1:  # cool, it is a grayscale image
                im = im.reshape(shape=[np.shape[0], np.shape[1]])
            else:
                if convert_to_grayscale:
                    im = np.dot(im, np.array(
                        [0.299, 0.587, 0.114], np.float32))
                else:
                    raise ValueError(
                        'The input image is not grayscale and convert_to_grayscale argument was set to false')
        assert len(
            im.shape) == 2, "Something is wrong. The map should be a grayscale image"
        return scale * im / 255

    def _interpolate_map(map_left, map_right, idx_left, idx_right, target_idx, num_of_maps):
        if map_left is None and map_right is None:
            raise ValueError('No maps given to interpolate from!')
        if target_idx == idx_left or target_idx == idx_right:
            assert idx_left == idx_right
        if idx_left > idx_right:
            if target_idx > idx_left:
                idx_right += num_of_maps
            else:
                idx_left -= num_of_maps
        assert not(idx_left > idx_right or target_idx < idx_left or target_idx >
                   idx_right), 'idx_left<=target_idx<=idx_right needs to be satisfied. passed values respectively were: {0},{1},{2}'.format(idx_left, target_idx, idx_right)
        if map_left is None:
            return map_right
        if map_right is None:
            return map_left
        if idx_left == target_idx:
            return map_left
        if idx_right == target_idx:
            return map_right
        balance = (target_idx - idx_left) / (idx_right - idx_left)
        return map_left + (map_right - map_left) * balance

    def _find_neighbour_map(maps, target_idx, direction=1):
        """set direction=1 for right. set -1 for left"""
        idx = target_idx
        while maps[idx % len(maps)] is None:
            idx = idx + direction
            if idx % len(maps) == target_idx:
                # we have come full circle
                raise ValueError("All the maps are none!")
        return idx % len(maps)

    def create_by_interpolation(other_maps, target_index):
        """Does bilinear interpolation
        """
        # find the map at an index < target_index:
        idx_left = RPHMapUtils._find_neighbour_map(
            other_maps, target_index, -1)
        idx_right = RPHMapUtils._find_neighbour_map(
            other_maps, target_index, 1)
        return RPHMapUtils._interpolate_map(other_maps[idx_left], other_maps[idx_right], idx_left, idx_right, target_index, len(other_maps))

    def absolute_index_to_row_col(rph_map: np.ndarray, index):
        row = index // rph_map.shape[1]
        col = index % rph_map.shape[1]
        return row, col

    def map_coord_to_game_coord(rph_map: np.ndarray, row, col, x_min, x_max, y_min, y_max):
        x_percent = col / rph_map.shape[1]
        x = x_min + x_percent * (x_max - x_min)
        y_percent = 1 - (row / rph_map.shape[0])
        y = y_min + y_percent * (y_max - y_min)
        return np.array([x, y, 0])

    def fill_all_by_interpolation(maps):
        """In the given list of maps, fills all the `None` entries by bilinear interpolation
        """
        idx_left = RPHMapUtils._find_neighbour_map(maps, 0, -1)
        left_indices = [idx_left] * len(maps)
        idx_right = RPHMapUtils._find_neighbour_map(maps, len(maps) - 1, 1)
        right_indices = [idx_right] * len(maps)
        for i in range(len(maps)):
            if maps[i] is not None:
                idx_left = i
            if maps[len(maps) - i - 1] is not None:
                idx_right = len(maps) - i - 1
            left_indices[i] = idx_left
            right_indices[len(maps) - i - 1] = idx_right
        for i in range(len(maps)):
            map_left = maps[left_indices[i]]
            map_right = maps[right_indices[i]]
            # print("{0},{1},{2}".format(
            #     left_indices[i], i, right_indices[i])) if i % 10 == 0 else None
            maps[i] = RPHMapUtils._interpolate_map(
                map_left, map_right, left_indices[i], right_indices[i], i, len(maps))
        return maps


class Enriched_RPH_Map:
    def __init__(self, rph_map: np.ndarray):
        self.rph_map = rph_map
        self.total_rph = np.sum(rph_map)
        self.probabilites_flat = np.reshape(
            self.rph_map / self.total_rph, [self.rph_map.size])


class MapBasedRequestGenerator(gymGame.GameComponent):
    def __init__(self):
        super().__init__()
        self.width = 4
        self.height = 4
        self.rph_maps = []  # type: List[np.ndarray]
        self._enriched_maps = []  # type: List[Enriched_RPH_Map]

    def awake(self):
        timeKeeperGO = self.gameObject.scene.findObjectByName(
            'Time Keeper')  # type: gymGame.GameObject
        self.timeKeeper = timeKeeperGO.getComponent(
            gym_ERSLE.pyERSEnv.TimeKeeper)  # type: gym_ERSLE.pyERSEnv.TimeKeeper
        requestsPoolGO = self.gameObject.scene.findObjectByName(
            'Requests Pool')  # type: gymGame.GameObject
        self.requestsPool = requestsPoolGO.getComponent(
            gym_ERSLE.pyERSEnv.RequestsPool)  # type: gym_ERSLE.pyERSEnv.RequestsPool
        for rph_map in self.rph_maps:
            self._enriched_maps.append(Enriched_RPH_Map(rph_map))

    def update(self):
        current_rph_map = self._enriched_maps[int(
            self.timeKeeper.minutesInCurrentDay)]
        total_rpf = current_rph_map.total_rph * \
            self.timeKeeper.simulatedSecondsPerFrame / 3600
        # now on an average total_rpf requests should me produced per frame
        assert total_rpf < 1, "The setting for requests per hour is too high. Cannot accurately simulate that"
        request_probability = total_rpf
        rand = self.gameObject.scene.random
        r = rand.random()
        if r < request_probability:
            idx = self.gameObject.scene.nprandom.choice(
                current_rph_map.rph_map.size, p=current_rph_map.probabilites_flat)
            r, c = RPHMapUtils.absolute_index_to_row_col(
                current_rph_map.rph_map, idx)
            x_min, x_max = self.gameObject.position[0] - 0.5 * \
                self.width, self.gameObject.position[0] + 0.5 * self.width
            y_min, y_max = self.gameObject.position[1] - 0.5 * \
                self.height, self.gameObject.position[1] + 0.5 * self.height
            position = RPHMapUtils.map_coord_to_game_coord(
                current_rph_map.rph_map, r, c, x_min, x_max, y_min, y_max)
            self.requestsPool.createNew(position)
