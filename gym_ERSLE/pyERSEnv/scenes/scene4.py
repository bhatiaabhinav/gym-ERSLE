import gym_ERSLE.pyERSEnv
import gymGame
import numpy as np
from gym import spaces


class Scene4(gymGame.Scene):
    metadata = {'render.modes': ['human', 'rgb']}

    def __init__(self, discrete_state=True, discrete_action=True, decision_interval=1, dynamic=False, random_blips=True, starting_allocation=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]):
        super().__init__()
        self.discrete_state = discrete_state
        self.discrete_action = discrete_action
        self.nbases = 12
        self.nambs = 24
        self.nhospitals = 20
        self.fullRewardDeadline = 10
        self.decision_interval = decision_interval
        self.dynamic = dynamic
        self.random_blips = random_blips
        self.starting_allocation = starting_allocation
        self.nact = self.nbases * (self.nbases - 1) + 1
        if discrete_action:
            self.action_space = spaces.Discrete(self.nact)
        else:
            self.action_space = spaces.Box(0, 1, shape=[self.nbases])
        if self.discrete_state:
            self.observation_space = spaces.Box(
                0, 1, shape=self._get_observation_shape())
        else:
            self.observation_space = spaces.Box(
                0, 255, shape=self._get_observation_shape())

        self.viewer = None  # type: gym.envs.classic_control.rendering.SimpleImageViewer

    def _reset(self):

        self._destroyObjects()

        self._map_bounds = [[-7, -5], [7, 5]]
        self.fov = [14, 10]

        # type: gymGame.GameObject
        camGO = self.instantiate(gym_ERSLE.pyERSEnv.CameraPrefab)
        self.mainCamera = camGO.getComponent(
            gymGame.Camera)  # type: gymGame.Camera
        timeKeeperGO = self.instantiate(
            gym_ERSLE.pyERSEnv.TimeKeeperPrefab, np.array([6, 4, 0]))
        self.timeKeeper = timeKeeperGO.getComponent(
            gym_ERSLE.pyERSEnv.TimeKeeper)  # type: gym_ERSLE.pyERSEnv.TimeKeeper
        ersManagerGO = self.instantiate(
            gym_ERSLE.pyERSEnv.ERSManagerPrefab)  # type: gymGame.GameObject
        self.ersManager = ersManagerGO.getComponent(
            gym_ERSLE.pyERSEnv.ERSManager)  # type: gym_ERSLE.pyERSEnv.ERSManager
        self.ersManager.AMBULANCE_COUNT = self.nambs

        requestsPoolGO = self.instantiate(
            gym_ERSLE.pyERSEnv.RequestsPoolPrefab)  # type: gymGame.GameObject
        self.requestsPool = requestsPoolGO.getComponent(
            gym_ERSLE.pyERSEnv.RequestsPool)  # type: gym_ERSLE.pyERSEnv.RequestsPool

        mainRequestsGenerator = self.instantiate(
            gym_ERSLE.pyERSEnv.RequestsGeneratorPrefab)
        mainRequestsGenerator.getComponent(
            gym_ERSLE.pyERSEnv.RequestsGenerator).width = 14
        mainRequestsGenerator.getComponent(
            gym_ERSLE.pyERSEnv.RequestsGenerator).height = 10
        mainRequestsGenerator.getComponent(
            gym_ERSLE.pyERSEnv.RequestsGenerator).requestsPerHour = 2

        if self.random_blips:
            blipsGenerator = self.instantiate(gym_ERSLE.pyERSEnv.RequestsGeneratorPrefab, position=np.array([
                                              12 * self.random.random() - 6, 8 * self.random.random() - 4, 0]))
            blipsGenerator.getComponent(
                gym_ERSLE.pyERSEnv.RequestsGenerator).width = 1
            blipsGenerator.getComponent(
                gym_ERSLE.pyERSEnv.RequestsGenerator).height = 1
            blipsGenerator.getComponent(
                gym_ERSLE.pyERSEnv.RequestsGenerator).requestsPerHour = 0
            blipsGenerator.getComponent(
                gym_ERSLE.pyERSEnv.Blip)._isEnabled = True
            blipsGenerator.getComponent(
                gym_ERSLE.pyERSEnv.Blip).peak_time = self.random.random()
            # print(blipsGenerator.getComponent(gym_ERSLE.pyERSEnv.Blip).peak_time)

        bottomRightRequestsGenerator = self.instantiate(
            gym_ERSLE.pyERSEnv.RequestsGeneratorPrefab, np.array([4.55, -0.87, 0]))
        bottomRightRequestsGenerator.getComponent(
            gym_ERSLE.pyERSEnv.RequestsGenerator).requestsPerHour = 5

        if self.dynamic:
            bottomLeftRG = self.instantiate(
                gym_ERSLE.pyERSEnv.RequestsGeneratorPrefab, np.array([-3.61, -2.54, 0]))
            bottomLeftRG.getComponent(
                gym_ERSLE.pyERSEnv.RequestsGenerator).requestsPerHour = 5
            bottomLeftRG.getComponent(
                gym_ERSLE.pyERSEnv.DynamicRequestRate)._isEnabled = True
            bottomLeftRG.getComponent(
                gym_ERSLE.pyERSEnv.DynamicRequestRate).peak_time = 0.5
            bottomRightRequestsGenerator.getComponent(
                gym_ERSLE.pyERSEnv.DynamicRequestRate)._isEnabled = True
            bottomRightRequestsGenerator.getComponent(
                gym_ERSLE.pyERSEnv.DynamicRequestRate).peak_time = 0

        topLeftRequestsGenerator = self.instantiate(
            gym_ERSLE.pyERSEnv.RequestsGeneratorPrefab, np.array([-2.36, 2.84, 0]))
        topLeftRequestsGenerator.getComponent(
            gym_ERSLE.pyERSEnv.RequestsGenerator).requestsPerHour = 5

        basesInitializer = self.instantiate(
            gym_ERSLE.pyERSEnv.BasesInitializerPrefab)
        bases = []
        basePositions = [
            [-4.2, 2.5, 0],
            [-1.4, 2.5, 0],
            [1.4, 2.5, 0],
            [4.2, 2.5, 0],
            [-4.2, 0, 0],
            [-1.4, 0, 0],
            [1.4, 0, 0],
            [4.2, 0, 0],
            [-4.2, -2.5, 0],
            [-1.4, -2.5, 0],
            [1.4, -2.5, 0],
            [4.2, -2.5, 0]
        ]
        initialAllocation = self.starting_allocation
        for i in range(self.nbases):
            bases.append(self.instantiate(
                gym_ERSLE.pyERSEnv.BasePrefab, np.array(basePositions[i])))
            bases[i].getComponent(
                gym_ERSLE.pyERSEnv.Base).initialAllocationPercentage = initialAllocation[i]
        basesInitializer.getComponent(
            gym_ERSLE.pyERSEnv.BasesInitializer).bases = bases

        hospitalPositions = [
            [-4.67, 3, 0],
            [-2.33, 3, 0],
            [0, 3, 0],
            [2.33, 3, 0],
            [4.67, 3, 0],
            [-4.67, 1, 0],
            [-2.33, 1, 0],
            [0, 1, 0],
            [2.33, 1, 0],
            [4.67, 1, 0],
            [-4.67, -1, 0],
            [-2.33, -1, 0],
            [0, -1, 0],
            [2.33, -1, 0],
            [4.67, -1, 0],
            [-4.67, -3, 0],
            [-2.33, -3, 0],
            [0, -3, 0],
            [2.33, -3, 0],
            [4.67, -3, 0]
        ]
        for i in range(self.nhospitals):
            self.instantiate(gym_ERSLE.pyERSEnv.HospitalPrefab,
                             np.array(hospitalPositions[i]))

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

        self.obs = self._getObservation()
        return self.obs

    def _step(self, action):
        # evaluate action here:
        self._act(action)
        reward = 0
        blip_reward = 0
        request_heat_map = None
        steps = 0
        for i in range(self.decision_interval):
            super()._step(action)
            reward += self._getReward()
            info = self._getInfo()
            blip_reward += info['blip_reward']
            info['blip_reward'] = blip_reward
            obs = self._getObservation(transform=False)
            steps += 1
            current_request_heat_map = obs[0:self.nbases] if self.discrete_state else obs[:, :, 0]
            if request_heat_map is None:
                request_heat_map = current_request_heat_map
            else:
                request_heat_map = request_heat_map + current_request_heat_map
            if self._getTerminal():
                break
        request_heat_map = request_heat_map / steps  # average over all the steps
        # replace the request heat map of current obs:
        if self.discrete_state:
            obs[0:self.nbases] = request_heat_map
        else:
            obs[:, :, 0] = request_heat_map
        self.obs = self._transform_obs(obs)
        return self.obs, reward, self._getTerminal(), info

    def _render(self, mode='human', close=False):
        if not close:
            if self.viewer is None:
                from gym.envs.classic_control.rendering import SimpleImageViewer
                self.viewer = SimpleImageViewer()
            if not self.discrete_state:
                obs = self.obs if mode == 'rgb' else self.mainCamera.getLatestFrame()
                self.viewer.imshow(obs)
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

    def _transform_obs(self, obs):
        if self.discrete_state:
            obs[0:self.nbases] = self._log_transform(
                obs[0:self.nbases], self.requestsPool.maximumRequests, 1, t=0.005)
            obs[self.nbases: 2 * self.nbases] = self._log_transform(
                obs[self.nbases: 2 * self.nbases], self.ersManager.AMBULANCE_COUNT, 1, t=5)
        else:
            obs[:, :, 0] = self._log_transform(
                obs[:, :, 0], self.requestsPool.maximumRequests, 255, t=0.005)
            obs[:, :, 1] = self._log_transform(
                obs[:, :, 1], self.ersManager.AMBULANCE_COUNT, 255, t=5)
            obs[:, :, 2] = 255 * obs[:, :, 2]
            assert np.all(obs <= 255)
            obs = obs.astype(np.uint8)
        return obs

    def _log_transform(self, x, max_x, max_ans, t=1):
        return max_ans * np.log(1 + x / t) / np.log(1 + max_x / t)

    def _getObservation(self, transform=True):
        if not self.discrete_state:
            # self.obs = self.mainCamera.getLatestFrame()
            shape = self._get_observation_shape()[0:2]
            mins = self.timeKeeper.getTimeOfDayAsFractionOfDayPassed()
            time_map = mins * np.ones(shape)
            requests_heat_map = self._to_heat_map(
                [r.gameObject.position for r in self.ersManager.requestsReceivedInThisFrame])
            alloc_heat_map = self._to_heat_map(
                [a.currentBase.gameObject.position for a in self.ersManager.ambulances])
            obs = np.stack([
                requests_heat_map,
                alloc_heat_map,
                time_map
            ], axis=2)
        else:
            mins = self.timeKeeper.getTimeOfDayAsFractionOfDayPassed()
            requests_heat_map = self._to_heat_map_by_base_zone(
                [r.gameObject.position for r in self.ersManager.requestsReceivedInThisFrame])
            alloc_heat_map = self._to_heat_map_by_base_zone(
                [a.currentBase.gameObject.position for a in self.ersManager.ambulances])
            obs = np.array(
                list(requests_heat_map) +
                list(alloc_heat_map) +
                [mins])
        if transform:
            obs = self._transform_obs(obs)
        assert list(obs.shape) == self._get_observation_shape(), print(
            'The shape of returned obs does not match the declared shape:\nobs.shape: {0}\ndeclared: {1}'.format(
                obs.shape, self._get_observation_shape()))
        return obs

    def _get_observation_shape(self):
        if not self.discrete_state:
            return [21, 21, 3]
        else:
            return [2 * self.nbases + 1]

    def norm_sqaured(self, p):
        return p.dot(p)

    def __to_heat_map_by_base_zone(self, positions):
        heat_map = np.zeros([len(self.ersManager.bases)])
        for p in positions:
            baseDistances = [self.norm_sqaured(
                p - b.gameObject.position) for b in self.ersManager.bases]
            closestBase = np.argmin(baseDistances)
            heat_map[closestBase] += 1
        return heat_map

    def _to_heat_map_by_base_zone(self, positions):
        heat_map = np.zeros([len(self.ersManager.bases)])
        if len(positions) > 0:
            closestBases = self.ersManager.nearest_bases(positions)[:, 0]
            for b_id in closestBases:
                heat_map[b_id] += 1
        return heat_map

    def _to_heat_map(self, positions):
        """
        Parameters
        -----------
        positions: a list of lists in [x,y,z] format
        Returns
        -------
        `Returns` an np array of shape self._get_observation_shape()[0:2]
        """
        shape = self._get_observation_shape()[0:2]
        map_resolution = shape[::-1]
        fov = self.fov
        assert len(map_resolution) == 2
        assert len(fov) == 2
        heat_map_float = np.zeros(shape)
        for p in positions:
            row = int((fov[1] / 2 - p[1]) * map_resolution[1] / fov[1])
            col = int((fov[0] / 2 + p[0]) * map_resolution[0] / fov[0])
            heat_map_float[row, col] += 1
        return heat_map_float

    def _getReward(self):
        reward = 0
        # max_reward = 0
        for t in self.ersManager.requestsServedInThisFrameTimes:
            if t <= self.fullRewardDeadline:
                reward += 1
        #     max_reward += 1  # why this clipping?? Nooooooooooooooooo
        # return reward / max_reward if max_reward > 0 else 0
        return reward

    def _getTerminal(self):
        return self.timeKeeper.minutes >= 1440

    def _getInfo(self):
        # ambs_idle, ambs_relocating, ambs_to_base, ambs_to_request, \
        #     ambs_to_hospital = 0, 0, 0, 0, 0
        # State = gym_ERSLE.pyERSEnv.Ambulance.State
        # for a in self.ersManager.ambulances:
        #     if a.state == State.Idle:
        #         ambs_idle += 1
        #     elif a.state == State.Relocating:
        #         ambs_relocating += 1
        #     elif a.state == State.InTransitToBase:
        #         ambs_to_base += 1
        #     elif a.state == State.InTransitToHospital:
        #         ambs_to_hospital += 1
        #     elif a.state == State.InTransitToRequest:
        #         ambs_to_request += 1
        # info = {
        #     'ambs_idle': ambs_idle,
        #     'ambs_relocating': ambs_relocating,
        #     'ambs_to_base': ambs_to_base,
        #     'ambs_to_request': ambs_to_request,
        #     'ambs_to_hospital': ambs_to_hospital
        # }
        # for b in self.ersManager.bases:
        #     info['base{0}'.format(b.ID)] = len(b.allocatedAmbulances)
        info = {}
        blip_reward = 0
        for t in self.ersManager.blipRequestsServedInThisFrameTimes:
            if t <= self.fullRewardDeadline:
                blip_reward += 1
        info['blip_reward'] = blip_reward
        return info
