from gym.envs.registration import register
from gym_ERSLE.pyERSEnv import ToyScene

register(
    id='pyERSEnv-v3',
    entry_point='gym_ERSLE:ToyScene',
    kwargs={'discrete_action':True, 'discrete_state':True},
    max_episode_steps = 10000000,
    nondeterministic=False
)

register(
    id='pyERSEnv-ca-v3',
    entry_point='gym_ERSLE:ToyScene',
    kwargs={'discrete_action':False, 'discrete_state':True},
    max_episode_steps = 10000000,
    nondeterministic=False
)

register(
    id='pyERSEnv-cs-v3',
    entry_point='gym_ERSLE:ToyScene',
    kwargs={'discrete_action':True, 'discrete_state':False},
    max_episode_steps = 10000000,
    nondeterministic=False
)

register(
    id='pyERSEnv-cs-ca-v3',
    entry_point='gym_ERSLE:ToyScene',
    kwargs={'discrete_action':False, 'discrete_state':False},
    max_episode_steps = 10000000,
    nondeterministic=False
)