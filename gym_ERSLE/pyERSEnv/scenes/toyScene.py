import gym_ERSLE.pyERSEnv
import gymGame
import numpy as np
from gym import spaces


class ToyScene(gymGame.Scene):
    metadata = {'render.modes': ['human']}

    def __init__(self, discrete_state=True, discrete_action=True, decision_interval=1, dynamic=False, starting_allocation=[1, 1, 3, 9, 3, 1]):
        super().__init__()
        self.discrete_state = discrete_state
        self.discrete_action = discrete_action
        self.nbases = 6
        self.nambs = 18
        self.nhospitals = 9
        self.fullRewardDeadline = 25
        self.decision_interval = decision_interval
        self.dynamic = dynamic
        self.starting_allocation = starting_allocation
        self.nact = self.nbases * (self.nbases - 1) + 1
        if discrete_action:
            self.action_space = spaces.Discrete(self.nact)
        else:
            self.action_space = spaces.Box(0, 1, shape=[self.nbases])
        if self.discrete_state:
            self.observation_space = spaces.Box(0, 1, shape=[self.nbases + 11])
        else:
            self.observation_space = spaces.Box(
                0, 255, shape=[gym_ERSLE.pyERSEnv.resolution[1], gym_ERSLE.pyERSEnv.resolution[0], 3])

        self.viewer = None  # type: gym.envs.classic_control.rendering.SimpleImageViewer

    def _reset(self):

        self._destroyObjects()

        self._map_bounds = [[-7, -5], [7, 5]]

        camGO = self.instantiate(gym_ERSLE.pyERSEnv.CameraPrefab)  # type: gymGame.GameObject
        self.mainCamera = camGO.getComponent(gymGame.Camera)  # type: gymGame.Camera
        timeKeeperGO = self.instantiate(gym_ERSLE.pyERSEnv.TimeKeeperPrefab, np.array([6, 4, 0]))
        self.timeKeeper = timeKeeperGO.getComponent(
            gym_ERSLE.pyERSEnv.TimeKeeper)  # type: gym_ERSLE.pyERSEnv.TimeKeeper
        ersManagerGO = self.instantiate(
            gym_ERSLE.pyERSEnv.ERSManagerPrefab)  # type: gymGame.GameObject
        self.ersManager = ersManagerGO.getComponent(
            gym_ERSLE.pyERSEnv.ERSManager)  # gym_ERSLE.pyERSEnv: ers.ERSManager

        requestsPoolGO = self.instantiate(
            gym_ERSLE.pyERSEnv.RequestsPoolPrefab)  # type: gymGame.GameObject
        self.requestsPool = requestsPoolGO.getComponent(
            gym_ERSLE.pyERSEnv.RequestsPool)  # type: gym_ERSLE.pyERSEnv.RequestsPool

        mainRequestsGenerator = self.instantiate(gym_ERSLE.pyERSEnv.RequestsGeneratorPrefab)
        mainRequestsGenerator.getComponent(gym_ERSLE.pyERSEnv.RequestsGenerator).width = 14
        mainRequestsGenerator.getComponent(gym_ERSLE.pyERSEnv.RequestsGenerator).height = 10
        mainRequestsGenerator.getComponent(gym_ERSLE.pyERSEnv.RequestsGenerator).requestsPerHour = 1

        bottomRightRequestsGenerator = self.instantiate(
            gym_ERSLE.pyERSEnv.RequestsGeneratorPrefab, np.array([4.55, -0.87, 0]))
        bottomRightRequestsGenerator.getComponent(
            gym_ERSLE.pyERSEnv.RequestsGenerator).requestsPerHour = 5

        if self.dynamic:
            bottomLeftRG = self.instantiate(
                gym_ERSLE.pyERSEnv.RequestsGeneratorPrefab, np.array([-3.61, -2.54, 0]))
            bottomLeftRG.getComponent(gym_ERSLE.pyERSEnv.RequestsGenerator).requestsPerHour = 5
            bottomLeftRG.getComponent(gym_ERSLE.pyERSEnv.DynamicRequestRate)._isEnabled = True
            bottomLeftRG.getComponent(gym_ERSLE.pyERSEnv.DynamicRequestRate).peak_time = 0.5
            bottomRightRequestsGenerator.getComponent(
                gym_ERSLE.pyERSEnv.DynamicRequestRate)._isEnabled = True
            bottomRightRequestsGenerator.getComponent(
                gym_ERSLE.pyERSEnv.DynamicRequestRate).peak_time = 0

        self.instantiate(gym_ERSLE.pyERSEnv.RequestsGeneratorPrefab, np.array([-2.36, 2.84, 0]))

        basesInitializer = self.instantiate(gym_ERSLE.pyERSEnv.BasesInitializerPrefab)
        bases = []
        basePositions = [
            [-4.49, 2.01, 0],
            [-0.04, 1.96, 0],
            [5.036, 2.1735, 0],
            [-4.422, -1.5255, 0],
            [1.03, -2.32, 0],
            [5.153, -1.1977, 0]
        ]
        initialAllocation = self.starting_allocation
        for i in range(self.nbases):
            bases.append(self.instantiate(
                gym_ERSLE.pyERSEnv.BasePrefab, np.array(basePositions[i])))
            bases[i].getComponent(
                gym_ERSLE.pyERSEnv.Base).initialAllocationPercentage = initialAllocation[i]
        basesInitializer.getComponent(gym_ERSLE.pyERSEnv.BasesInitializer).bases = bases

        hospitalPositions = [
            [3.655, -0.004, 0],
            [-2.994, 0.020, 0],
            [0.12, 3.72, 0],
            [0.120, -3.281, 0],
            [0, 0, 0],
            [4.006, 3.531, 0],
            [4.310, -3.352, 0],
            [-3.416, -3.469, 0],
            [-3.416, 3.602, 0]
        ]
        for i in range(self.nhospitals):
            self.instantiate(gym_ERSLE.pyERSEnv.HospitalPrefab, np.array(hospitalPositions[i]))

        gymGame.set_execution_order([
            gym_ERSLE.pyERSEnv.TimeKeeper,
            gym_ERSLE.pyERSEnv.ERSManager,
            gym_ERSLE.pyERSEnv.Base,
            gym_ERSLE.pyERSEnv.BasesInitializer,
            gym_ERSLE.pyERSEnv.Hospital,
            gym_ERSLE.pyERSEnv.Ambulance,
            gym_ERSLE.pyERSEnv.RequestsPool,
            gym_ERSLE.pyERSEnv.DynamicRequestRate,
            gym_ERSLE.pyERSEnv.RequestsGenerator,
            gymGame.SimpleSprite,
            gymGame.Camera
        ])

        super()._reset()

        return self._getObservation()  # return obs here

    def _step(self, action):
        # evaluate action here:
        self._act(action)
        reward = 0
        for i in range(self.decision_interval):
            super()._step(action)
            reward += self._getReward()
            if self._getTerminal():
                break
        return self._getObservation(), reward, self._getTerminal(), self._getInfo()

    def _render(self, mode='human', close=False):
        if not close:
            if self.viewer is None:
                from gym.envs.classic_control.rendering import SimpleImageViewer
                self.viewer = SimpleImageViewer()
            if not self.discrete_state:
                self.viewer.imshow(self.obs)
            else:
                obs = self.mainCamera.getLatestFrame()
                self.viewer.imshow(obs)
        else:
            if self.viewer is not None and self.viewer.isopen:
                self.viewer.close()
                self.viewer = None

    def _act(self, action):
        if self.discrete_action:
            if action > 0:
                b = len(self.ersManager.bases)
                dest = (action - 1) // (b - 1)
                src = (action - 1) % (b - 1)
                if src >= dest:
                    src += 1
                frm = self.ersManager.bases[src]
                to = self.ersManager.bases[dest]
                self.ersManager.relocateAnAmbulance(frm, to)
            else:
                # noop
                pass
        else:
            self.ersManager.causeAllocation(action)

    def _getObservation(self):
        if not self.discrete_state:
            self.obs = self.mainCamera.getLatestFrame()
        else:
            alloc = np.array([len(b.allocatedAmbulances)
                              for b in self.ersManager.bases]) / self.ersManager.AMBULANCE_COUNT
            ur = len(self.ersManager.unservedRequests) / self.requestsPool.maximumRequests
            bs = len(self.ersManager.beingServed) / self.requestsPool.maximumRequests
            btth = len(self.ersManager.beingTransportedToHospital) / \
                self.requestsPool.maximumRequests
            rsitf = len(self.ersManager.requestsServedInThisFrame) / \
                self.requestsPool.maximumRequests
            mins = self.timeKeeper.getTimeOfDayAsPointOnCircle()
            ambs_idle, ambs_relocating, ambs_to_base, ambs_to_request, ambs_to_hospital = 0, 0, 0, 0, 0
            State = gym_ERSLE.pyERSEnv.Ambulance.State
            for a in self.ersManager.ambulances:
                if a.state == State.Idle:
                    ambs_idle += 1 / self.ersManager.AMBULANCE_COUNT
                elif a.state == State.Relocating:
                    ambs_relocating += 1 / self.ersManager.AMBULANCE_COUNT
                elif a.state == State.InTransitToBase:
                    ambs_to_base += 1 / self.ersManager.AMBULANCE_COUNT
                elif a.state == State.InTransitToHospital:
                    ambs_to_hospital += 1 / self.ersManager.AMBULANCE_COUNT
                elif a.state == State.InTransitToRequest:
                    ambs_to_request += 1 / self.ersManager.AMBULANCE_COUNT
            self.obs = np.array(list(alloc) +
                                [ambs_idle, ambs_relocating, ambs_to_base, ambs_to_request, ambs_to_hospital] +
                                [ur, bs, btth, rsitf, mins[0], mins[1]])
        return self.obs

    def _getReward(self):
        reward = 0
        for r in self.ersManager.requestsServedInThisFrame:
            if r.servedIn < self.fullRewardDeadline:
                reward += 1
            elif r.servedIn < 2 * self.fullRewardDeadline:
                reward += 0.5
            else:
                reward += 0
        return reward

    def _getTerminal(self):
        return self.timeKeeper.minutes >= 1440

    def _getInfo(self):
        ambs_idle, ambs_relocating, ambs_to_base, ambs_to_request, ambs_to_hospital = 0, 0, 0, 0, 0
        State = gym_ERSLE.pyERSEnv.Ambulance.State
        for a in self.ersManager.ambulances:
            if a.state == State.Idle:
                ambs_idle += 1
            elif a.state == State.Relocating:
                ambs_relocating += 1
            elif a.state == State.InTransitToBase:
                ambs_to_base += 1
            elif a.state == State.InTransitToHospital:
                ambs_to_hospital += 1
            elif a.state == State.InTransitToRequest:
                ambs_to_request += 1
        info = {
            'ambs_idle': ambs_idle,
            'ambs_relocating': ambs_relocating,
            'ambs_to_base': ambs_to_base,
            'ambs_to_request': ambs_to_request,
            'ambs_to_hospital': ambs_to_hospital
        }
        for b in self.ersManager.bases:
            info['base{0}'.format(b.ID)] = len(b.allocatedAmbulances)
        return info
