from typing import List
import gymGame
import gym_ERSLE.pyERSEnv

class BasesInitializer(gymGame.GameComponent):

    def __init__(self):
        super().__init__()
        self.bases = [] # type: List[gymGame.GameObject]

    def awake(self):
        for bgo in self.bases:
            b = bgo.getComponent(gym_ERSLE.pyERSEnv.Base) # type: gym_ERSLE.pyERSEnv.Base
            b.register()