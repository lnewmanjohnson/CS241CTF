# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first='TestDefender', second='TestDefender'):
    """
    This function should return a list of two agents that will form the
    team, initialized using firstIndex and secondIndex as their agent
    index numbers.  isRed is True if the red team is being created, and
    will be False if the blue team is being created.

    As a potentially helpful development aid, this function can take
    additional string-valued keyword arguments ("first" and "second" are
    such arguments in the case of this function), which will come from
    the --redOpts and --blueOpts command-line arguments to capture.py.
    For the nightly contest, however, your team will be created without
    any extra arguments, so you should make sure that the default
    behavior is what you want for the nightly contest.
    """

    # The following line is an example only; feel free to change it.
    return [eval(first)(firstIndex), eval(second)(secondIndex)]


##########
# Agents #
##########

class MyAgents(CaptureAgent):
    distributionA = util.Counter()
    distributionB = util.Counter()
    particleListA = []
    particleListB = []
    isInitialized = False
    numParticles = 1000
    stats = {}


    
class TestDefender(MyAgents):

    def registerInitialState(self, gameState):

        self.PF = ParticleFilter(gameState, self.index, MyAgents.numParticles)

        CaptureAgent.registerInitialState(self, gameState)

        self.start = gameState.getAgentPosition(self.index)  # Start position

            # of the form [action, position, timeSpentInPosition]
        self.prevStats = ["Stop", [0, 0], 0]

        """
        setting team specific objects
        """

            #set team name
        if (self.index in gameState.getRedTeamIndices()):
            self.team = "red"
        else:
            self.team = "blue"

            #set defensePoint to play defense later
        if (self.team == "red"):
            self.defensePoints = [(13, 4), (13, 7), (12, 11)] #TODO verify that these are optimal positions
        else:
            self.defensePoints = [(19, 3), (18, 6), (18, 10)] 

            #create a list of form [a, b] containing the enemy indices
        self.enemyIndices = gameState.getRedTeamIndices()
        if (self.index in gameState.getRedTeamIndices()):
            self.enemyIndices = gameState.getBlueTeamIndices()


            #creating the first particleLists
        if (self.index in gameState.getRedTeamIndices()):
            enemyStartA = (30, 13)
            enemyStartB = (30, 14)
        else:
            enemyStartA = (1, 2)
            enemyStartB = (1, 1)
            #these have been verified

        i = 1
        while (i <= self.numParticles):
            MyAgents.particleListA.append(enemyStartA)
            MyAgents.particleListB.append(enemyStartB)
            i += 1

            #create the enemyDistributions array to make index to distribution conversion easier
        self.enemyDistributions = [None, None, None, None]
        if (self.team == "red"):
            self.enemyDistributions[1] = MyAgents.distributionA
            self.enemyDistributions[3] = MyAgents.distributionB
        else:
            self.enemyDistributions[0] = MyAgents.distributionA
            self.enemyDistributions[2] = MyAgents.distributionB

        self.particleLists = [None, None, None, None]
        if (self.team == "red"):
            self.particleLists[1] = MyAgents.particleListA
            self.particleLists[3] = MyAgents.particleListB
        else:
            self.particleLists[0] = MyAgents.particleListA
            self.particleLists[2] = MyAgents.particleListB

            #filling out some default stats
        MyAgents.stats["prevThreatA"] = 0
        MyAgents.stats["prevThreatB"] = 0




    def chooseAction(self, gameState):
        #raw_input()
        if (self.index == 1 or self.index == 2):
            #elapseTime for the enemy B agent
            MyAgents.particleListA = self.PF.elapseTime(gameState, MyAgents.particleListA)
        if (self.index == 0 or self.index == 3):
            #elapseTime for the enemy A agent
            MyAgents.particleListB = self.PF.elapseTime(gameState, MyAgents.particleListB)

        MyAgents.particleListA, MyAgents.distributionA, MyAgents.particleListB,  MyAgents.distributionB = self.PF.observe(gameState, MyAgents.particleListA, MyAgents.particleListB, MyAgents.distributionA, MyAgents.distributionB, MyAgents.stats)
        enemyDistributions = [None, MyAgents.distributionA, None, MyAgents.distributionB]
        target, prevThreatA, prevThreatB = self.determineTarget(gameState, MyAgents.distributionA, MyAgents.distributionB)
        MyAgents.stats["prevThreatA"] = prevThreatA
        MyAgents.stats["prevThreatB"] = prevThreatB

        if (target == "A"):
            targetDistribution = MyAgents.distributionA
        else:
            targetDistribution = MyAgents.distributionB
        probInBackCourt = 0
        zoneDistribution = [0, 0 ,0]
        for state in targetDistribution:
            # the numbers in the conditionals, 18 and 13, may need to be changed in the future to tune
            if (self.team == "red" and state[0] > 17):
                probInBackCourt += targetDistribution[state]
                if (state[1] <= 4):
                    #tests for Zone A
                    zoneDistribution[0] += targetDistribution[state]
                elif (state[1] <= 9):
                    #tests for Zone B
                    zoneDistribution[1] += targetDistribution[state]
                else:
                    #tests for Zone C
                    zoneDistribution[2] += targetDistribution[state]
            elif (self.team == "blue" and state[0] < 13):               #TODO I just did this for RED, BLUE is outdated
                if (state[1] <= 4):
                    #tests for Zone A
                    zoneDistribution[0] += targetDistribution[state]
                elif (state[1] <= 8):
                    #tests for Zone B
                    zoneDistribution[1] += targetDistribution[state]
                else:
                    #tests for Zone C
                    zoneDistribution[2] += targetDistribution[state]

        #print("probInBackCourt for ", target, " is: ", probInBackCourt)
        #TODO currently it does not know when enemy is actually in back court its done by a focal point
        if (probInBackCourt > .5):                                  
        #the strictness of these inequalities probably does not really matter
            return self.pointDefense(gameState, probInBackCourt, zoneDistribution)
        else:
            return self.chase(gameState, target)



    def chase(self, gameState, target):
        #this function just tries to run to the square where the ghost most likely is


        if (target == "A"):
            targetPos = MyAgents.distributionA.argMax()
        else:
            targetPos = MyAgents.distributionB.argMax()

        #print("running chase with target: ", target)
        #print("currently at: ", gameState.getAgentPosition(self.index))
        #print("trying to reach: ", targetPos)
        #print("PROTOCOL: chasing target ", target, " at pos: ", targetPos)
        myPos = gameState.getAgentPosition(self.index)
        bestAction = ["Stop", self.distancer.getDistance(myPos, targetPos)]
        for action in gameState.getLegalActions(self.index):
            successor = self.getSuccessor(gameState, action)
            if (successor.getAgentState(self.index).configuration.pos == targetPos and successor.getAgentState(self.index).configuration.pos[0] < 15):
                #the defender is about to eat the enemy
                if (target == "A"):
                    MyAgents.distributionA, MyAgents.particleListA = self.PF.eat(target)
                else:
                    MyAgents.distributionB, MyAgents.particleListB = self.PF.eat(target)
                return action

            if (self.distancer.getDistance(successor.getAgentState(self.index).configuration.pos, targetPos) <= bestAction[1] and successor.getAgentState(self.index).configuration.pos[0] < 15): #TODO make '16' this work for blue too
                bestAction[0] = action
                bestAction[1] = self.distancer.getDistance(successor.getAgentState(self.index).configuration.pos, targetPos)
        #print("chose to do: ", bestAction[0])
        if (self.runStallStats(bestAction[0], self.getSuccessor(gameState, bestAction[0])) == True):
            randomAction = gameState.getLegalActions(self.index)[random.randint(0, len(gameState.getLegalActions())-1)]
            self.runStallStats(randomAction, self.getSuccessor(gameState, bestAction[0]))
            return randomAction
        else:
            return bestAction[0]
        


    def pointDefense(self, gameState, probInBackCourt, zoneDistribution):
        #this function is a switch to tell the defenders how to play point defense

        #print("running assumePost with zone: ", zoneDistribution.index(max(zoneDistribution)))
        #print("trying to reach: ", self.defensePoints[zoneDistribution.index(max(zoneDistribution))])
        return self.assumePost(gameState, zoneDistribution.index(max(zoneDistribution)))
        #TODO flesh out a more nuanced transition function between posts


    def assumePost(self, gameState, postIndex):
        #this function sends the agent toward either post a, b, or c along the perimeter
        myPos = gameState.getAgentPosition(self.index)
        bestAction = ["Stop", self.distancer.getDistance(myPos, self.defensePoints[postIndex])]
        #best action is the one that gets closest to the defense point, in this case B since were in lower
        for action in gameState.getLegalActions(self.index):
            successor = self.getSuccessor(gameState, action)
            if (self.distancer.getDistance(successor.getAgentState(self.index).configuration.pos, self.defensePoints[postIndex]) < bestAction[1]):
                bestAction[0] = action
                bestAction[1] = self.distancer.getDistance(myPos, self.defensePoints[postIndex])

        #a small method to check if the agent got stuck somehow
        if (self.runStallStats(bestAction[0], self.getSuccessor(gameState, bestAction[0])) == True):
            randomAction = gameState.getLegalActions(self.index)[random.randint(0, len(gameState.getLegalActions())-1)]
            self.runStallStats(randomAction, self.getSuccessor(gameState, bestAction[0]))
            return randomAction
        else:
            return bestAction[0]


    def getSuccessor(self, gameState, action):
        """
        Finds the next successor which is a grid position (location tuple).
        """
        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()
        if pos != util.nearestPoint(pos):
            # Only half a grid position was covered
            return successor.generateSuccessor(self.index, action)
        else:
            return successor


    def determineTarget(self, gameState, distributionA, distributionB):
        #this function returns the index of the enemy most likely playing offense

        threatA = 0
        for state in distributionA:
            threatA += (1.0/(state[0]))*distributionA[state]
        #print("threatA: ", threatA)
        threatB = 0
        for state in distributionB:
            threatB += (1.0/(state[0]))*distributionB[state]
        #print("threatB: ", threatB)
        if (threatA >= threatB):
            return "A", threatA, threatB
        else:
            return "B", threatA, threatB

    def runStallStats(self, action, successor):
        # this function runs upkeep on the relevant stall stats and tries to find out 
        # if the agent is stuck (same move more than 5 times)
        #prevStats is of the form: [action, position, timeSpentInPosition]

        #print("action:", action)
        if (action == self.prevStats[0] and successor == self.prevStats[1]):
            self.prevStats[2] += 1
            if (self.prevStats[2] >= 5):
                #print("timeSpentInPosition: ", self.prevStats[2])
                return True
        else:
            self.prevStats[0] = action
            self.prevStats[1] = successor
            self.prevStats[2] = 1
        return False


class ParticleFilter():

    def __init__(self, gameState, index, numParticles):
        """
        parameters
        """

        self.numParticles = numParticles #TODO remember to change this back to some thing reasonable

        self.index = index

        self.numInitializedUniformly = 0


        """
        pre-processing some useful persistent objects
        """

            #set team name
        if (self.index in gameState.getRedTeamIndices()):
            self.team = "red"
        else:
            self.team = "blue"

            #create a list of form [a, b] containing the enemy indices
        if (self.index in gameState.getRedTeamIndices()):
            self.enemyIndices = gameState.getBlueTeamIndices()
        else:
            self.enemyIndices = gameState.getRedTeamIndices()

        self.legalPositions = []
        for x in range(0, 32):
            for y in range(0, 16):
                if not(gameState.hasWall(x,y)):
                    self.legalPositions.append((x,y))

            #NOTE: this is based off domain knowledge that they start in the opposite corner
        if (self.index in gameState.getRedTeamIndices()):
            self.enemyStartA = (30, 13)
            self.enemyStartB = (30, 14)
        else:
            self.enemyStartA = (1, 2)
            self.enemyStartB = (1, 1)

    def observe(self, gameState, particleListA, particleListB, distributionA, distributionB, stats):
        #this function takes the two noisyDistances and edits the distributions
        #NOTE: since getDistanceProb returns only 0 or 1/13 this might as well be a boolean operation
        #RETURN: this returns 4 objects, IN THIS ORDER: [particleListA, distributionA, particleListB, distributionB]
        #        it returns the distributions so they don't have to be recalculated by chooseAction() because running
        #        extra getBeliefDistribution is expensive

        selfPosition = gameState.getAgentState(self.index).getPosition()
        noisyDistances = gameState.getAgentDistances()
        distributionA = self.getBeliefDistribution(particleListA)
        distributionB = self.getBeliefDistribution(particleListB)
        enemyDistributions = [None, distributionA, None, distributionB]
        particleLists = [None, particleListA, None, particleListB]
        prevThreats = [None, stats["prevThreatA"], None, stats["prevThreatB"]]

        returnObjs = []
        for enemy in self.enemyIndices:
            distribution = enemyDistributions[enemy]
            particleList = particleLists[enemy]
            #if the enemy is in sight range
            if (gameState.getAgentPosition(enemy)):
                distribution = util.Counter()
                distribution[gameState.getAgentPosition(enemy)] = 1

            #if the enemy is not in sight range
            else:
                for state in distribution:
                    distribution[state] = distribution[state]*gameState.getDistanceProb(util.manhattanDistance(selfPosition, state), noisyDistances[enemy])
                distribution.normalize()

                #test for bottoming out
                if (distribution.totalCount() == 0):
                    self.numInitializedUniformly += 1
                    #print("DISTRIBUTION FOR:", enemy, "JUST BOTTOMED OUT. #:", self.numInitializedUniformly)
                    particleList = self.initializeUniformly(particleList)
                    distribution = self.getBeliefDistribution(particleList)
                    for state in distribution:
                        if(prevThreats[enemy] < .25 and state[0] < selfPosition[0]):
                            #print("badState: ", state, " was pre-removed")
                            distribution[state] = 0
                        elif(prevThreats[enemy] > .50 and state[0] > selfPosition[0]):
                            print("THE BACKWARDS ANTI-BIMODAL WAS CALLED")
                            distribution[state] = 0
                        else:
                            distribution[state] = distribution[state]*gameState.getDistanceProb(util.manhattanDistance(selfPosition, state), noisyDistances[enemy])
                    distribution.normalize()
                    #print("After: ", distribution)

            #resample for next time
            returnList = []
            i = 0
            while (i < self.numParticles):
                returnList.append(util.sample(distribution))
                i += 1
            returnObjs.append(returnList)
            returnObjs.append(distribution)
        return returnObjs

    def elapseTime(self, gameState, particleList):
        #this is going to be somewhat simple since we have no epxlicit knowledge about where
        #the enemy ghosts like to go. it will still be necessary to do but it may be made
        #more useful in the future
        returnList = []
        i = 0
        while (i < len(particleList)):
            possiblePositions = []
            adjacents = [(particleList[i][0], particleList[i][1]), (particleList[i][0]+1, particleList[i][1]), (particleList[i][0]-1, particleList[i][1]), (particleList[i][0], particleList[i][1]+1), (particleList[i][0], particleList[i][1]-1)]
            for pos in adjacents:
                if not(gameState.hasWall(pos[0], pos[1])):
                    possiblePositions.append(pos)
            #selects a random particle fomr possiblePositions
            returnList.append(possiblePositions[random.randint(0, len(possiblePositions)-1)])
            #selects a random particle fomr possiblePositions
            i += 1
        return returnList

    def getBeliefDistribution(self, particleList):
        distribution = util.Counter()
        for particle in particleList:
            distribution[tuple(particle)] += 1
        distribution.normalize()
        return distribution

        
    def initializeUniformly(self, particleList):
        self.numInitializedUniformly += 1
        newParticleList = []
        randomizedPositions = list(self.legalPositions)
        random.shuffle(randomizedPositions)
        i = 0
        while (i <= self.numParticles):
            for state in randomizedPositions:
                if (i <= self.numParticles):
                    newParticleList.append(state)
                i += 1
        return newParticleList

    def eat(self, target):
        if (target == "A"):
            distribution = util.Counter()
            distribution[self.enemyStartA] = 1
            particleList = [self.enemyStartA] * self.numParticles
        else:
            distribution = util.Counter()
            distribution[self.enemyStartB] = 1
            particleList = [self.enemyStartB for x in range(self.numParticles)]

        return distribution, particleList