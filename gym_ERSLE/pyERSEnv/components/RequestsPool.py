import gym_ERSLE.pyERSEnv
import gymGame
import numpy as np
from typing import List


class RequestsPool(gymGame.GameComponent):

    def __init__(self):
        super().__init__()
        self.requestPrefab = None
        self.maximumRequests = 30
        self.requests = []  # type: List[gym_ERSLE.pyERSEnv.Request]
        self.stashPoint = np.array([-100, -100, 0])
        self._nextPooledRequestID = 0

    def awake(self):
        pass

    def start(self):
        for i in range(self.maximumRequests):
            # type: gym_ERSLE.pyERSEnv.RequestPrefab
            obj = self.gameObject.scene.instantiate(self.requestPrefab, position=self.stashPoint)
            obj.deactivate()
            req = obj.getComponent(gym_ERSLE.pyERSEnv.Request)  # type: gym_ERSLE.pyERSEnv.Request
            self.requests.append(req)

    def createNew(self, position):
        r = self.requests[self._nextPooledRequestID]
        if r.gameObject.isActive:
            #print("No more requests can be created right now")
            return None
        self._nextPooledRequestID = (self._nextPooledRequestID + 1) % self.maximumRequests
        r.gameObject.setPosition(position)
        r.gameObject.activate()
        r.create()
        return r

    def returnBack(self, r):
        r.gameObject.deactivate()
        r.reset()
