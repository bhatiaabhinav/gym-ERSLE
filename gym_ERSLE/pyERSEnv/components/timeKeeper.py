import gymGame
import gym_ERSLE.pyERSEnv
import random
import math


class TimeKeeper(gymGame.GameComponent):
    def __init__(self):
        super().__init__()
        self.simulatedKmsPerUnit = 12
        self.simulatedSecondsPerFrame = 60
        self.SECONDS_IN_A_DAY = 24 * 60 * 60
        self.seconds = 0
        self.minutes = 0.
        self.secondsInCurrentDay = 0
        self.minutesInCurrentDay = 0.
        self.hoursInCurrentDay = 0.

    def awake(self):
        self.sprite = self.gameObject.getComponent(
            gymGame.SimpleSprite)  # type: gymGame.SimpleSprite

    def start(self):
        self.seconds = 0
        self.minutes = 0.
        self.secondsInCurrentDay = 0
        self.minutesInCurrentDay = 0.
        self.hoursInCurrentDay = 0.
        self.sprite.setRotation(0)

    def update(self):
        self.seconds += self.simulatedSecondsPerFrame
        self.minutes = float(self.seconds) / 60
        self.secondsInCurrentDay = int(self.seconds % self.SECONDS_IN_A_DAY)
        self.minutesInCurrentDay = float(self.secondsInCurrentDay) / 60
        self.hoursInCurrentDay = float(self.minutesInCurrentDay) / 60
        if int(self.minutesInCurrentDay) % 15 == 0:
            self.sprite.setRotation(-self.minutesInCurrentDay * 2 * math.pi / 1440)

    def getTimeOfDayAsFractionOfDayPassed(self):
        return self.secondsInCurrentDay / float(self.SECONDS_IN_A_DAY)

    def getTimeOfDayAsPointOnCircle(self):
        angle = self.getTimeOfDayAsFractionOfDayPassed() * 2 * math.pi
        return (math.sin(angle), math.cos(angle))
