import gym_ERSLE.pyERSEnv
import gymGame
import numpy as np
import math


class RequestsGenerator(gymGame.GameComponent):

    def __init__(self):
        super().__init__()
        self.requestsPerHour = 2.0
        self.width = 4
        self.height = 4

    def awake(self):
        timeKeeperGO = self.gameObject.scene.findObjectByName(
            'Time Keeper')  # type: gymGame.GameObject
        self.timeKeeper = timeKeeperGO.getComponent(
            gym_ERSLE.pyERSEnv.TimeKeeper)  # type: gym_ERSLE.pyERSEnv.TimeKeeper

        requestsPoolGO = self.gameObject.scene.findObjectByName(
            'Requests Pool')  # type: gymGame.GameObject
        self.requestsPool = requestsPoolGO.getComponent(
            gym_ERSLE.pyERSEnv.RequestsPool)  # type: gym_ERSLE.pyERSEnv.RequestsPool

    def update(self):
        requestsPerSecond = self.requestsPerHour / 3600
        requestsPerFrame = requestsPerSecond * self.timeKeeper.simulatedSecondsPerFrame
        requestProbability = requestsPerFrame
        rand = self.gameObject.scene.random
        r = rand.random()
        if r < requestProbability:
            x = self.gameObject.position[0] + self.width * (rand.random() - 0.5)
            y = self.gameObject.position[1] + self.height * (rand.random() - 0.5)
            self.requestsPool.createNew(np.array([x, y, 0]))


class DynamicRequestRate(gymGame.GameComponent):
    def __init__(self):
        super().__init__()
        self.peak_time = 0  # in terms of fraction of day passed

    def awake(self):
        self.rg = self.gameObject.getComponent(RequestsGenerator)  # type: RequestsGenerator
        time_keeper_GO = self.gameObject.scene.findObjectByName(
            'Time Keeper')  # type: gymGame.GameObject
        self.time_keeper = time_keeper_GO.getComponent(
            gym_ERSLE.pyERSEnv.TimeKeeper)  # type: gym_ERSLE.pyERSEnv.TimeKeeper

    def start(self):
        self.max_rph = self.rg.requestsPerHour

    def update(self):
        peak_time_angle = self.peak_time * math.pi
        cur_time_angle = self.time_keeper.getTimeOfDayAsFractionOfDayPassed() * math.pi
        self.rg.requestsPerHour = self.max_rph * (math.cos(peak_time_angle - cur_time_angle)**2)


class Blip(gymGame.GameComponent):
    def __init__(self, peak_time=0.5, peak_sigma=0.05, peak_height=5):
        super().__init__()
        self.peak_time = 0  # in terms of fraction of day passed
        self.peak_height = peak_height
        self.peak_sigma = peak_sigma

    def awake(self):
        self.rg = self.gameObject.getComponent(RequestsGenerator)  # type: RequestsGenerator
        time_keeper_GO = self.gameObject.scene.findObjectByName(
            'Time Keeper')  # type: gymGame.GameObject
        self.time_keeper = time_keeper_GO.getComponent(
            gym_ERSLE.pyERSEnv.TimeKeeper)  # type: gym_ERSLE.pyERSEnv.TimeKeeper

    def update(self):
        self.variance = self.peak_sigma * self.peak_sigma
        # refer https://en.wikipedia.org/wiki/Normal_distribution
        coeff = self.peak_height / (2.5 * self.peak_sigma)
        power = - ((self.time_keeper.getTimeOfDayAsFractionOfDayPassed() -
                    self.peak_time)**2) / (2 * self.variance)
        self.rg.requestsPerHour = coeff * (math.e**power)
