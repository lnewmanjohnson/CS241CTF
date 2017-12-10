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
    max_time = 0
    roles = [None, None, None, None]
    isGuarding = [None, None, None, None]
    isChasing = [None, None, None, None]
    top = -1

class TestDefender(MyAgents):

    def offenseChooseAction(self, gameState):
        """
        Picks among the actions with the highest Q(s,a).
        """
        if (self.team == "red" and gameState.data.score >= 3) or (self.team == "blue" and gameState.data.score <= -3):
            MyAgents.roles[self.index] = "defense"
            return self.chooseAction(gameState)
        start = time.time()
        if (self.index == 1 or self.index == 2):
            # elapseTime for the enemy B agent
            MyAgents.particleListA = self.PF.elapseTime(gameState, MyAgents.particleListA)
        if (self.index == 0 or self.index == 3):
            # elapseTime for the enemy A agent
            MyAgents.particleListB = self.PF.elapseTime(gameState, MyAgents.particleListB)

        MyAgents.particleListA, MyAgents.distributionA, MyAgents.particleListB, MyAgents.distributionB = self.PF.observe(
            gameState, MyAgents.particleListA, MyAgents.particleListB, MyAgents.stats)

        enemyDistributions = [None, None, None, None]
        enemyDistributions[self.enemyIndices[0]] = MyAgents.distributionA
        enemyDistributions[self.enemyIndices[1]] = MyAgents.distributionB

        actions = gameState.getLegalActions(self.index)
        values = [self.evaluate(gameState, a) for a in actions]

        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]

        foodLeft = len(self.getFood(gameState).asList())

        if foodLeft <= 2:
            bestDist = 9999
            for action in actions:
                successor = self.getSuccessor(gameState, action)
                pos2 = successor.getAgentPosition(self.index)
                dist = self.getMazeDistance(self.start, pos2)
                if dist < bestDist:
                    bestAction = action
                    bestDist = dist
            elapsed = time.time() - start
            if elapsed > 0.95:
                raise ValueError('chooseAction Timeout')
            MyAgents.max_time = max(MyAgents.max_time, elapsed)
            return bestAction

        return random.choice(bestActions)

    def evaluate(self, gameState, action):
        """
        Computes a linear combination of features and feature weights
        """
        features = self.getFeatures(gameState, action)
        weights = self.getWeights(gameState, action)
        return features * weights

    def getSafetyScore(self, gameState):
        myPos = gameState.getAgentPosition(self.index)
        myState = gameState.getAgentState(self.index)
        safety_score = 100
        vulnerable = True
        if (myPos[0] > 15 and myState.scaredTimer == 0):
            vulnerable = False
        if vulnerable:
            opps_index = [(self.index + 1) % 4, (self.index + 3) % 4]
            for opp in opps_index:
                opp_state = gameState.getAgentState(opp)
                opp_timer = opp_state.scaredTimer
                opp_pos = gameState.getAgentPosition(opp)
                if opp_pos is not None and not (
                        opp_state.isPacman and myState.scaredTimer > 0):
                    distance = self.getMazeDistance(myPos, opp_pos)
                    if distance > opp_timer and distance <= 6:
                        safety_score -= 150 / distance
                if opp_pos is None:
                    if opp < 2:
                        opp_pos = MyAgents.distributionA.argMax()
                    else:
                        opp_pos = MyAgents.distributionB.argMax()
                    distance = self.getMazeDistance(myPos, opp_pos)
                    if distance < 6:
                        distance = 7
                    safety_score -= 10 / distance
        return safety_score

    def getFeatures(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        myState = successor.getAgentState(self.index)
        myPos = successor.getAgentPosition(self.index)
        foodList = self.getFood(successor).asList()
        safetyScore = self.getSafetyScore(successor)
        features['successorScore'] = 0

        if safetyScore > 50 and len(foodList) > 2 and myState.numCarrying < 5:
            features['successorScore'] += - 2*len(foodList) + safetyScore + 10*myState.numReturned
            opps_index = [(self.index + 1) % 4, (self.index + 3) % 4]
            for opp in opps_index:
                opp_state = successor.getAgentState(opp)
                opp_timer = opp_state.scaredTimer
                opp_pos = successor.getAgentPosition(opp)
                if opp_pos is not None:
                    distance = self.getMazeDistance(myPos, opp_pos)
                    if distance <= 3 and (opp_state.isPacman or opp_timer > distance + 2):
                        features['successorScore'] += 5/distance
                    if opp_pos == (1, 2) or (opp_timer == 0 and gameState.getAgentState(opp).scaredTimer > 1):
                        features['successorScore'] += 10000
        else:
            myPos = successor.getAgentPosition(self.index)
            score = 0.0
            safety_spots = [(17, i) for i in [1, 3, 4, 6, 7, 8, 10, 14]]
            for pos in safety_spots:
                if self.getMazeDistance(myPos, pos) == 0:
                    score += 10
                else:
                    score += 10.0 / self.getMazeDistance(myPos, pos)
            features['successorScore'] = score + safetyScore

        # Compute distance to the nearest food
        if len(foodList) > 0:
            myPos = successor.getAgentState(self.index).getPosition()
            if MyAgents.roles[self.index] == "offense" and MyAgents.roles[(self.index + 2) % 4] == "offense":
                if MyAgents.top == self.index:
                    altFoodList = []
                    for food in foodList:
                        if food[1] > 7:
                            altFoodList.append(food)
                    minDistance = min([self.getMazeDistance(myPos, food) for food in altFoodList])
                    features['distanceToFood'] = minDistance
                else:
                    altFoodList = []
                    for food in foodList:
                        if food[1] < 8:
                            altFoodList.append(food)
                    minDistance = min([self.getMazeDistance(myPos, food) for food in altFoodList])
                    features['distanceToFood'] = minDistance
            else:
                minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
                features['distanceToFood'] = minDistance

        return features

    def getWeights(self, gameState, action):
        return {'successorScore': 100, 'distanceToFood': -1}

    def registerInitialState(self, gameState):

        self.PF = ParticleFilter(gameState, self.index, MyAgents.numParticles)

        CaptureAgent.registerInitialState(self, gameState)

        self.start = gameState.getAgentPosition(self.index)  # Start position
        if self.index < 2:
            MyAgents.roles[self.index] = "offense"
        else:
            MyAgents.roles[self.index] = "defense"

        # of the form [action, position, timeSpentInPosition]
        self.prevStats = ["Stop", [0, 0], 0]

        """
        setting team specific objects
        """

        # set team name
        if (self.index in gameState.getRedTeamIndices()):
            self.team = "red"
            self.enemyIndices = gameState.getBlueTeamIndices()
            self.defensePoints = [(13, 4), (12, 6), (12, 10)]
            enemyStartA = (30, 13)
            enemyStartB = (30, 14)
        else:
            self.team = "blue"
            self.enemyIndices = gameState.getRedTeamIndices()
            self.defensePoints = [(19, 3), (19, 6), (18, 11)]
            enemyStartA = (1, 2)
            enemyStartB = (1, 1)
        i = 1
        while (i <= self.numParticles):
            MyAgents.particleListA.append(enemyStartA)
            MyAgents.particleListB.append(enemyStartB)
            i += 1

            # create the enemyDistributions array to make index to distribution conversion easier
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

            # filling out some default stats
        MyAgents.stats["prevThreatA"] = 0
        MyAgents.stats["prevThreatB"] = 0

    def chooseAction(self, gameState):
        # raw_input()

        opp_timer = 99
        opps_index = [(self.index + 1) % 4, (self.index + 3) % 4]
        for opp in opps_index:
            opp_state = gameState.getAgentState(opp)
            opp_timer = min(opp_timer, opp_state.scaredTimer)
        if opp_timer > 3 and MyAgents.roles[self.index] == "defense":
            MyAgents.roles[self.index] == "offense"
            if gameState.getAgentPosition(self.index)[1] > gameState.getAgentPosition((self.index + 2) % 4)[1]:
                MyAgents.top = self.index
            return self.offenseChooseAction(gameState)
        if opp_timer == 0 and self.index > 2 and MyAgents.roles[self.index] == "offense":
            MyAgents.roles[self.index] == "defense"
        if MyAgents.roles[self.index] == "offense":
            return self.offenseChooseAction(gameState)
        if self.index < 2:
            if (self.team == "red" and gameState.data.score <= 0) or (
                    self.team == "blue" and gameState.data.score >= 0):
                MyAgents.roles[self.index] = "offense"
                return self.offenseChooseAction(gameState)

        start = time.time()
        if (self.index == 1 or self.index == 2):
            # elapseTime for the enemy B agent
            MyAgents.particleListA = self.PF.elapseTime(gameState, MyAgents.particleListA)
        if (self.index == 0 or self.index == 3):
            # elapseTime for the enemy A agent
            MyAgents.particleListB = self.PF.elapseTime(gameState, MyAgents.particleListB)

        MyAgents.particleListA, MyAgents.distributionA, MyAgents.particleListB, MyAgents.distributionB = self.PF.observe(
            gameState, MyAgents.particleListA, MyAgents.particleListB, MyAgents.stats)

        enemyDistributions = [None, None, None, None]
        enemyDistributions[self.enemyIndices[0]] = MyAgents.distributionA
        enemyDistributions[self.enemyIndices[1]] = MyAgents.distributionB

        target, threatA, threatB = self.determineTarget(gameState, MyAgents.distributionA, MyAgents.distributionB)
        MyAgents.stats["prevThreatA"] = threatA
        MyAgents.stats["prevThreatB"] = threatB

        # TODO THE FUTURE SITE OF THE SCAREDTIMER SWITCH
        elapsed = time.time() - start
        #if elapsed > 0.95:
            #raise ValueError('ChooseAction Timeout')
        MyAgents.max_time = max(MyAgents.max_time, elapsed)
        return self.pointDefense(gameState)

    def chase(self, gameState, target):
        # this function just tries to run to the square where the ghost most likely is
        MyAgents.isChasing[self.index] = target

        if (target == "A"):
            targetPos = MyAgents.distributionA.argMax()
        else:
            targetPos = MyAgents.distributionB.argMax()

        # print("running chase with target: ", target)
        # print("currently at: ", gameState.getAgentPosition(self.index))
        # print("trying to reach: ", targetPos)
        # print("PROTOCOL: chasing target ", target, " at pos: ", targetPos)

        # sets the limitLine which is the X value the defender will NEVER go to to chase
        if (self.team == "red"):
            defenderLimitZone = (0, 15)
        else:
            defenderLimitZone = (17, 31)
        myPos = gameState.getAgentPosition(self.index)
        bestAction = ["Stop", self.distancer.getDistance(myPos, targetPos)]
        for action in gameState.getLegalActions(self.index):
            successor = self.getSuccessor(gameState, action)
            if (successor.getAgentState(self.index).configuration.pos == targetPos and
                    successor.getAgentState(self.index).configuration.pos[0]):
                # the defender is about to eat the enemy
                if (target == "A"):
                    MyAgents.distributionA, MyAgents.particleListA = self.PF.eat(target)
                else:
                    MyAgents.distributionB, MyAgents.particleListB = self.PF.eat(target)
                return action

            if (self.distancer.getDistance(successor.getAgentState(self.index).configuration.pos, targetPos) <=
                    bestAction[1] and successor.getAgentState(self.index).configuration.pos[0] in range(
                            defenderLimitZone[0], defenderLimitZone[1])):
                bestAction[0] = action
                bestAction[1] = self.distancer.getDistance(successor.getAgentState(self.index).configuration.pos,
                                                           targetPos)
        if (self.runStallStats(bestAction[0], self.getSuccessor(gameState, bestAction[0])) == True):
            randomAction = gameState.getLegalActions(self.index)[
                random.randint(0, len(gameState.getLegalActions(self.index)) - 1)]
            self.runStallStats(randomAction, self.getSuccessor(gameState, bestAction[0]))
            return randomAction
        else:
            return bestAction[0]

    def pointDefense(self, gameState):
        # this function is a switch to tell the defenders how to play point defense
        if (self.team == "red"):
            defenseLine = 17
            direction = 1
        else:
            defenseLine = 13
            direction = (-1)

        probInBackCourt = 0
        zoneDistribution = [0, 0, 0]

        target, prevThreatA, prevThreatB = self.determineTarget(gameState, MyAgents.distributionA,
                                                                MyAgents.distributionB)
        MyAgents.stats["prevThreatA"] = prevThreatA
        MyAgents.stats["prevThreatB"] = prevThreatB

        if (target == "A"):
            targetDistribution = MyAgents.distributionA
        else:
            targetDistribution = MyAgents.distributionB

        for state in targetDistribution:
            if ((state[0] - defenseLine) * direction > 0):
                # tests if they are beyond the
                probInBackCourt += targetDistribution[state]
            if (state[1] <= 4):
                # test for Zone A
                zoneDistribution[0] += targetDistribution[state]
            elif (state[1] <= 9):
                # tests for Zone B
                zoneDistribution[1] += targetDistribution[state]
            else:
                # tests for Zone C
                zoneDistribution[2] += targetDistribution[state]

        if (probInBackCourt > .5 or MyAgents.isChasing[(self.index + 2) % 4] == target):
            # the strictness of these inequalities probably does not really matter
            return self.assumePost(gameState, zoneDistribution.index(max(zoneDistribution)))
        else:
            return self.chase(gameState, target)

    def assumePost(self, gameState, postIndex):
        MyAgents.isChasing[self.index] = None
        if (postIndex == MyAgents.isGuarding[(self.index + 2) % 4]):
            if (postIndex == 2 or postIndex == 0):
                postIndex = 1
            else:
                if not(MyAgents.isGuarding[self.index] == None):
                    postIndex = MyAgents.isGuarding[self.index]
                else:
                    postIndex = 1
        MyAgents.isGuarding[self.index] = postIndex
        # this function sends the agent toward either post a, b, or c along the perimeter
        myPos = gameState.getAgentPosition(self.index)
        bestAction = ["Stop", self.distancer.getDistance(myPos, self.defensePoints[postIndex])]
        # best action is the one that gets closest to the defense point, in this case B since were in lower
        for action in gameState.getLegalActions(self.index):
            successor = self.getSuccessor(gameState, action)
            if (self.distancer.getDistance(successor.getAgentState(self.index).configuration.pos,
                                           self.defensePoints[postIndex]) < bestAction[1]):
                bestAction[0] = action
                bestAction[1] = self.distancer.getDistance(myPos, self.defensePoints[postIndex])

        # a small method to check if the agent got stuck somehow
        if (self.runStallStats(bestAction[0], self.getSuccessor(gameState, bestAction[0])) == True):
            randomAction = gameState.getLegalActions(self.index)[
                random.randint(0, len(gameState.getLegalActions(self.index)) - 1)]
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
        # this function returns the index of the enemy most likely playing offense

        # sets variables so the function can go in both directions
        if (self.team == "red"):
            backLine = 0
            direction = (1)
        else:
            backLine = 31
            direction = (-1)

        threatA = 0
        for state in distributionA:
            threatA += (direction) * (1.0 / (state[0] - backLine)) * distributionA[state]
        threatB = 0
        for state in distributionB:
            threatB += (direction) * (1.0 / (state[0] - backLine)) * distributionB[state]
        if (threatA >= threatB):
            return "A", threatA, threatB
        else:
            return "B", threatA, threatB

    def runStallStats(self, action, successor):
        # this function runs upkeep on the relevant stall stats and tries to find out
        # if the agent is stuck (same move more than 5 times)
        # prevStats is of the form: [action, position, timeSpentInPosition]
        #TODO: Fix this line
        if (action == self.prevStats[0]): #and successor == self.prevStats[1]):
            self.prevStats[2] += 1
            if (self.prevStats[2] >= 5):
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

        self.numParticles = numParticles  # TODO remember to change this back to some thing reasonable

        self.index = index

        self.numInitializedUniformly = 0

        """
        pre-processing some useful persistent objects
        """

        # set team name
        if (self.index in gameState.getRedTeamIndices()):
            self.team = "red"
        else:
            self.team = "blue"

            # create a list of form [a, b] containing the enemy indices
        if (self.index in gameState.getRedTeamIndices()):
            self.enemyIndices = gameState.getBlueTeamIndices()
        else:
            self.enemyIndices = gameState.getRedTeamIndices()

        self.legalPositions = []
        for x in range(0, 32):
            for y in range(0, 16):
                if not (gameState.hasWall(x, y)):
                    self.legalPositions.append((x, y))

            # NOTE: this is based off domain knowledge that they start in the opposite corner
        if (self.index in gameState.getRedTeamIndices()):
            self.enemyStartA = (30, 13)
            self.enemyStartB = (30, 14)
        else:
            self.enemyStartA = (1, 2)
            self.enemyStartB = (1, 1)

    def observe(self, gameState, particleListA, particleListB, stats):
        # this function takes the two noisyDistances and edits the distributions
        # NOTE: since getDistanceProb returns only 0 or 1/13 this might as well be a boolean operation
        # RETURN: this returns 4 objects, IN THIS ORDER: [particleListA, distributionA, particleListB, distributionB]
        #        it returns the distributions so they don't have to be recalculated by chooseAction(); running
        #        extra getBeliefDistribution is expensive
        # NOTE: this doesn't actually take distributionA, distributionB right now. everything runs out of the list may need to change later

        selfPosition = gameState.getAgentState(self.index).getPosition()
        noisyDistances = gameState.getAgentDistances()
        distributionA = self.getBeliefDistribution(particleListA)
        distributionB = self.getBeliefDistribution(particleListB)

        enemyDistributions = [None, None, None, None]
        enemyDistributions[self.enemyIndices[0]] = distributionA
        enemyDistributions[self.enemyIndices[1]] = distributionB

        particleLists = [None, None, None, None]
        particleLists[self.enemyIndices[0]] = particleListA
        particleLists[self.enemyIndices[1]] = particleListB

        prevThreats = [None, None, None, None]
        prevThreats[self.enemyIndices[0]] = stats["prevThreatA"]
        prevThreats[self.enemyIndices[1]] = stats["prevThreatB"]

        returnObjs = []
        for enemy in self.enemyIndices:
            distribution = enemyDistributions[enemy]
            particleList = particleLists[enemy]
            # if the enemy is in sight range
            if (gameState.getAgentPosition(enemy)):
                distribution = util.Counter()
                distribution[gameState.getAgentPosition(enemy)] = 1

            # if the enemy is not in sight range
            else:
                for state in distribution:
                    distribution[state] = distribution[state] * gameState.getDistanceProb(
                        util.manhattanDistance(selfPosition, state), noisyDistances[enemy])
                distribution.normalize()

                # test for bottoming out
                if (distribution.totalCount() == 0):
                    self.numInitializedUniformly += 1
                    # print("DISTRIBUTION FOR:", enemy, "JUST BOTTOMED OUT. #:", self.numInitializedUniformly)
                    particleList = self.initializeUniformly(particleList)
                    distribution = self.getBeliefDistribution(particleList)
                    distribution = self.antiBimodalCleaning(distribution, enemy, selfPosition)
                    for state in distribution:
                        distribution[state] = distribution[state] * gameState.getDistanceProb(
                            util.manhattanDistance(selfPosition, state), noisyDistances[enemy])
                    distribution.normalize()

            # resample for next time
            returnList = []
            i = 0
            while (i < self.numParticles):
                returnList.append(util.sample(distribution))
                i += 1
            returnObjs.append(returnList)
            returnObjs.append(distribution)

        return returnObjs

    def antiBimodalCleaning(self, origDistribution, enemy, selfPosition):
        # cleans up post-initializeUniformly distributions removings that are impossible due to knowledge of the
        # previous turn's threat analysis

        if (self.team == "red"):
            direction = 1
        else:
            direction = -1

        prevThreats = [None, None, None, None]
        prevThreats[self.enemyIndices[0]] = MyAgents.stats["prevThreatA"]
        prevThreats[self.enemyIndices[1]] = MyAgents.stats["prevThreatB"]
        distribution = origDistribution.copy()
        for state in distribution:
            if (prevThreats[enemy] < .25 and (state[0] - selfPosition[0]) * direction < 0):
                distribution[state] = 0
            elif (prevThreats[enemy] > .50 and (state[0] - selfPosition[0]) * direction > 0):
                distribution[state] = 0
        distribution.normalize()
        return distribution

    def elapseTime(self, gameState, particleList):
        # this function moves particles along in time picking evenly from all possible moves from that particle's state

        returnList = []
        i = 0
        while (i < len(particleList)):
            possiblePositions = []
            adjacents = [(particleList[i][0], particleList[i][1]), (particleList[i][0] + 1, particleList[i][1]),
                         (particleList[i][0] - 1, particleList[i][1]), (particleList[i][0], particleList[i][1] + 1),
                         (particleList[i][0], particleList[i][1] - 1)]
            for pos in adjacents:
                if not (gameState.hasWall(pos[0], pos[1])):
                    possiblePositions.append(pos)
            # selects a random particle fomr possiblePositions
            returnList.append(possiblePositions[random.randint(0, len(possiblePositions) - 1)])
            # selects a random particle fomr possiblePositions
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
            particleList = [self.enemyStartB] * self.numParticles

        return distribution, particleList