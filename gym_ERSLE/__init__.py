from gym.envs.registration import register
from gym_ERSLE.pyERSEnv import ToyScene

for decision_interval in [1, 30, 60, 120, 240, 360, 720, 1440]:
    for ca in [False, True]:
        for im in [False, True]:
            for dynamic in [False, True]:
                register(
                    id='pyERSEnv{0}{1}{2}{3}-v3'.format(
                        '-im' if im else '',
                        '-ca' if ca else '',
                        '-dynamic' if dynamic else '',
                        '-{0}'.format(decision_interval) if decision_interval > 1 else ''
                    ),
                    entry_point='gym_ERSLE:ToyScene',
                    kwargs={'discrete_action':not ca, 'discrete_state':not im, 'decision_interval': decision_interval, 'dynamic': dynamic},
                    max_episode_steps = 10000000,
                    nondeterministic=False
                )