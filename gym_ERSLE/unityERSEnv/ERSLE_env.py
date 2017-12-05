import gym
from gym import error, spaces, utils
from gym.utils import seeding
import socket
import subprocess
import time
import struct
import numpy as np
import PIL
import io
import matplotlib.pyplot as plt
try:
    import ujson as json # Not necessary for monitor writing, but very useful for monitor loading
except ImportError:
    import json

REMOTE_STARTING_PORT_NO = 7710
REMOTE_MAX_PORT_NO = 8000

class ERSEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    image_width = 32
    image_height = 32
    image_channels = 3

    def __init__(self, exe_path, image_observation_space):

        subprocess.Popen(exe_path + " -batchmode", close_fds=True)
        time.sleep(10)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', 0))
        self.sock.settimeout(10)
        if not self._find_simulator():
            print("No available simulator seems to be running!!")
            raise RuntimeError()
        print("connected :)")
        self.action_space = spaces.Discrete(int(self._send_message("action_space_n")))
        self.image_observation_space = image_observation_space
        if image_observation_space:
            self._send_message("set_image_observation_space true {0} {1}".format(ERSEnv.image_height, ERSEnv.image_width))
        else:
            self._send_message("set_image_observation_space false")
        ob_space = self._send_message("observation_space")
        if image_observation_space:
            ERSEnv.image_height = int(ob_space.split(' ')[1])
            ERSEnv.image_width = int(ob_space.split(' ')[2])
            #ERSEnv.image_channels = int(ob_space.split(' ')[3])
            ERSEnv.image_channels = 1
            self.observation_space = spaces.Box(0, 255, shape=(ERSEnv.image_height, ERSEnv.image_width, ERSEnv.image_channels))
        else:
            # nh = 387, nw = 1, nc = 1
            n = int(ob_space.split(' ')[1])
            self.observation_space = spaces.Box(-1.0, 1.0, shape=(n,1,1))
        self.viewer = None
        self.current_obs = None
        self.is_render_open = False
        self._send_message("render close") # close by default

    def _step(self, action):
        self.sock.sendto(("step " + str(action)).encode(), self.REMOTE_SOCKET_ADDRESS)
        if not self.image_observation_space:
            fixed_length_part = 4 * (self.observation_space.shape[0] + 2) # obs and reward and isTerminal
            msg_data, msg_addr = self.sock.recvfrom(fixed_length_part + 2048)
            msg_data_float = struct.unpack("%df" % (self.observation_space.shape[0] + 2), msg_data[:fixed_length_part])
            obs = np.array(msg_data_float[:-2]).reshape(self.observation_space.shape)
            reward = msg_data_float[-2]
            isTerminal = msg_data_float[-1] > 0
            info_msg = msg_data[fixed_length_part:].decode()
        else:
            #n = self.observation_space.shape[0] * self.observation_space.shape[1] * self.observation_space.shape[2]
            n = 4096
            fixed_length_part = n + 4 * 2 # obs and reward and isTerminal
            msg_data, msg_addr = self.sock.recvfrom(fixed_length_part + 2048)
            #msg_data_bytes = struct.unpack("%dc" % n, msg_data[:n])
            obs_stream = io.BytesIO(msg_data)
            obs = (255 * plt.imread(obs_stream)).astype(np.uint8)
            #obs = np.array(msg_data_bytes).reshape(self.observation_space.shape)
            #obs.dtype = np.uint8
            reward_and_isTerminal = struct.unpack("%df" % 2, msg_data[n:n+8])
            reward = reward_and_isTerminal[0]
            isTerminal = reward_and_isTerminal[1] > 0
            info_msg = msg_data[fixed_length_part:].decode()
            self.current_obs = obs
            obs = obs[:,:,0:1]
        return (obs, reward, isTerminal, json.loads(info_msg))

    def _reset(self):
        self.sock.sendto("reset".encode(), self.REMOTE_SOCKET_ADDRESS)
        if not self.image_observation_space:
            msg_data, msg_addr = self.sock.recvfrom(4 * self.observation_space.shape[0])
            msg_data_float = struct.unpack("%df" % self.observation_space.shape[0], msg_data)
            obs = np.array(msg_data_float).reshape(self.observation_space.shape)
        else:
            #n = self.observation_space.shape[0] * self.observation_space.shape[1] * self.observation_space.shape[2]
            n = 4096
            msg_data, msg_addr = self.sock.recvfrom(n)
            #msg_data_bytes = struct.unpack("%dc" % n, msg_data)
            obs_stream = io.BytesIO(msg_data)
            obs = (255 * plt.imread(obs_stream)).astype(np.uint8)
            #obs = np.array(msg_data_bytes).reshape(self.observation_space.shape)
            #obs.dtype = np.uint8
            self.current_obs = obs
            obs = obs[:,:,0:1]
        return obs

    def _seed(self, seed = None):
        if seed is None:
            seed = 0
        self._send_message("seed " + str(seed))
        return super()._seed(seed)

    def _render(self, mode='human', close=False):
        if not self.image_observation_space:
            if close:
                if self.is_render_open:
                    self._send_message("render close")
                    self.is_render_open = False
            else:
                if not self.is_render_open:
                    self._send_message("render open")
                    self.is_render_open = True
        else:
            if not close:
                if mode == 'human':
                    if self.viewer is None:
                        from gym.envs.classic_control.rendering import SimpleImageViewer
                        self.viewer = SimpleImageViewer()
                    self.viewer.imshow(self.current_obs)
                else:
                    return self.current_obs
            else:
                if self.viewer is not None and self.viewer.isopen:
                    self.viewer.close()
            

    def _close(self):
        print(self._send_message("close"))
        return super()._close()

    def _find_simulator(self):
        for port in range(REMOTE_STARTING_PORT_NO, REMOTE_MAX_PORT_NO):
            try:
                self.REMOTE_SOCKET_ADDRESS = ("127.0.0.1", port)
                if self._send_message("init") == 'ack':
                    return True
                else:
                    print('confirmed that port {0} simlulator is busy'.format(port))
            except socket.timeout:
                print('No response from port {0}'.format(port))
            
        self.REMOTE_SOCKET_ADDRESS = None;
        return False

    def _send_message(self, msg):
        self.sock.sendto(msg.encode(), self.REMOTE_SOCKET_ADDRESS)
        msg_data, msg_addr = self.sock.recvfrom(1024)
        #print(str(msg_addr) + " replied: " + msg_data.decode())
        return msg_data.decode()

if __name__ == '__main__':
    import gym
    import gym_ERSLE
    env = gym.make('ERSEnv-image-v2')
    #env = gym.make('ERSEnv-v2')
    obs = env.reset()
    #env.render()
    print(env.observation_space)
    print(obs.shape)
    import time
    t = time.time()
    while True:
        obs, r, d, info = env.step(np.random.randint(0,env.action_space.n))
        #env.render()
        
        #print(r)
        #print(info)
        if d: obs = env.reset()
    print(time.time() - t)
    #obs, r, d, _ = env.step(29)
    #assert(_['base5'] == 2)
    #assert(_['base3'] == 8)
    env.close()