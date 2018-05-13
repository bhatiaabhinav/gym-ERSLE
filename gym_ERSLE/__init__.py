from gym.envs.registration import register
from gym_ERSLE.pyERSEnv import ToyScene  # noqa F401
from gym_ERSLE.pyERSEnv import Scene4  # noqa F401
from gym_ERSLE.pyERSEnv import Scene5  # noqa F401
from gym_ERSLE.pyERSEnv import SgScene  # noqa F401

version_to_scene_map = {
    'v3': 'gym_ERSLE:ToyScene',
    'v4': 'gym_ERSLE:Scene4',
    'v5': 'gym_ERSLE:Scene5',
    'v6': 'gym_ERSLE:Scene5',
    'v7': 'gym_ERSLE:Scene5',
    'v8': 'gym_ERSLE:Scene5'
}

version_to_ambs_map = {'v4': 24, 'v5': 40, 'v6': 32, 'v7': 24, 'v8': 16}
version_to_bases_map = {'v4': 12, 'v5': 25, 'v6': 25, 'v7': 25, 'v8': 25}

for version in ['v3', 'v4']:
    for decision_interval in [1, 10, 15, 20, 30, 60, 120, 240, 360, 720, 1440]:
        for ca in [False, True]:
            for im in [False, True]:
                for dynamic in [False, True]:
                    for blips in [False, True]:
                        register(
                            id='pyERSEnv{0}{1}{2}{3}{4}-{5}'.format(
                                '-im' if im else '',
                                '-ca' if ca else '',
                                '-dynamic' if dynamic else '',
                                '-blips' if blips else '',
                                '-{0}'.format(decision_interval) if decision_interval > 1 else '',
                                version
                            ),
                            entry_point=version_to_scene_map[version],
                            kwargs={'discrete_action': not ca, 'discrete_state': not im,
                                    'decision_interval': decision_interval, 'dynamic': dynamic, 'random_blips': blips},
                            max_episode_steps=10000000,
                            nondeterministic=False
                        )


for version in ['v5', 'v6', 'v7', 'v8']:
    for decision_interval in [1, 10, 15, 20, 30, 60, 120, 240, 360, 720, 1440]:
        for ca in [False, True]:
            for im in [False, True]:
                for dynamic in [False, True]:
                    for blips in [False, True]:
                        register(
                            id='pyERSEnv{0}{1}{2}{3}{4}-{5}'.format(
                                '-im' if im else '',
                                '-ca' if ca else '',
                                '-dynamic' if dynamic else '',
                                '-blips' if blips else '',
                                '-{0}'.format(
                                    decision_interval) if decision_interval > 1 else '',
                                version
                            ),
                            entry_point=version_to_scene_map[version],
                            kwargs={'discrete_action': not ca, 'discrete_state': not im,
                                    'decision_interval': decision_interval, 'dynamic': dynamic, 'random_blips': blips,
                                    'nbases': version_to_bases_map[version], 'nambs': version_to_ambs_map[version],
                                    'nhospitals': 36},
                            max_episode_steps=10000000,
                            nondeterministic=False
                        )
                        register(
                            id='SgERSEnv{0}{1}{2}{3}{4}-{5}'.format(
                                '-im' if im else '',
                                '-ca' if ca else '',
                                '-dynamic' if dynamic else '',
                                '-blips' if blips else '',
                                '-{0}'.format(
                                    decision_interval) if decision_interval > 1 else '',
                                version
                            ),
                            entry_point='gym_ERSLE:SgScene',
                            kwargs={'discrete_action': not ca, 'discrete_state': not im,
                                    'decision_interval': decision_interval, 'dynamic': dynamic, 'random_blips': blips,
                                    'nbases': version_to_bases_map[version], 'nambs': version_to_ambs_map[version],
                                    'nhospitals': 36},
                            max_episode_steps=10000000,
                            nondeterministic=False
                        )
