import gym_ERSLE
import gym
import numpy as np
import typing
import time

NOOP = 0
NOOP = np.array([1,1,3,9,3,1])/18
TARGET = np.array([5, 2, 1, 4, 1, 5])/18

def eval(env_name, episodes=10, render = False):
    print('Evaluating ' + env_name)
    env = gym.make(env_name) # type: gym.Env
    env.seed(0)
    tstart = time.time()
    Rs = []
    f = 0
    for ep in range(episodes):
        d = False
        R = 0
        obs = env.reset()
        f += 1
        if render: env.render()
        while not d:
            obs, r, d, _ = env.step(TARGET)
            f += 1
            if render: env.render()
            R += r
            #print(obs)
        Rs.append(R)
        print(R)
    tend = time.time()
    env.close()
    stats = {
        'av_reward': np.average(Rs),
        'fps': episodes*1440 / (tend - tstart),
        'eps': episodes/(tend - tstart)
    }
    print(stats)
    print()

eval('pyERSEnv-im-ca-dynamic-v3', episodes=5, render=False)
#eval('PongNoFrameskip-v4', episodes=20)