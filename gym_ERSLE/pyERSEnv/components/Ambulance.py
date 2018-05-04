from enum import Enum
import gymGame
import numpy as np
import gym_ERSLE.pyERSEnv


class Ambulance(gymGame.GameComponent):
    treat_transit_to_base_as_busy = True

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
        self.currentRequest = None  # type: gym_ERSLE.pyERSEnv.Request
        self.currentBase = None  # type: gym_ERSLE.pyERSEnv.Base
        self.currentHospital = None  # type: gym_ERSLE.pyERSEnv.Hospital
        self.state = Ambulance.State.Idle
        self.ID = 0
        self._secondsSpentAtHospital = 0
        self._secondsSpentAtRequestSite = 0
        self.ersManager = None  # type: gym_ERSLE.pyERSEnv.ERSManager
        self.travel_time_estimator = None

    def awake(self):
        ersManagerGO = self.gameObject.scene.findObjectByName(
            'ERS Manager')  # type: gymGame.GameObject
        self.ersManager = ersManagerGO.getComponent(
            gym_ERSLE.pyERSEnv.ERSManager)  # type: gym_ERSLE.pyERSEnv.ERSManager

        timeKeeperGO = self.gameObject.scene.findObjectByName(
            'Time Keeper')  # type: gymGame.GameObject
        self.timeKeeper = timeKeeperGO.getComponent(
            gym_ERSLE.pyERSEnv.TimeKeeper)  # type: gym_ERSLE.pyERSEnv.TimeKeeper

        self.ID = self.ersManager.registerAmbulance(self)
        # print('Registered Ambulance with ID {0}'.format(self.ID))

        self._set_driving_speed(self.drivingSpeed)

    def _compute_move_per_frame_from_driving_speed(self):
        self.movePerFrame = self.drivingSpeed / self.timeKeeper.simulatedKmsPerUnit
        self.movePerFrame /= 60 * 60
        self.movePerFrame *= self.timeKeeper.simulatedSecondsPerFrame

    def atBase(self):
        return self.currentBase is not None and self.gameObject.collider2D.isTouching(self.currentBase.gameObject.collider2D)

    def atRequest(self):
        return self.currentRequest is not None and self.gameObject.collider2D.isTouching(self.currentRequest.gameObject.collider2D)

    def atHospital(self):
        return self.currentHospital is not None and self.gameObject.collider2D.isTouching(self.currentHospital.gameObject.collider2D)

    def moveTowards(self, position):
        diff = position - self.gameObject.position
        norm = np.sqrt(diff.dot(diff))
        if norm > self.movePerFrame:
            diff = diff * self.movePerFrame / norm
        self.gameObject.move(diff)

    def norm_sqaured(self, p):
        return p.dot(p)

    def findNearestHospital(self):
        return self.ersManager.hospitals[self.ersManager.nearest_hospitals([self.gameObject.position])[0][0]]

    def update(self):

        if self.state == Ambulance.State.Idle:
            if self.relocationOrder:
                self._set_state(Ambulance.State.Relocating)
                self.relocationOrder = False
            elif not self.atBase():
                self.moveTowards(self.currentBase.gameObject.position)

        elif self.state == Ambulance.State.InTransitToBase:
            if self.relocationOrder:
                self._set_state(Ambulance.State.Relocating)
                self.relocationOrder = False
            elif self.atBase():
                # print("Reached Base")
                self._set_state(Ambulance.State.Idle)
            else:
                self.moveTowards(self.currentBase.gameObject.position)

        elif self.state == Ambulance.State.Relocating:
            if self.atBase():
                # print("Reached Base")
                self._set_state(Ambulance.State.Idle)
            else:
                self.moveTowards(self.currentBase.gameObject.position)

        elif self.state == Ambulance.State.InTransitToRequest:
            if self.atRequest():
                self._set_state(Ambulance.State.WaitingAtRequestSite)
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
                self._set_state(Ambulance.State.WaitingAtHospital)
                self._secondsSpentAtHospital = 0
                self.ersManager.markAsReachedHospital(self.currentRequest)
                self.currentRequest = None
            else:
                self.moveTowards(self.currentHospital.gameObject.position)

        elif self.state == Ambulance.State.WaitingAtHospital:
            self._secondsSpentAtHospital += self.timeKeeper.simulatedSecondsPerFrame
            if self._secondsSpentAtHospital >= self.minutesAtHospital:
                self.currentRequest = None
                self._set_state(Ambulance.State.InTransitToBase)
                self.currentHospital = None

        elif self.state == Ambulance.State.WaitingAtRequestSite:
            self._secondsSpentAtRequestSite += self.timeKeeper.simulatedSecondsPerFrame
            if self._secondsSpentAtRequestSite >= self.minutesAtRequestSite:
                self._set_state(Ambulance.State.InTransitToHospital)

    def assignBase(self, b):
        if self.currentBase is not None and self.currentBase != b:
            self.relocationOrder = True
            # if not self.isBusy():
            #     self.relocationOrder = False
            #     self.state = Ambulance.State.Relocating
        self.currentBase = b

    def isBusy(self):
        # and self.state != Ambulance.State.InTransitToBase
        if Ambulance.treat_transit_to_base_as_busy:
            return self.state != Ambulance.State.Idle
        else:
            return not(self.state == Ambulance.State.Idle or self.state == Ambulance.State.InTransitToBase)

    def dispatch(self, r):
        if not self.isBusy():
            self.currentRequest = r
            self._set_state(Ambulance.State.InTransitToRequest)
        else:
            print('Invalid dispatch request!!! The ambulance is busy right now')

    def _set_state(self, state):
        self.state = state
        self._set_speed_according_to_travel_time()

    def _set_speed_according_to_travel_time(self):
        if self.travel_time_estimator is not None:
            destination_map = {
                Ambulance.State.Idle: self.currentBase.gameObject.position,
                Ambulance.State.InTransitToBase: self.currentBase.gameObject.position,
                Ambulance.State.InTransitToHospital: self.currentHospital.gameObject.position,
                Ambulance.State.InTransitToRequest: self.currentRequest.gameObject.position,
                Ambulance.State.Relocating: self.currentBase.gameObject.position,
                Ambulance.State.WaitingAtHospital: None,
                Ambulance.State.WaitingAtRequestSite: None
            }
            destination = destination_map[self.state]
            if destination is not None:
                cur_position = self.gameObject.position
                travel_time_minutes = self.travel_time_estimator(
                    [cur_position[0], cur_position[1], destination[0], destination[1]])
                travel_time_hours = travel_time_minutes / 60
                distance_unity_units = np.sqrt(
                    self.norm_sqaured(cur_position - destination))
                distance_kms = self.timeKeeper.simulatedKmsPerUnit * distance_unity_units
                drivingSpeed = distance_kms / travel_time_hours
                self._set_driving_speed(drivingSpeed)
        else:
            # leave it default
            pass

    def _set_driving_speed(self, speed_kph):
        self.drivingSpeed = speed_kph
        # print("Driving speed = {0} kph".format(self.drivingSpeed))
        self._compute_move_per_frame_from_driving_speed()
