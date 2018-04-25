import gym_ERSLE.pyERSEnv
import gymGame
import numpy as np
import os.path as osp
import gym_ERSLE.pyERSEnv.sprites

DIR_NAME = osp.dirname(__file__)


class AmbulancePrefab(gymGame.GameObject):
    def __init__(self):
        super().__init__()
        boxCollider = gymGame.BoxCollider2D(w=0.15, h=0.15)
        visual = gymGame.SimpleSprite(
            gym_ERSLE.pyERSEnv.sprites.ambulance, w=0.15, h=0.15)
        amb = gym_ERSLE.pyERSEnv.Ambulance()
        amb.state = gym_ERSLE.pyERSEnv.Ambulance.State.Idle
        amb.drivingSpeed = 30.0
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
        boxCollider = gymGame.BoxCollider2D(w=0.25, h=0.25)
        visual = gymGame.SimpleSprite(
            gym_ERSLE.pyERSEnv.sprites.hospital, w=0.25, h=0.25, static=True)
        h = gym_ERSLE.pyERSEnv.Hospital()
        self.addComponent(boxCollider)
        self.addComponent(h)
        self.addComponent(visual)
        self.name = 'Hospital'


class BasePrefab(gymGame.GameObject):
    def __init__(self):
        super().__init__()
        boxCollider = gymGame.BoxCollider2D(w=0.25, h=0.25)
        visual = gymGame.SimpleSprite(
            gym_ERSLE.pyERSEnv.sprites.base, w=0.25, h=0.25, static=True)
        visual_level = gymGame.SimpleSprite(
            gym_ERSLE.pyERSEnv.sprites.base_level, w=0.25, h=0.25)
        visual_level.tag = 'level'
        b = gym_ERSLE.pyERSEnv.Base()
        b.initialAllocationPercentage = 100
        b.spawnPointOffset = np.array([0.12, 0, 0])
        self.addComponent(boxCollider)
        self.addComponent(b)
        self.addComponent(visual)
        self.addComponent(visual_level)
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
        blip = gym_ERSLE.pyERSEnv.Blip()
        drr._isEnabled = False
        blip._isEnabled = False
        rg.requestsPerHour = 3
        rg.width = 4
        rg.height = 4
        self.addComponent(rg)
        self.addComponent(drr)
        self.addComponent(blip)
        self.name = 'Requests Generator'


class MapRequestsGeneratorPrefab(gymGame.GameObject):
    def __init__(self):
        super().__init__()
        rg = gym_ERSLE.pyERSEnv.MapBasedRequestGenerator()
        rg.width = 14
        rg.height = 10
        self.addComponent(rg)
        self.name = "Map Requests Generator"


class RequestPrefab(gymGame.GameObject):
    def __init__(self):
        super().__init__()
        boxCollider = gymGame.BoxCollider2D(w=0.15, h=0.15)
        visual = gymGame.SimpleSprite(
            gym_ERSLE.pyERSEnv.sprites.requestOld, w=0.15, h=0.15)
        visual.tag = 'sprite_request_old'
        visual2 = gymGame.SimpleSprite(
            gym_ERSLE.pyERSEnv.sprites.requestNew, w=0.15, h=0.15)
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
        rp.maximumRequests = 100
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
        g.simulatedKmsPerUnit = 3
        g.simulatedSecondsPerFrame = 60
        visual = gymGame.SimpleSprite(
            gym_ERSLE.pyERSEnv.sprites.clock, w=1, h=1)
        self.addComponent(g)
        self.addComponent(visual)
        self.name = 'Time Keeper'


class CameraPrefab(gymGame.GameObject):
    def __init__(self):
        super().__init__()
        surface = gymGame.Camera.createRenderingSurface([400, 300])
        cam = gymGame.Camera(renderingSurface=surface, fov=[14, 10])
        self.addComponent(cam)
        self.name = 'Main Camera'
