from .ERSLE_env import ERSEnv
from gym.envs.registration import register
import os
import platform

app_dir = os.getenv('GYM_ERSLE_APP_DIR')
if app_dir is None:
    raise EnvironmentError('Please set GYM_ERSLE_APP_DIR environment variable to point to the directory where ERS simulator executables are placed')

if platform.system() == 'Windows':
    extn = '.exe'
elif platform.system() == 'Darwin':
    extn = '.app'
else:
    extn = ''

for env_no in range(4):
    env_name = 'ERSEnv-v{0}'.format(env_no)
    register(
        id=env_name,
        entry_point='gym_ERSLE:unityERSEnv:ERSEnv',
        kwargs={'exe_path': os.path.join(app_dir, env_name) + extn, 'image_observation_space': False },
        max_episode_steps = 10000000,
        nondeterministic=False
    )
    register(
        id='ERSEnv-image-v{0}'.format(env_no),
        entry_point='gym_ERSLE:unityERSEnv:ERSEnv',
        kwargs={'exe_path': os.path.join(app_dir, env_name) + extn, 'image_observation_space': True },
        max_episode_steps = 10000000,
        nondeterministic=False
    )
