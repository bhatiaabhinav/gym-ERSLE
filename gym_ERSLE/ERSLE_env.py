import gym
from gym import error, spaces, utils
from gym.utils import seeding
import socket
import subprocess
import time
import struct
import numpy as np
try:
    import ujson as json # Not necessary for monitor writing, but very useful for monitor loading
except ImportError:
    import json

REMOTE_STARTING_PORT_NO = 7710
REMOTE_MAX_PORT_NO = 8000

class ERSEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    image_width = 24
    image_height = 20

    def __init__(self, exe_path, image_observation_space):

        subprocess.Popen(exe_path, close_fds=True)
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
            self.observation_space = spaces.Box(0, 255, shape=(ERSEnv.image_height, ERSEnv.image_width, int(ob_space.split(' ')[3])))
        else:
            # nh = 387, nw = 1, nc = 1
            n = int(ob_space.split(' ')[1])
            self.observation_space = spaces.Box(-1.0, 1.0, shape=(n,1,1))


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
            n = self.observation_space.shape[0] * self.observation_space.shape[1] * self.observation_space.shape[2]
            fixed_length_part = n + 4 * 2 # obs and reward and isTerminal
            msg_data, msg_addr = self.sock.recvfrom(fixed_length_part + 2048)
            msg_data_bytes = struct.unpack("%dc" % n, msg_data[:n])
            obs = np.array(msg_data_bytes).reshape(self.observation_space.shape)
            obs.dtype = np.uint8
            reward_and_isTerminal = struct.unpack("%df" % 2, msg_data[n:n+8])
            reward = reward_and_isTerminal[0]
            isTerminal = reward_and_isTerminal[1] > 0
            info_msg = msg_data[fixed_length_part:].decode()
        return (obs, reward, isTerminal, json.loads(info_msg))

    def _reset(self):
        self.sock.sendto("reset".encode(), self.REMOTE_SOCKET_ADDRESS)
        if not self.image_observation_space:
            msg_data, msg_addr = self.sock.recvfrom(4 * self.observation_space.shape[0])
            msg_data_float = struct.unpack("%df" % self.observation_space.shape[0], msg_data)
            obs = np.array(msg_data_float).reshape(self.observation_space.shape)
        else:
            n = self.observation_space.shape[0] * self.observation_space.shape[1] * self.observation_space.shape[2]
            msg_data, msg_addr = self.sock.recvfrom(n)
            msg_data_bytes = struct.unpack("%dc" % n, msg_data)
            obs = np.array(msg_data_bytes).reshape(self.observation_space.shape)
            obs.dtype = np.uint8
        return obs

    def _seed(self, seed = None):
        if seed is None:
            seed = 0
        self._send_message("seed " + str(seed))
        return super()._seed(seed)

    def _render(self, mode='human', close=False):
        if close:
            self._send_message("render close")
        else:
            self._send_message("render open")

    def _close(self):
        print(self._send_message("close"))
        return super()._close()

    def _find_simulator(self):
        for port in range(REMOTE_STARTING_PORT_NO, REMOTE_MAX_PORT_NO):
            try:
                self.REMOTE_SOCKET_ADDRESS = ("127.0.0.1", port)
                if self._send_message("init") == 'ack':
                    return True
            except socket.timeout:
                ...
            
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
    obs = env.reset()
    env.render()
    for i in range(10000):
        obs, r, d, info = env.step(np.random.randint(0,36))
        #print(info)
        if d: obs = env.reset()
    env.close()