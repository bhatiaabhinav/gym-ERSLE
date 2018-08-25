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


def build_constraints_2_level_simple(nzones, zone_ids_per_group, group_mins, group_maxs, local_min, local_max, nresources=1):
    constraints = {
        "name": "root",
        "equals": nresources,
        "min": nresources,
        "max": nresources,
        "children": []
    }
    zones_consumed_set = set()
    for zone_ids, group_min, group_max, group_index in zip(zone_ids_per_group, group_mins, group_maxs, range(len(zone_ids_per_group))):
        group = {
            "name": "group{0}".format(group_index),
            "min": group_min,
            "max": group_max,
            "equals": None,
            "children": []
        }
        for zone_id, group_zone_index in zip(zone_ids, range(len(zone_ids))):
            assert zone_id not in zones_consumed_set, "Something wrong. zone_id {0} cannot be part of more than one group".format(
                zone_id)
            zone = {
                "name": "G{0}Z{1}".format(group_index, group_zone_index),
                "min": local_min,
                "max": local_max,
                "equals": None,
                "zone_id": zone_id
            }
            zones_consumed_set.add(zone_id)
            group['children'].append(zone)
        constraints['children'].append(group)
    assert len(
        zones_consumed_set) == nzones, "All zone_ids need to be specified as part of some group"
    return constraints


if __name__ == '__main__':
    # c = build_constraints_min_max_every(25, 5, 2, 10, 0, 8, nresources=32)
    c = build_constraints_2_level_simple(25,
                                         [
                                             [0, 1, 5, 6, 7],
                                             [2, 3, 4, 8, 9],
                                             [10, 15, 20],
                                             [11, 12, 16, 17],
                                             [13, 14, 18, 19, 24],
                                             [21, 22, 23]
                                         ],
                                         [3, 3, 1, 3, 3, 1],
                                         [16, 16, 8, 16, 16, 8],
                                         0,
                                         8)
    print(c)
