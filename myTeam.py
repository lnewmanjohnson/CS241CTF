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
import math


#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first='TestAgent', second='TestDefender'):
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

class TestDefender(CaptureAgent):

    beliefs = util.Counter()
    agents = [0, 0]

    def registerInitialState(self, gameState):


        #TODO figure out in registerInitialState operations really need to be run on both agents or if some can be run by one and emitted to the other

        CaptureAgent.registerInitialState(self, gameState)

        self.numParticles = 300
        self.start = gameState.getAgentPosition(self.index)  # Start position

        self.enemyIndices = gameState.getRedTeamIndices()
        if (self.index in gameState.getRedTeamIndices()):
            self.enemyIndices = gameState.getBlueTeamIndices()

        self.legalPositions = []
        for x in range(0, 32):
            for y in range(0, 16):
                if not(gameState.hasWall(x,y)):
                    self.legalPositions.append((x,y))

        #create the objects that are going to be persistent
        self.particleListA = []     #starts at 30, 13 or 1,2
        self.particleListB = []     #starts at 30, 14 or 1,1
        distributionA = self.getBeliefDistribution(self.particleListA)
        distributionB = self.getBeliefDistribution(self.particleListB)

        #this is based off domain knowledge that they start in the opposite corner
        enemyStartA = [1, 2]
        enemyStartB = [1, 1]
        if (self.index in gameState.getRedTeamIndices()):
            enemyStartA = [30, 13]
            enemyStartB = [30, 14]

        #fill out the prelim particleLists with the particles representing the enemies in the corner
        i = 1
        while (i <= self.numParticles):
            self.particleListA.append(enemyStartA)
            self.particleListB.append(enemyStartB)
            i += 1




    def chooseAction(self, gameState): #TODO
        self.observe(gameState)
        #start by observing the enemies and updating


        #target = determineTarget(gameState)

    def determineTarget(gameState): #TODO
        #DETERMINE WHICH ENEMY IS MOST DANGEROUS, OR WHETHER ITS A 2v1





    def observe(self, gameState):
        teammate_index = (self.index + 2) % 4
        teammate = gameState.getAgentState(teammate_index)


        noisyDistances = gameState.getAgentDistances()
        #emissionModel is of the form gameState.getDistanceProb(distance, noisyDistance)
        selfPosition = gameState.getAgentState(self.index).getPosition()
        teammatePosition = gameState.getAgentState((self.index + 2) % 4)


        #reweighting distribution based on new information
        distributionA = self.getBeliefDistribution(self.particleListA)
        #reweight first distribution based on the noisyDistance we get for enemy A
        for state in distributionA:
            distributionA[state] = distributionA[state]*gameState.getDistanceProb(util.manhattanDistance(selfPosition, state), noisyDistances[enemyIndices[0]])
        distributionA.normalize()
        #reweight first distribution based on the noisyDistance we get for enemy B
        for state in distributionB:
            distributionB[state] = distributionB[state]*gameState.getDistanceProb(util.manhattanDistance(selfPosition, state), noisyDistances[enemyIndices[1]])
        distributionB.normalize()
        
        #test for bottoming out, which should be rare but is a good test none the less
        if (distributionA.totalCount() == 0):
            self.particleListA = self.initializeUniformly(particleListA)
            distributionA = self.getBeliefDistribution(particleListA)
        if (distributionB.totalCount() == 0):
            self.particleListB = self.initializeUniformly(particleListB)
            distributionB = self.getBeliefDistribution(particleListB)

        #resample for next time
        self.particleListA = []
        self.particleListB = []
        i = 0
        while (i < self.numParticles):
            self.particleListA.append(util.sample(distributionA))
            self.particleListB.append(util.sample(distributionB))
            i += 1

    def elapseTime(self, gameState):
        #this is going to be somewhat simple since we have no epxlicit knowledge about where
        #the enemy ghosts like to go. it will still be necessary to do but may not be very helpful
        if (self.index == 1 or self.index == 2):
            #these are the cases where the agent will elapseTime for their "A" enemy
            i = 0
            while (i < len(self.particleListA)):
                #building up an unweighted distribution for possible new positions
                numPossibilities = 0
                possiblePositions = []
                adjacents = [[self.particleListA[i][0], self.particleListA[i][1]], [self.particleListA[i][0]+1, self.particleListA[i][1]], [self.particleListA[i][0]-1, self.particleListA[i][1]], [self.particleListA[i][0], self.particleListA[i][1]+1], [self.particleListA[i][0], self.particleListA[i][1]-1]]
                #this is enumerating all the adjacent squares
                for possiblePos in adjacents:
                    if not(gameState.hasWall(possiblePos[0], possiblePos[1])):
                        possiblePositions.append(possiblePos)
                #this for loop has built up the possiblePositions array that is going to serve as the "distribution" for moving the particles in time
                self.particleListA[i] = possiblePositions[random.randint(0, len(possiblePositions)-1)]
                #this is an obstruse way of getting a random element of the possiblePositions array
                i += 1

    def getBeliefDistribution(self, particleList):
        distribution = util.Counter()
        for particle in particleList:
            distribution[particle] += 1
        distribution.normalize()
        return distribution

        
    def initializeUniformly(self, particleList):
        #TODO this is not super important but it is a good failsafe for if the distribution bottoms out in a weird way
        newParticleList = []
        randomizedPositions = random.shuffle(legalPositions)
        i = 0
        while (i <= self.numParticles):
            for state in randomizedPositions:
                if (i <= self.numParticles):
                    newParticleList.append(state)
                i += 1
        return newParticleList





class TestAgent(CaptureAgent):
    """
    A Dummy agent to serve as an example of the necessary agent structure.
    You should look at baselineTeam.py for more details about how to
    create an agent as this is the bare minimum.
    """

    beliefs = util.Counter()  # Keep track of beliefs about location of opponents (tuple of 2 positions with prob)
    agents = [0, 0]

    def registerInitialState(self, gameState):
        """
        This method handles the initial setup of the
        agent to populate useful fields (such as what team
        we're on).

        A distanceCalculator instance caches the maze distances
        between each pair of positions, so your agents can use:
        self.distancer.getDistance(p1, p2)

        IMPORTANT: This method may run for at most 15 seconds.
        """

        '''
        Make sure you do not delete the following line. If you would like to
        use Manhattan distances instead of maze distances in order to save
        on initialization time, please take a look at
        CaptureAgent.registerInitialState in captureAgents.py.
        '''
        CaptureAgent.registerInitialState(self, gameState)

        '''
        Your initialization code goes here, if you need any.
        '''

        # Init beliefs with starting positions of opponents
        belief = [(0, 0), (0, 0)]
        for i in range(2):
            o = self.getOpponents(gameState)
            belief[i] = gameState.getAgentPosition(o[i])
        TestAgent.beliefs[tuple(belief)] = 1.0

        self.start = gameState.getAgentPosition(self.index)  # Start position

    def chooseAction(self, gameState):
        """
        Picks among actions randomly.
        """
        if self.index > 1:
            index = 0
        else:
            index = 1

        teammate_index = (self.index + 2) % 4
        teammate = gameState.getAgentState(teammate_index)

        # TODO: Update beliefs based on new observations and possible moves
        beliefs = TestAgent.beliefs
        # print(gameState.getAgentDistances())
        # print(beliefs)

        actions = gameState.getLegalActions(self.index)
        if TestAgent.agents[index] == 0:
            return self.search(gameState, actions)

    def search(self, gameState, actions):
        """
        Offense 1: Aggressively searches for food, avoiding ghosts
        """
        def evaluate(self, gameState, action):
            score = 0.0
            danger = 0
            dist = 9999

            successor = self.getSuccessor(gameState, action)
            newPos = successor.getAgentState(self.index).configuration.pos
            if (successor.getAgentState(self.index).numCarrying > gameState.getAgentState(self.index).numCarrying):
                score += 50

            for food in self.getFood(successor).asList():
                score += 10.0 / self.getMazeDistance(newPos, food)

            score -= len(self.getFood(successor).asList())
            print score
            return score

        # TODO: Checks for switching routines
        carrying = gameState.getAgentState(self.index).numCarrying
        if (carrying > 6):
            return self.deliver_food(gameState, actions)
        # elif(other_checks): return other)subroutine2(gameState)
        else:
            best_action = actions[0]
            best_score = -9999

            for action in actions:
                score = evaluate(self, gameState, action)
                if (score > best_score):
                    best_score = score
                    best_action = action

        return best_action

    def deliver_food(self, gameState, actions):
        """
        Offense 2: Return food to safety
        """
        def evaluate(self, gameState, action):
            #TODO: Keep other ghosts into account
            score = 0.0
            danger = 0
            dist = 9999

            successor = self.getSuccessor(gameState, action)
            newPos = successor.getAgentState(self.index).configuration.pos

            safety_spots = [(17, i) for i in [1, 3, 4, 6, 7, 8, 10, 14]]
            for pos in safety_spots:
                score += 10.0 / (self.getMazeDistance(newPos, pos) ** 2)
            return score

        best_action = actions[0]
        best_score = -9999
        for action in actions:
            score = evaluate(self, gameState, action)
            if (score > best_score):
                best_score = score
                best_action = action

        return best_action

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
