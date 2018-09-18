import argparse
import ast
import gym_ERSLE  # noqa: F401
import gym
import numpy as np
import typing  # noqa: F401
import time
from baselines.ers.wrappers import ERStoMMDPWrapper, MMDPActionSpaceNormalizerWrapper, MMDPActionWrapper

NOOP = 0
# NOOP = np.array([1,1,3,9,3,1])/18
NOOP = np.array([2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]) / 24
# TARGET = np.array([5, 2, 1, 4, 1, 5])/18
TARGET = np.array([4, 4, 1, 1, 2, 1, 2, 3, 2, 3, 1, 0]) / 24


def eval(env_name, episodes=10, render=False, seed=42, action=0):
    print('Evaluating {0} for {1} episodes. Seed={2}'.format(
        env_name, episodes, seed))
    env = gym.make(env_name)  # type: gym.Env
    env = MMDPActionWrapper(MMDPActionSpaceNormalizerWrapper(ERStoMMDPWrapper(env)), True)
    if action == 'uniform':
        action = np.array([1 / env.action_space.shape[0]] * env.action_space.shape[0])
    env.seed(seed)
    tstart = time.time()
    Rs = []
    blip_Rs = []
    f = 0
    for ep in range(episodes):
        d = False
        R = 0
        blip_R = 0
        obs = env.reset()
        f += 1
        if render:
            env.render()
        while not d:
            obs, r, d, _ = env.step(action)
            f += 1
            if render:
                env.render(mode='human')
            # time.sleep(1/60)
            R += r
            blip_R += _['blip_reward']
            # print(obs)
        Rs.append(R)
        blip_Rs.append(blip_R)
        print({'R': R, 'blip_R': blip_R})
    tend = time.time()
    env.close()
    stats = {
        'episode': ep,
        'av_reward': np.average(Rs),
        'av_blip_reward': np.average(blip_Rs),
        'std_reward': np.std(Rs),
        'std_blip_reward': np.std(blip_Rs),
        'fps': episodes * 1440 / (tend - tstart),
        'eps': episodes / (tend - tstart)
    }
    print(stats)
    print()


def str2bool(v):
    if v is True or v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v is False or v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--env', help='environment ID',
                    default='pyERSEnv-ca-dynamic-1440-v6')
parser.add_argument(
    '--seed', help='initial env seed for testing', default=42, type=int)
parser.add_argument(
    '--episodes', help='Test for how many episodes', default=5, type=int)
parser.add_argument('--render', help='render?', default=False, type=str2bool)
parser.add_argument('--alloc', help='static allocaton to test',
                    default="uniform")
args = parser.parse_args()
print('alloc={0}'.format(args.alloc))
if args.alloc == 'uniform':
    alloc = args.alloc
else:
    alloc = np.array(ast.literal_eval(args.alloc))
    alloc = alloc / np.sum(alloc)
eval(args.env, episodes=args.episodes,
     render=args.render, seed=args.seed, action=alloc)
# eval('PongNoFrameskip-v4', episodes=20)
