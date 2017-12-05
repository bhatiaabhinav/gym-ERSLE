import gym_ERSLE.pyERSEnv
import gymGame
import numpy as np

class RequestsGenerator(gymGame.GameComponent):

    def __init__(self):
        super().__init__()
        self.requestsPerHour = 2.0
        self.width = 4
        self.height = 4

    def awake(self):
        timeKeeperGO = self.gameObject.scene.findObjectByName('Time Keeper') # type: gymGame.GameObject
        self.timeKeeper = timeKeeperGO.getComponent(gym_ERSLE.pyERSEnv.TimeKeeper) # type: gym_ERSLE.pyERSEnv.TimeKeeper

        requestsPoolGO = self.gameObject.scene.findObjectByName('Requests Pool') # type: gymGame.GameObject
        self.requestsPool = requestsPoolGO.getComponent(gym_ERSLE.pyERSEnv.RequestsPool) # type: gym_ERSLE.pyERSEnv.RequestsPool

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