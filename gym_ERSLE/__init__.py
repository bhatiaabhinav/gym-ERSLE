from gym_ERSLE.ERSLE_env import ERSEnv
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

for env_name in ['ERSEnv-v0', 'ERSEnv-v1']:
    register(
        id=env_name,
        entry_point='gym_ERSLE:ERSEnv',
        kwargs={'exe_path': os.path.join(app_dir, env_name) + extn },
        max_episode_steps = 10000000,
        nondeterministic=False
    )