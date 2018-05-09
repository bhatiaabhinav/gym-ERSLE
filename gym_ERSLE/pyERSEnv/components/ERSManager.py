import gym_ERSLE.pyERSEnv
import gymGame
import numpy as np
from typing import List, Set  # noqa: F401


class ERSManager(gymGame.GameComponent):

    def __init__(self):
        super().__init__()
        self.AMBULANCE_COUNT = 18
        self.bases = []  # type: List[gym_ERSLE.pyERSEnv.Base]
        self.ambulances = []  # type: List[gym_ERSLE.pyERSEnv.Ambulance]
        self.hospitals = []  # type: List[gym_ERSLE.pyERSEnv.Hospital]
        self.unservedRequests = []  # type: List[gym_ERSLE.pyERSEnv.Request]
        self.beingServed = set()  # type: Set[gym_ERSLE.pyERSEnv.Request]
        # type: Set[gym_ERSLE.pyERSEnv.Request]
        self.beingTransportedToHospital = set()
        self.ambulancePrefab = None
        self.requestsServedInThisFrameTimes = []
        self.blipRequestsServedInThisFrameTimes = []
        self.requestsReceivedInThisFrame = []  # type: List[gym_ERSLE.pyERSEnv.Request]

    def awake(self):
        for i in range(self.AMBULANCE_COUNT):
            self.gameObject.scene.instantiate(self.ambulancePrefab)

    def registerBase(self, b):
        self.bases.append(b)
        return len(self.bases) - 1

    def registerAmbulance(self, a):
        self.ambulances.append(a)
        return len(self.ambulances) - 1

    def registerHospital(self, h):
        self.hospitals.append(h)
        return len(self.hospitals) - 1

    def registerRequest(self, r):
        self.unservedRequests.append(r)
        self.requestsReceivedInThisFrame.append(r)

    def markAsServed(self, r):
        r.informAmbulanceArrived()
        self.beingServed.remove(r)
        self.beingTransportedToHospital.add(r)
        self.requestsServedInThisFrameTimes.append(r.servedIn)
        if r.is_part_of_blip:
            self.blipRequestsServedInThisFrameTimes.append(r.servedIn)

    def markAsReachedHospital(self, r):
        r.informReachedHospital()
        self.beingTransportedToHospital.remove(r)
        r.destroy()

    def _normalizedAllocation(self, unNormalizedAllocation):
        unNormalizedAllocation = np.array(unNormalizedAllocation)
        if any(unNormalizedAllocation > 1) or any(unNormalizedAllocation < 0):
            raise ValueError('Target allocation must be fraction of ambulances on each base. Each item in array should be between 0 and 1. Got array {0}'.format(
                unNormalizedAllocation))
        allocation_fraction = (
            unNormalizedAllocation * self.AMBULANCE_COUNT) / np.sum(unNormalizedAllocation)
        # print(allocation_fraction)
        allocation = np.round(allocation_fraction)
        # print(allocation)
        allocated = np.sum(allocation)
        deficit_per_base = allocation_fraction - allocation
        deficit = self.AMBULANCE_COUNT - allocated
        # print('deficit: {0}'.format(deficit))
        while deficit != 0:
            increase = int(deficit > 0) - int(deficit < 0)
            # print('increase: {0}'.format(increase))
            target_base = np.argmax(increase * deficit_per_base)
            # print('target base: {0}'.format(target_base))
            allocation[target_base] += increase
            # print('alloction: {0}'.format(allocation))
            allocated += increase
            deficit_per_base[target_base] -= increase
            deficit -= increase
            # print('deficit: {0}'.format(deficit))
        # print(allocation)
        return allocation

    def causeAllocation(self, target_allocation):
        # target_allocation = self._normalizedAllocation(target_allocation)
        if sum(target_allocation) != self.AMBULANCE_COUNT:
            raise ValueError(
                'sum of target_allocation should be same as num_ambs')
        current_allocation = [len(b.allocatedAmbulances) for b in self.bases]
        change = (np.asarray(target_allocation) -
                  np.asarray(current_allocation)).tolist()
        assert(sum(change) == 0)
        change = [{'base': i, 'change': change[i]}
                  for i in range(len(self.bases))]
        largest_sources = sorted(change, key=lambda item: item['change'])
        largest_gainers = sorted(
            change, key=lambda item: item['change'], reverse=True)
        ls_index = 0
        lg_index = 0
        while max(ls_index, lg_index) < len(self.bases):
            while largest_sources[ls_index]['change'] < 0 and largest_gainers[lg_index]['change'] > 0:
                src = largest_sources[ls_index]['base']
                dst = largest_gainers[lg_index]['base']
                self.relocateAnAmbulance(self.bases[src], self.bases[dst])
                largest_sources[ls_index]['change'] += 1
                largest_gainers[lg_index]['change'] -= 1
            if largest_sources[ls_index]['change'] == 0:
                ls_index += 1
            if largest_gainers[lg_index]['change'] == 0:
                lg_index += 1
        for c in change:
            assert(c['change'] == 0)

    def allocateAmbulance(self, b, a):
        if a.currentBase is None:
            # the ambulance is being allocated for the first time. Should be teleported to its first base :p
            a.gameObject.setPosition(
                b.gameObject.position + b.spawnPointOffset)
            a.state = gym_ERSLE.pyERSEnv.Ambulance.State.Idle
        if a.currentBase is not None and a.currentBase != b:
            a.currentBase.removeAmbulance(a)
        a.assignBase(b)
        b.addAmbulance(a)

    def start(self):
        ambulanceIndex = 0
        alloc = self._normalizedAllocation(
            [b.initialAllocationPercentage for b in self.bases])
        while ambulanceIndex < self.AMBULANCE_COUNT:
            for b, b_amb_count in zip(self.bases, alloc):
                for i in range(int(b_amb_count)):
                    self.allocateAmbulance(b, self.ambulances[ambulanceIndex])
                    ambulanceIndex += 1

    def norm_squared(self, p):
        return p.dot(p)

    def relocateAnAmbulance(self, frm, to):
        # print('Relocating')
        State = gym_ERSLE.pyERSEnv.Ambulance.State
        if frm != to:
            # give preference to move a going back or idle ambualance first
            eligibleAmbs = list(filter(lambda a: (a.state == State.Idle or a.state ==
                                                  State.InTransitToBase) and not a.relocationOrder, frm.allocatedAmbulances))
            if len(eligibleAmbs) == 0:
                # pick up any one (which isn't already relocating) if there is no amb which is either idle or going back:
                eligibleAmbs = list(filter(lambda a: not a.relocationOrder and a.state !=
                                           State.Relocating, frm.allocatedAmbulances))
            if len(eligibleAmbs) > 0:
                distances = [self.norm_squared(a.gameObject.position - to.gameObject.position)
                             for a in eligibleAmbs]
                amb = eligibleAmbs[np.argmin(distances)]
                self.allocateAmbulance(to, amb)

    def serveRequests(self):
        while len(self.unservedRequests) > 0:
            first = self.unservedRequests[0]
            nonBusyAmbs = list(
                filter(lambda a: not a.isBusy(), self.ambulances))
            if len(nonBusyAmbs) > 0:
                ambsDistances = [self.norm_squared(a.gameObject.position - first.gameObject.position)
                                 for a in nonBusyAmbs]
                bestAmb = nonBusyAmbs[np.argmin(ambsDistances)]
                bestAmb.dispatch(first)
                first.informAmbulanceAssigned(bestAmb)
                self.unservedRequests.pop(0)
                self.beingServed.add(first)
            else:
                break

    def update(self):
        self.requestsServedInThisFrameTimes.clear()
        self.blipRequestsServedInThisFrameTimes.clear()
        self.requestsReceivedInThisFrame.clear()
        self.serveRequests()

    def nearest_bases(self, positions, k=1, return_distance=False):
        if not hasattr(self, '_bases_kdt'):
            # print('Building bases KDT')
            from sklearn.neighbors import KDTree
            self._bases_kdt = KDTree(
                [b.gameObject.position for b in self.bases], leaf_size=1)
        return self._bases_kdt.query(positions, k=k, return_distance=return_distance)

    def nearest_hospitals(self, positions, k=1, return_distance=False):
        if not hasattr(self, '_hospitals_kdt'):
            # print('Building hospitals KDT')
            from sklearn.neighbors import KDTree
            self._hospitals_kdt = KDTree(
                [h.gameObject.position for h in self.hospitals], leaf_size=1)
        return self._hospitals_kdt.query(positions, k=k, return_distance=return_distance)
