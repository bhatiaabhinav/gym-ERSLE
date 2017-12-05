import gym_ERSLE.pyERSEnv
import gymGame

class Request(gymGame.GameComponent):
    def __init__(self):
        super().__init__()
        self.servicingAmbulance = None # type: gym_ERSLE.pyERSEnv.Ambulance
        self.timeOfCreation = 0.
        self.timeOfAmnbulanceAllocation = 0.
        self.timeOfAmbulannceArrival = 0.
        self.timeOfClosure = 0.
        self.servedIn = 0.

    def awake(self):
        ers = gym_ERSLE.pyERSEnv
        ersManagerGO = self.gameObject.scene.findObjectByName('ERS Manager') # type: gymGame.GameObject
        self.ersManager = ersManagerGO.getComponent(ers.ERSManager) # type: gym_ERSLE.pyERSEnv.ERSManager

        requestsPoolGO = self.gameObject.scene.findObjectByName('Requests Pool') # type: gymGame.GameObject
        self.requestsPool = requestsPoolGO.getComponent(ers.RequestsPool) # type: gym_ERSLE.pyERSEnv.RequestsPool

        timeKeeperGO = self.gameObject.scene.findObjectByName('Time Keeper') # type: gymGame.GameObject
        self.timeKeeper = timeKeeperGO.getComponent(ers.TimeKeeper) # type: gym_ERSLE.pyERSEnv.TimeKeeper

    def age(self):
        return self.timeKeeper.minutes - self.timeOfCreation

    def reset(self):
        self.servicingAmbulance = None
        self.gameObject.setParent(self.requestsPool.gameObject)
        self.timeOfCreation = 0.
        self.timeOfAmnbulanceAllocation = 0.
        self.timeOfAmbulannceArrival = 0.
        self.timeOfClosure = 0.
        self.servedIn = 0.

    def create(self):
        self.servicingAmbulance = None
        self.timeOfCreation = self.timeKeeper.minutes
        self.register()
        #print('New request')

    def register(self):
        self.ersManager.registerRequest(self)

    def informAmbulanceAssigned(self, a):
        self.servicingAmbulance = a
        self.timeOfAmnbulanceAllocation = self.timeKeeper.minutes
        #print('Request assigned an ambulance')

    def informAmbulanceArrived(self):
        self.timeOfAmbulannceArrival = self.timeKeeper.minutes
        self.servedIn = self.timeOfAmbulannceArrival - self.timeOfCreation
        #print('Ambulance arrived at request site')

    def informReachedHospital(self):
        self.timeOfClosure = self.timeKeeper.minutes
        #print('Request reached hospital')

    def destroy(self):
        self.requestsPool.returnBack(self)
        #print('Request closed')