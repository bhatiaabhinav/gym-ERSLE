import gym_ERSLE.pyERSEnv
import gymGame
import numpy as np
import os.path as osp
import gym_ERSLE.pyERSEnv.sprites

DIR_NAME = osp.dirname(__file__)

class AmbulancePrefab(gymGame.GameObject):
    def __init__(self):
        super().__init__()
        boxCollider = gymGame.BoxCollider2D(w=0.3, h=0.3)
        visual = gymGame.SimpleSprite(gym_ERSLE.pyERSEnv.sprites.ambulance, w=0.3, h=0.3)
        amb = gym_ERSLE.pyERSEnv.Ambulance()
        amb.state = gym_ERSLE.pyERSEnv.Ambulance.State.Idle
        amb.drivingSpeed = 60.0
        amb.kmsPerLitre = 10.0
        amb.minutesAtRequestSite = 0
        amb.minutesAtHospital = 0
        self.addComponent(boxCollider)
        self.addComponent(amb)
        self.addComponent(visual)
        self.name = 'Ambulance'

class HospitalPrefab(gymGame.GameObject):
    def __init__(self):
        super().__init__()
        boxCollider = gymGame.BoxCollider2D(w=0.4, h=0.4)
        visual = gymGame.SimpleSprite(gym_ERSLE.pyERSEnv.sprites.hospital, w=0.4, h=0.4, static=True)
        h = gym_ERSLE.pyERSEnv.Hospital()
        self.addComponent(boxCollider)
        self.addComponent(h)
        self.addComponent(visual)
        self.name = 'Hospital'

class BasePrefab(gymGame.GameObject):
    def __init__(self):
        super().__init__()
        boxCollider = gymGame.BoxCollider2D(w=0.6, h=0.6)
        visual = gymGame.SimpleSprite(gym_ERSLE.pyERSEnv.sprites.base, w=0.6, h=0.6, static=True)
        b = gym_ERSLE.pyERSEnv.Base()
        b.initialAllocationPercentage = 100
        b.spawnPointOffset = np.array([0.25, 0, 0])
        self.addComponent(boxCollider)
        self.addComponent(b)
        self.addComponent(visual)
        self.name = 'Base'

class BasesInitializerPrefab(gymGame.GameObject):
    def __init__(self):
        super().__init__()
        bi = gym_ERSLE.pyERSEnv.BasesInitializer()
        bi.bases = []
        self.addComponent(bi)
        self.name = 'Bases Initializer'

class RequestsGeneratorPrefab(gymGame.GameObject):
    def __init__(self):
        super().__init__()
        rg = gym_ERSLE.pyERSEnv.RequestsGenerator()
        drr = gym_ERSLE.pyERSEnv.DynamicRequestRate()
        drr._isEnabled = False
        rg.requestsPerHour = 3
        rg.width = 4
        rg.height = 4
        self.addComponent(rg)
        self.addComponent(drr)
        self.name = 'Requests Generator'

class RequestPrefab(gymGame.GameObject):
    def __init__(self):
        super().__init__()
        boxCollider = gymGame.BoxCollider2D(w=0.25, h=0.25)
        visual = gymGame.SimpleSprite(gym_ERSLE.pyERSEnv.sprites.requestOld, w=0.25, h=0.25)
        visual.tag = 'sprite_request_old'
        visual2 = gymGame.SimpleSprite(gym_ERSLE.pyERSEnv.sprites.requestNew, w=0.25, h=0.25)
        visual2.tag = 'sprite_request_new'
        visual._isEnabled = False
        r = gym_ERSLE.pyERSEnv.Request()
        self.addComponent(boxCollider)
        self.addComponent(r)
        self.addComponent(visual)
        self.addComponent(visual2)
        self.name = 'Request'

class RequestsPoolPrefab(gymGame.GameObject):
    def __init__(self):
        super().__init__()
        rp = gym_ERSLE.pyERSEnv.RequestsPool()
        rp.maximumRequests = 30
        rp.stashPoint = np.array([-100, -100, 0])
        rp.requestPrefab = RequestPrefab
        self.addComponent(rp)
        self.name = 'Requests Pool'

class ERSManagerPrefab(gymGame.GameObject):
    def __init__(self):
        super().__init__()
        ersm = gym_ERSLE.pyERSEnv.ERSManager()
        ersm.AMBULANCE_COUNT = 18
        ersm.ambulancePrefab = AmbulancePrefab
        self.addComponent(ersm)
        self.name = 'ERS Manager'

class TimeKeeperPrefab(gymGame.GameObject):
    def __init__(self):
        super().__init__()
        g = gym_ERSLE.pyERSEnv.TimeKeeper()
        g.simulatedKmsPerUnit = 12
        g.simulatedSecondsPerFrame = 60
        visual = gymGame.SimpleSprite(gym_ERSLE.pyERSEnv.sprites.clock, w=0.5, h=0.5)
        self.addComponent(g)
        self.addComponent(visual)
        self.name = 'Time Keeper'

class CameraPrefab(gymGame.GameObject):
    def __init__(self):
        super().__init__()
        surface = gymGame.Camera.createRenderingSurface(gym_ERSLE.pyERSEnv.resolution)
        cam = gymGame.Camera(renderingSurface= surface, fov=[14, 10])
        cam._isEnabled = False
        self.addComponent(cam)
        self.name = 'Main Camera'