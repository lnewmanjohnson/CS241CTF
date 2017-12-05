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

        #DEBUGGING OBJECTS HERE
        self.numInitializedUniformly = 0

        CaptureAgent.registerInitialState(self, gameState)

        self.start = gameState.getAgentPosition(self.index)  # Start position


        """
        parameters
        """

        self.numParticles = 1000


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
            self.defensePoints = [(12, 11), (13, 5)] #these might need to be up one or down one
        else:
            self.defensePoints = [(18, 10), (19, 4)]

            #create a list of form [a, b] containing the enemy indices
        self.enemyIndices = gameState.getRedTeamIndices()
        if (self.index in gameState.getRedTeamIndices()):
            self.enemyIndices = gameState.getBlueTeamIndices()


        """
        pre-processing some useful persistent objects
        """

            #built list of legalPositions
            #NOTE: USEFUL ONLY FOR INITIALIZEUNIFORMLY() AND MAY BE MOVED IF THAT ISNT USED
        self.legalPositions = []
        for x in range(0, 32):
            for y in range(0, 16):
                if not(gameState.hasWall(x,y)):
                    self.legalPositions.append((x,y))



            #create the objects that are going to be persistent
        self.particleListA = []     #starts at 30, 13 or 1,2
        self.particleListB = []     #starts at 30, 14 or 1,1
        self.distributionA = self.getBeliefDistribution(self.particleListA)
        self.distributionB = self.getBeliefDistribution(self.particleListB)
        self.enemyDistributions = [None, None, None, None]
        if (self.team == "red"):
            self.enemyDistributions[1] = self.distributionA
            self.enemyDistributions[3] = self.distributionB
        else:
            self.enemyDistributions[0] = self.distributionA
            self.enemyDistributions[2] = self.distributionB

            #this is based off domain knowledge that they start in the opposite corner
        if (self.index in gameState.getRedTeamIndices()):
            enemyStartA = (30, 13)
            enemyStartB = (30, 14)
        else:
            enemyStartA = (1, 2)
            enemyStartB = (1, 1)

            #fill out the prelim particleLists with the particles representing the enemies in the corner
        i = 1
        while (i <= self.numParticles):
            self.particleListA.append(enemyStartA)
            self.particleListB.append(enemyStartB)
            i += 1



        #TODO figure out in registerInitialState operations really need to be run on both agents or if some can be run by one and emitted to the other





    def chooseAction(self, gameState): #TODO
        self.elapseTime(gameState)
        self.observe(gameState)
        #start by elapsing time for the move just previous and observing the enemies and updating beliefs

        target = self.determineTarget(gameState)
        targetDistribution = self.enemyDistributions[target]
        targetDistribution = self.enemyDistributions[target].copy()
        probInBackCourt = 0
        probInLower = 0
        for state in targetDistribution:
            # the numbers in the conditionals, 18 and 13, may need to be changed in the future to tune
            if (self.team == "red" and state[0] > 18):
                probInBackCourt += targetDistribution[state]
                if (state[1] <= 7):
                    probInLower += targetDistribution[state]
                print("probInBackCourt for ", target, " is: ", probInBackCourt)
            elif (self.team == "blue" and state[0] < 13):
                probInBackCourt += targetDistribution[state]
                if (state[1] <= 7):
                    probInLower += targetDistribution[state]

        #TODO currently it does not know when enemy is actually in back court
        if (probInBackCourt > .5):                                  
        #the strictness of these inequalities probably does not really matter
            return self.assumePost(gameState, (probInLower > .5))
        else:
            print("WARN: The enemy was not in backCourt and the chase function")


    def assumePost(self, gameState, isLower):
        myPos = gameState.getAgentPosition(self.index)
        if (isLower):
            bestAction = [None, self.distancer.getDistance(myPos, self.defensePoints[1])]
            #best action is the one that gets closest to the defense point, in this case B since were in lower
            for action in gameState.getLegalActions(self.index):
                successor = self.getSuccessor(gameState, action)
                if (self.distancer.getDistance(successor, self.defensePoints[1]) < bestAction[1]):
                    bestAction[0] = action
                    bestAction[1] = self.distancer.getDistance(myPos, self.defensePoints[1])
            return bestAction[0]
        else:
            #doing the same thing as above but for the "A" defense point
            bestAction = [None, self.distancer.getDistance(myPos, self.defensePoints[0])]
            #best action is the one that gets closest to the defense point, in this case B since were in lower
            for action in gameState.getLegalActions(self.index):
                successor = self.getSuccessor(gameState, action)
                if (self.distancer.getDistance(successor.getAgentPosition(self.index), self.defensePoints[0]) < bestAction[1]):
                    bestAction[0] = action
                    bestAction[1] = self.distancer.getDistance(myPos, self.defensePoints[0])
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


        #calculates if the enemy is within striking range


    def determineTarget(self, gameState): #TODO this needs to be more subtly done
        #this function returns the index of the enemy most dangerous right now
        midline = 15.5 #between lines x = 15 and x = 16
        myPos = gameState.getAgentPosition(self.index)
        homeWall = None #should throw error if not changed
        focalPoint =  [None, None] #should throw error if not changed
        if (self.index in gameState.getRedTeamIndices()):
            homeWall = 0
            focalPoint = (3, 8)
        else:
            homeWall = 31
            focalPoint = (28, 7)
        #switch to figure out which place were defending

        distributionA = self.getBeliefDistribution(self.particleListA)
        threatA = 0
        for state in distributionA:
            threatA += self.distancer.getDistance(state, focalPoint)*distributionA[state]
        distributionB = self.getBeliefDistribution(self.particleListB)

        threatB = 0
        for state in distributionB:
            threatB += self.distancer.getDistance(state, focalPoint)*distributionB[state]

        if (threatA >= threatB): #This >= is not terribly meaningful but biases very slightly toward the A agent.
            return self.enemyIndices[0]
        else:
            return self.enemyIndices[1]

    def observe(self, gameState):
        #this may be too slow to run if planning gets particularly complex
        teammate_index = (self.index + 2) % 4
        teammate = gameState.getAgentState(teammate_index)

        noisyDistances = gameState.getAgentDistances()
        #emissionModel is of the form gameState.getDistanceProb(distance, noisyDistance)
        selfPosition = gameState.getAgentState(self.index).getPosition()
        teammatePosition = gameState.getAgentState((self.index + 2) % 4)


        #reweighting distribution based on new information
        self.distributionA = self.getBeliefDistribution(self.particleListA)
        self.distributionB = self.getBeliefDistribution(self.particleListB)
        #reweight first distribution based on the noisyDistance we get for enemy A
        for state in self.distributionA:
            self.distributionA[state] = self.distributionA[state]*gameState.getDistanceProb(util.manhattanDistance(selfPosition, state), noisyDistances[self.enemyIndices[0]])
        self.distributionA.normalize()
        #reweight first distribution based on the noisyDistance we get for enemy B
        for state in self.distributionB:
            self.distributionB[state] = self.distributionB[state]*gameState.getDistanceProb(util.manhattanDistance(selfPosition, state), noisyDistances[self.enemyIndices[1]])
        self.distributionB.normalize()

        #test for bottoming out, which should be rare but is a good test none the less
        if (self.distributionA.totalCount() == 0):
            self.particleListA = self.initializeUniformly(self.particleListA)
            self.distributionA = self.getBeliefDistribution(self.particleListA)
        if (self.distributionB.totalCount() == 0):
            self.particleListB = self.initializeUniformly(self.particleListB)
            self.distributionB = self.getBeliefDistribution(self.particleListB)

        #resample for next time
        self.particleListA = []
        self.particleListB = []
        i = 0
        while (i < self.numParticles):
            self.particleListA.append(util.sample(self.distributionA))
            self.particleListB.append(util.sample(self.distributionB))
            i += 1

        self.distributionA = self.getBeliefDistribution(self.particleListA)
        self.distributionB = self.getBeliefDistribution(self.particleListB)
        if (self.team == "red"):
            self.enemyDistributions[1] = self.distributionA
            self.enemyDistributions[3] = self.distributionB
        else:
            self.enemyDistributions[0] = self.distributionA
            self.enemyDistributions[2] = self.distributionB

    def elapseTime(self, gameState):
        #this is going to be somewhat simple since we have no epxlicit knowledge about where
        #the enemy ghosts like to go. it will still be necessary to do but it may be made
        #more useful in the future
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
        else:
            #in a case where the the agent will elapseTime for their "B" enemy
            i = 0
            while (i < len(self.particleListB)):
                #building up an unweighted distribution for possible new positions
                numPossibilities = 0
                possiblePositions = []
                adjacents = [[self.particleListB[i][0], self.particleListB[i][1]], [self.particleListB[i][0]+1, self.particleListB[i][1]], [self.particleListB[i][0]-1, self.particleListB[i][1]], [self.particleListB[i][0], self.particleListB[i][1]+1], [self.particleListB[i][0], self.particleListB[i][1]-1]]
                #this is enumerating all the adjacent squares
                for possiblePos in adjacents:
                    if not(gameState.hasWall(possiblePos[0], possiblePos[1])):
                        possiblePositions.append(possiblePos)
                #this for loop has built up the possiblePositions array that is going to serve as the "distribution" for moving the particles in time
                self.particleListB[i] = possiblePositions[random.randint(0, len(possiblePositions)-1)]
                #this is an obstruse way of getting a random element of the possiblePositions array
                i += 1


    def getBeliefDistribution(self, particleList):
        distribution = util.Counter()
        for particle in particleList:
            distribution[tuple(particle)] += 1
        distribution.normalize()
        return distribution

        
    def initializeUniformly(self, particleList):
        self.numInitializedUniformly += 1
        print("WARN: InitializeUniformly() was called and has been called a total of: ", self.numInitializedUniformly, " times this game.")
        #TODO this is not super important but it is a good failsafe for if the distribution bottoms out in a weird way
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
