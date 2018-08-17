import math


def build_constraints_min_max_every(nzones, group_size, group_min, group_max, local_min, local_max, nresources=1):
    ngroups = math.ceil(nzones / group_size)
    constraints = {
        "name": "root",
        "equals": nresources,
        "min": nresources,
        "max": nresources,
        "children": []
    }
    zone_id = 0
    for group_index in range(ngroups):
        group = {
            "name": "group{0}".format(group_index),
            "min": group_min,
            "max": group_max,
            "equals": None,
            "children": []
        }
        for group_zone_index in range(group_size):
            if zone_id >= nzones:
                break
            zone = {
                "name": "G{0}Z{1}".format(group_index, group_zone_index),
                "zone_id": zone_id,
                "min": local_min,
                "max": local_max,
                "equals": None
            }
            group["children"].append(zone)
            zone_id += 1
        constraints["children"].append(group)
    return constraints


if __name__ == '__main__':
    c = build_constraints_min_max_every(25, 5, 2, 10, 0, 8, nresources=32)
    print(c)
