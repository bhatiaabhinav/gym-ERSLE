import gym_ERSLE.pyERSEnv
import gymGame

class Hospital(gymGame.GameComponent):

    def __init__(self):
        super().__init__()
        self.ID = None # type: int

    def awake(self):
        ersManagerGO = self.gameObject.scene.findObjectByName('ERS Manager') # type: gymGame.GameObject
        self.ersManager = ersManagerGO.getComponent(gym_ERSLE.pyERSEnv.ERSManager) # type: gym_ERSLE.pyERSEnv.ERSManager
        self.ID = self.ersManager.registerHospital(self)
        #print('Registered hospital with ID {0}'.format(self.ID))