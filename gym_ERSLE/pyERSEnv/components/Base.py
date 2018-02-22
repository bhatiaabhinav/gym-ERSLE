import numpy as np
import gym_ERSLE.pyERSEnv
import gymGame
from typing import Set


class Base(gymGame.GameComponent):
    def __init__(self):
        super().__init__()
        self.initialAllocationPercentage = 100
        self.allocatedAmbulances = set()  # type: Set[ers.Ambulance]
        self.ID = None  # type: int
        self.spawnPointOffset = np.array([0.1, 0, 0])
        self.ersManager = None  # type: gym_ERSLE.pyERSEnv.ERSManager
        self.last_count = -1

    def awake(self):
        ersManagerGO = self.gameObject.scene.findObjectByName(
            'ERS Manager')  # type: gymGame.GameObject
        self.ersManager = ersManagerGO.getComponent(
            gym_ERSLE.pyERSEnv.ERSManager)  # type: gym_ERSLE.pyERSEnv.ERSManager
        self.level_sprite = self.gameObject.getComponent(
            gymGame.SimpleSprite, tag='level')  # type: gymGame.SimpleSprite
        self.max_size = self.level_sprite.size

    def register(self):
        self.ID = self.ersManager.registerBase(self)
        # print('Registered base with ID {0}'.format(self.ID))

    def addAmbulance(self, a):
        self.allocatedAmbulances.add(a)

    def removeAmbulance(self, a):
        self.allocatedAmbulances.remove(a)

    def _log_transform(self, x, max_x, max_ans, t=1):
        return max_ans * np.log(1 + x / t) / np.log(1 + max_x / t)

    def update(self):
        new_count = len(self.allocatedAmbulances)
        if new_count != self.last_count:
            self.last_count = new_count
            # fraction = len(self.allocatedAmbulances) / \
            #     self.ersManager.AMBULANCE_COUNT
            fraction = self._log_transform(
                len(self.allocatedAmbulances), self.ersManager.AMBULANCE_COUNT, 1, t=5)
            self.level_sprite.setSize(
                [fraction * self.max_size[0], fraction * self.max_size[1]])
