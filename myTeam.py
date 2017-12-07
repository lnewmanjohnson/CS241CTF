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

#MAIN TODO:
# make it work on both red and blue side
# make chase cheat towards the back

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

    """
    def __init__(self, gameState):
        print("Now it is doing MyAgents init")
            #this is based off domain knowledge that they start in the opposite corner
    """

    
class TestDefender(MyAgents):

    def registerInitialState(self, gameState):

        self.PF = ParticleFilter(gameState, self.index, MyAgents.numParticles)

        CaptureAgent.registerInitialState(self, gameState)

        self.start = gameState.getAgentPosition(self.index)  # Start position


        """
        parameters
        """

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
            self.defensePoints = [(12, 11), (13, 7), (13, 4)] #TODO verify that these are optimal positions
        else:
            self.defensePoints = [(18, 10), (18, 6), (19, 3)] 

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




    def chooseAction(self, gameState):
        #raw_input()


        #MyAgents.distributionA = self.PF.getBeliefDistribution(MyAgents.particleListA)
        #MyAgents.distributionB = self.PF.getBeliefDistribution(MyAgents.particleListB)
        #print("distribution A:", MyAgents.distributionA)
        #print("distribution B:", MyAgents.distributionB)
        if (self.index == 1 or self.index == 2):
            #elapseTime for the enemy B agent
            MyAgents.particleListA = self.PF.elapseTime(gameState, MyAgents.particleListA)
        if (self.index == 0 or self.index == 3):
            #elapseTime for the enemy A agent
            MyAgents.particleListB = self.PF.elapseTime(gameState, MyAgents.particleListB)
        #print("after elapse: particleListB", MyAgents.particleListB)
        #MyAgents.distributionB = self.PF.getBeliefDistribution(MyAgents.particleListB)
        #print("after elapse: distribution B:", MyAgents.distributionB)
        #MyAgents.particleListA, MyAgents.particleListB = self.PF.elapseTime(gameState, MyAgents.particleListA, MyAgents.particleListB, MyAgents.distributionA, MyAgents.distributionB)
        #print("AFTER ELAPSETIME distribution A:", self.PF.getBeliefDistribution(MyAgents.particleListA))
        #print("AFTER ELAPSETIME distribution B:", self.PF.getBeliefDistribution(MyAgents.particleListB))
        MyAgents.particleListA, MyAgents.particleListB = self.PF.observe(gameState, MyAgents.particleListA, MyAgents.particleListB, MyAgents.distributionA, MyAgents.distributionB)
        MyAgents.distributionA = self.PF.getBeliefDistribution(MyAgents.particleListA)
        MyAgents.distributionB = self.PF.getBeliefDistribution(MyAgents.particleListB)
        #print("AFTER OBSERVE distribution A:", MyAgents.distributionA)
        #print("AFTER OBSERVE distribution B:", MyAgents.distributionB)
        #start by elapsing time for the move just previous and observing the enemies and updating beliefs

        enemyDistributions = [None, MyAgents.distributionA, None, MyAgents.distributionB]
        target = self.determineTarget(gameState, MyAgents.distributionA, MyAgents.distributionB)
        #print("target is:", target)
        if (target == "A"):
            targetDistribution = MyAgents.distributionA
        else:
            targetDistribution = MyAgents.distributionB
        probInBackCourt = 0
        zoneDistribution = [0, 0 ,0]
        for state in targetDistribution:
            # the numbers in the conditionals, 18 and 13, may need to be changed in the future to tune
            if (self.team == "red" and state[0] > 18):
                probInBackCourt += targetDistribution[state]
                if (state[1] <= 4):
                    #tests for Zone A
                    zoneDistribution[0] += targetDistribution[state]
                elif (state[1] <= 8):
                    #tests for Zone B
                    zoneDistribution[1] += targetDistribution[state]
                else:
                    #tests for Zone C
                    zoneDistribution[2] += targetDistribution[state]
            elif (self.team == "blue" and state[0] < 13):
                if (state[1] <= 4):
                    #tests for Zone A
                    zoneDistribution[0] += targetDistribution[state]
                elif (state[1] <= 8):
                    #tests for Zone B
                    zoneDistribution[1] += targetDistribution[state]
                else:
                    #tests for Zone C
                    zoneDistribution[2] += targetDistribution[state]
        print("probInBackCourt for ", target, " is: ", probInBackCourt)
        #TODO currently it does not know when enemy is actually in back court
        if (probInBackCourt > .5):                                  
        #the strictness of these inequalities probably does not really matter
            return self.pointDefense(gameState, probInBackCourt, zoneDistribution)
        else:
            return self.chase(gameState, target)


            



    def chase(self, gameState, target):

        
        #print("PROTOCOL: chasing target ", target)
        if (target == "A"):
            targetPos = MyAgents.distributionA.argMax()
        else:
            targetPos = MyAgents.distributionB.argMax()
        myPos = gameState.getAgentPosition(self.index)
        bestAction = [None, self.distancer.getDistance(myPos, targetPos)]
        for action in gameState.getLegalActions(self.index):
            #print("action being considered is:", action)
            successor = self.getSuccessor(gameState, action)
            #rint("self.distancer.getDistance(successor.getAgentState(self.index).configuration.pos, targetPos):",self.distancer.getDistance(successor.getAgentState(self.index).configuration.pos, targetPos))
            #print("bestAction[1]:",bestAction[1])
            if (self.distancer.getDistance(successor.getAgentState(self.index).configuration.pos, targetPos) <= bestAction[1]):
                #print("found advantageous action: ", action)
                bestAction[0] = action
                bestAction[1] = self.distancer.getDistance(myPos, targetPos)
        return bestAction[0]
        


    def pointDefense(self, gameState, probInBackCourt, zoneDistribution):
        #print("PROTOCOL: pointDefense")
        return self.assumePost(gameState, zoneDistribution.index(max(zoneDistribution)))
        #TODO flesh out a more nuanced transition function between posts


    def assumePost(self, gameState, postIndex):
        #print(gameState.getLegalActions(self.index))
        #will send the agent toward either post 0, 1, or 2 (a, b, c) in the perimeter
        myPos = gameState.getAgentPosition(self.index)
        bestAction = ["Stop", self.distancer.getDistance(myPos, self.defensePoints[postIndex])]
        #best action is the one that gets closest to the defense point, in this case B since were in lower
        for action in gameState.getLegalActions(self.index):
            successor = self.getSuccessor(gameState, action)
            if (self.distancer.getDistance(successor.getAgentState(self.index).configuration.pos, self.defensePoints[postIndex]) < bestAction[1]):
                bestAction[0] = action
                bestAction[1] = self.distancer.getDistance(myPos, self.defensePoints[postIndex])
        return bestAction[0]


        """
        if (isLower):
            bestAction = [None, self.distancer.getDistance(myPos, self.defensePoints[1])]
            #best action is the one that gets closest to the defense point, in this case B since were in lower
            for action in gameState.getLegalActions(self.index):
                successor = self.getSuccessor(gameState, action)
                print("successor:", successor)
                print("self.defensePoints:", self.defensePoints)
                if (self.distancer.getDistance(successor.getAgentState(self.index).configuration.pos, self.defensePoints[1]) < bestAction[1]):
                    bestAction[0] = action
                    bestAction[1] = self.distancer.getDistance(myPos, self.defensePoints[1])
            return bestAction[0]
        else:
            #doing the same thing as above but for the "A" defense point
            bestAction = [None, self.distancer.getDistance(myPos, self.defensePoints[0])]
            #best action is the one that gets closest to the defense point, in this case B since were in lower
            for action in gameState.getLegalActions(self.index):
                successor = self.getSuccessor(gameState, action)
                print("successor:", successor)
                print("self.defensePoints:", self.defensePoints)
                if (self.distancer.getDistance(successor.getAgentPosition(self.index), self.defensePoints[0]) < bestAction[1]):
                    bestAction[0] = action
                    bestAction[1] = self.distancer.getDistance(myPos, self.defensePoints[0])
            return bestAction[0]
            """

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


    def determineTarget(self, gameState, distributionA, distributionB): #TODO this needs to be more subtly done
        #this function returns the index of the enemy most dangerous right now
        midline = 15.5 #between lines x = 15 and x = 16
        myPos = gameState.getAgentPosition(self.index)
        homeWall = None #should throw error if not changed
        focalPoint =  [None, None] #should throw error if not changed
        if (self.team == "red"):
            homeWall = 0
            focalPoint = (3, 8)
        else:
            homeWall = 31
            focalPoint = (28, 7)
        #switch to figure out which place were defending

        threatA = 0
        for state in distributionA:
            if (self.distancer.getDistance(state, focalPoint) != 0):
                threatA += (1/(self.distancer.getDistance(state, focalPoint)))*distributionA[state]
            else:
                threatA += 1


        threatB = 0
        for state in distributionB:
            if (self.distancer.getDistance(state, focalPoint) != 0):
                threatB += (1/(self.distancer.getDistance(state, focalPoint)))*distributionB[state]
            else:
                threatB += 1
        #print("threatA: ",threatA, " threatB ", threatB)
        if (threatA >= threatB): #This >= is not terribly meaningful but biases very slightly toward the A agent.
            return "A"
        else:
            return "B"


class TestAgent(MyAgents):
    """
    A Dummy agent to serve as an example of the necessary agent structure.
    You should look at baselineTeam.py for more details about how to
    create an agent as this is the bare minimum.
    """

    beliefs = util.Counter()  # Keep track of beliefs about location of opponents (tuple of 2 positions with prob)
    agents = [0, 0]

    def registerInitialState(self, gameState):

        self.PF = ParticleFilter(gameState, self.index)

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
            self.defensePoints = [(12, 11), (13, 7), (13, 4)] #TODO verify that these are optimal positions
        else:
            self.defensePoints = [(18, 10), (18, 6), (19, 3)] 

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
        print("this is bottom chooseAction")
        print("BEFORE distribution A:", MyAgents.distributionA)
        print("BEFORE distribution B:", MyAgents.distributionB)
        self.PF.elapseTime(gameState, MyAgents.particleListA, MyAgents.particleListB, self.enemyDistributions)
        print("AFTER ELAPSETIME distribution A:", MyAgents.distributionA)
        print("AFTER ELAPSETIME distribution B:", MyAgents.distributionB)
        self.PF.observe(gameState, MyAgents.particleListA, MyAgents.particleListB, self.enemyDistributions)
        print("AFTER OBSERVE distribution A:", MyAgents.distributionA)
        print("AFTER OBSERVE distribution B:", MyAgents.distributionB)
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
            #print score #TODO restore this to peter's original
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

class ParticleFilter():

    def __init__(self, gameState, index, numParticles):
        """
        parameters
        """

        self.numParticles = numParticles #TODO remember to change this back to some thing reasonable

        self.index = index

        self.numInitializedUniformly = 0

        """
        setting team specific objects
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

            #this is based off domain knowledge that they start in the opposite corner
        if (self.index in gameState.getRedTeamIndices()):
            enemyStartA = (30, 13)
            enemyStartB = (30, 14)
        else:
            enemyStartA = (1, 2)
            enemyStartB = (1, 1)

    def testEdit(self, distributionA):
        distributionA = util.Counter()
        return distributionA

    def observe(self, gameState, particleListA, particleListB, distributionA, distributionB):

        selfPosition = gameState.getAgentState(self.index).getPosition()
        noisyDistances = gameState.getAgentDistances()
        distributionA = self.getBeliefDistribution(particleListA)
        distributionB = self.getBeliefDistribution(particleListB)
        enemyDistributions = [None, distributionA, None, distributionB]
        particleLists = [None, particleListA, None, particleListB]

        returnDistributions = []
        returnLists = []
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
                    print("DISTRIBUTION FOR:", enemy, "JUST BOTTOMED OUT. #:", self.numInitializedUniformly)
                    particleList = self.initializeUniformly(particleList)
                    distribution = self.getBeliefDistribution(particleList)

            #resample for next time
            returnList = []
            i = 0
            while (i < self.numParticles):
                returnList.append(util.sample(distribution))
                i += 1
            returnLists.append(returnList)
            #returnDistributions.append(distribution)
        return returnLists

    def elapseTime(self, gameState, particleList):
        #this is going to be somewhat simple since we have no epxlicit knowledge about where
        #the enemy ghosts like to go. it will still be necessary to do but it may be made
        #more useful in the future
        #particleListA = particleLists[self.enemyIndices[0]]
        #particleListB = particleLists[self.enemyIndices[1]]

        #print("particleList",particleList)
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

        """
        returnListA = []
        returnListB = []
        returnLists = []
        if (self.index == 1 or self.index == 2):
            #these are the cases where the agent will elapseTime for their "A" enemy
            i = 0
            while (i < len(particleListA)):
                #building up an unweighted distribution for possible new positions
                numPossibilities = 0
                possiblePositions = []
                adjacents = [[particleListA[i][0], particleListA[i][1]], [particleListA[i][0]+1, particleListA[i][1]], [particleListA[i][0]-1, particleListA[i][1]], [particleListA[i][0], particleListA[i][1]+1], [particleListA[i][0], particleListA[i][1]-1]]
                #this is enumerating all the adjacent squares
                for possiblePos in adjacents:
                    if not(gameState.hasWall(possiblePos[0], possiblePos[1])):
                        possiblePositions.append(possiblePos)
                #this for loop has built up the possiblePositions array that is going to serve as the "distribution" for moving the particles in time
                returnListA.append(possiblePositions[random.randint(0, len(possiblePositions)-1)])
                particleListA[i] = possiblePositions[random.randint(0, len(possiblePositions)-1)]
                #this is an obstruse way of getting a random element of the possiblePositions array
                i += 1
        else:
            #in a case where the the agent will elapseTime for their "B" enemy
            i = 0
            while (i < len(particleListB)):
                #building up an unweighted distribution for possible new positions
                numPossibilities = 0
                possiblePositions = []
                adjacents = [[particleListB[i][0], particleListB[i][1]], [particleListB[i][0]+1, particleListB[i][1]], [particleListB[i][0]-1, particleListB[i][1]], [particleListB[i][0], particleListB[i][1]+1], [particleListB[i][0], particleListB[i][1]-1]]
                #this is enumerating all the adjacent squares
                for possiblePos in adjacents:
                    if not(gameState.hasWall(possiblePos[0], possiblePos[1])):
                        possiblePositions.append(possiblePos)
                #this for loop has built up the possiblePositions array that is going to serve as the "distribution" for moving the particles in time
                returnListB.append(possiblePositions[random.randint(0, len(possiblePositions)-1)])
                particleListB[i] = possiblePositions[random.randint(0, len(possiblePositions)-1)]
                #this is an obstruse way of getting a random element of the possiblePositions array
                i += 1

        returnList = [returnListA, returnListB]
        if (len(returnListA) == 0):
            returnList[0] = particleListA
        if (len(returnListB) == 0):
            returnList[1] = particleListB
        
        return returnLists
        """


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

    def setBeliefDistribution(self, distTag):
        if (distTag == "A"):
            self.getBeliefDistribution(self.particleListA)
        else:
            self.getBeliefDistribution(self.particleListB)

    def getCounterInstance(self, distTag):
        #NOTE: This should be obsolete now after moving to a shared MyAgents distribution system
        #this actually returns the counter so the class variables can be used in a not-gross way
        if (distTag == "A"):
            return self.distributionA
        else:
            return self.distributionB

