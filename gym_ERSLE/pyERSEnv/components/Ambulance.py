from enum import Enum
import gymGame
import numpy as np
import gym_ERSLE.pyERSEnv

class Ambulance(gymGame.GameComponent):

    class State(Enum):
        Idle = 0
        InTransitToRequest = 1
        WaitingAtRequestSite = 2
        InTransitToHospital = 3
        WaitingAtHospital = 4
        InTransitToBase = 5
        Relocating = 6

    def __init__(self):
        super().__init__()
        self.relocationOrder = False
        self.drivingSpeed = 60.
        self.kmsPerLitre = 10.
        self.minutesAtRequestSite = 0.
        self.minutesAtHospital = 0.
        self.movePerFrame = 0.
        self.currentRequest = None # type: gym_ERSLE.pyERSEnv.Request
        self.currentBase = None # type: gym_ERSLE.pyERSEnv.Base
        self.currentHospital = None # type: gym_ERSLE.pyERSEnv.Hospital
        self.state = Ambulance.State.Idle
        self.ID = 0
        self._secondsSpentAtHospital = 0
        self._secondsSpentAtRequestSite = 0
        self.ersManager = None # type: gym_ERSLE.pyERSEnv.ERSManager

    def awake(self):
        ersManagerGO = self.gameObject.scene.findObjectByName('ERS Manager') # type: gymGame.GameObject
        self.ersManager = ersManagerGO.getComponent(gym_ERSLE.pyERSEnv.ERSManager) # type: gym_ERSLE.pyERSEnv.ERSManager

        timeKeeperGO = self.gameObject.scene.findObjectByName('Time Keeper') # type: gymGame.GameObject
        self.timeKeeper = timeKeeperGO.getComponent(gym_ERSLE.pyERSEnv.TimeKeeper) # type: gym_ERSLE.pyERSEnv.TimeKeeper
        
        self.ID = self.ersManager.registerAmbulance(self)
        #print('Registered Ambulance with ID {0}'.format(self.ID))

    def atBase(self):
        return self.currentBase is not None and self.gameObject.collider2D.isTouching(self.currentBase.gameObject.collider2D)

    def atRequest(self):
        return self.currentRequest is not None and self.gameObject.collider2D.isTouching(self.currentRequest.gameObject.collider2D)

    def atHospital(self):
        return self.currentHospital is not None and self.gameObject.collider2D.isTouching(self.currentHospital.gameObject.collider2D)

    def moveTowards(self, position):
        diff = position - self.gameObject.position
        norm = np.linalg.norm(diff)
        if norm > self.movePerFrame:
            diff = diff * self.movePerFrame / norm
        self.gameObject.move(diff)

    def findNearestHospital(self):
        distances = [np.linalg.norm(self.gameObject.position - h.gameObject.position) for h in self.ersManager.hospitals]
        return self.ersManager.hospitals[np.argmin(distances)]

    def update(self):
        self.movePerFrame = self.drivingSpeed / self.timeKeeper.simulatedKmsPerUnit
        self.movePerFrame /= 60*60
        self.movePerFrame *= self.timeKeeper.simulatedSecondsPerFrame

        if self.state == Ambulance.State.Idle:
            if self.relocationOrder:
                self.state = Ambulance.State.Relocating
                self.relocationOrder = False
            elif not self.atBase():
                self.moveTowards(self.currentBase.gameObject.position)

        elif self.state == Ambulance.State.InTransitToBase:
            if self.relocationOrder:
                self.state = Ambulance.State.Relocating
                self.relocationOrder = False
            elif self.atBase():
                #print("Reached Base")
                self.state = Ambulance.State.Idle
            else:
                self.moveTowards(self.currentBase.gameObject.position)

        elif self.state == Ambulance.State.Relocating:
            if self.atBase():
                #print("Reached Base")
                self.state = Ambulance.State.Idle
            else:
                self.moveTowards(self.currentBase.gameObject.position)
        
        elif self.state == Ambulance.State.InTransitToRequest:
            if self.atRequest():
                self.state = Ambulance.State.WaitingAtRequestSite
                self._secondsSpentAtRequestSite = 0
                self.currentRequest.gameObject.setParent(self.gameObject)
                self.ersManager.markAsServed(self.currentRequest)
                self.currentHospital = self.findNearestHospital()
                if self.currentHospital is None:
                    print("There are no hospitals!!")
            else:
                self.moveTowards(self.currentRequest.gameObject.position)

        elif self.state == Ambulance.State.InTransitToHospital:
            if self.atHospital():
                self.state = Ambulance.State.WaitingAtHospital
                self._secondsSpentAtHospital = 0
                self.ersManager.markAsReachedHospital(self.currentRequest)
                self.currentRequest = None
            else:
                self.moveTowards(self.currentHospital.gameObject.position)

        elif self.state == Ambulance.State.WaitingAtHospital:
            self._secondsSpentAtHospital += self.timeKeeper.simulatedSecondsPerFrame
            if self._secondsSpentAtHospital >= self.minutesAtHospital:
                self.currentRequest = None
                self.state = Ambulance.State.InTransitToBase
                self.currentHospital = None

        elif self.state == Ambulance.State.WaitingAtRequestSite:
            self._secondsSpentAtRequestSite += self.timeKeeper.simulatedSecondsPerFrame
            if self._secondsSpentAtRequestSite >= self.minutesAtRequestSite:
                self.state = Ambulance.State.InTransitToHospital


    def assignBase(self, b):
        if self.currentBase is not None and self.currentBase != b:
            self.relocationOrder = True
            if not self.isBusy():
                self.relocationOrder = False
                self.state = Ambulance.State.Relocating
        self.currentBase = b

    def isBusy(self):
        return self.state != Ambulance.State.Idle and self.state != Ambulance.State.InTransitToBase

    def dispatch(self, r):
        if not self.isBusy():
            self.currentRequest = r
            self.state = Ambulance.State.InTransitToRequest
        else:
            print('Invalid dispatch request!!! The ambulance is busy right now')