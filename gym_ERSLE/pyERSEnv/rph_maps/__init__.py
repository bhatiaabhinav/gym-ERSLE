import os.path as osp
import os
import re
from gym_ERSLE.pyERSEnv import RPHMapUtils

DIR_NAME = osp.dirname(__file__)
regex = re.compile(r'\d+')

singapore_rph_maps = [None] * 1440
singapore_rph = {
    180: 210 / 26,
    540: 485 / 26,
    900: 415 / 26,
    1260: 390 / 26
}
for file in os.listdir(DIR_NAME):
    if 'singapore_rph_map' in file:
        minute = int(regex.findall(file)[-1])
        singapore_rph_maps[minute] = RPHMapUtils.load_from_image(
            osp.join(DIR_NAME, file))
        singapore_rph_maps[minute] = RPHMapUtils.scale_to_total_requests_per_hour(
            singapore_rph_maps[minute], singapore_rph[minute])
        print('Read singapore rph map for minute {0}'.format(minute))

singapore_rph_maps = RPHMapUtils.fill_all_by_interpolation(singapore_rph_maps)
