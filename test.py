import gym_ERSLE
import gym
import time

env1 = gym.make('ERSEnvNoFrameskip-v4')
env2 = gym.make('ERSEnvNoFrameskip-v4')
env1.seed(1)
env2.seed(200)
obs = env1.reset()
obs = env2.reset()

for i in range(10000):
    obs,r,d,_ = env1.step(0)
    env2.step(0)
    env1.render(close=False)
    env2.render(close=False)
    time.sleep(1.0/60);
    
    if r > 0: print(r)

env1.close()
env2.close()