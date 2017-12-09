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
               first='OffensiveReflexAgent', second='OffensiveReflexAgent'):
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


class ReflexCaptureAgent(CaptureAgent):
    """
    A base class for reflex agents that chooses score-maximizing actions
    """
    agents = [0, 0, 0, 0]

    def registerInitialState(self, gameState):
        self.start = gameState.getAgentPosition(self.index)
        CaptureAgent.registerInitialState(self, gameState)

    def chooseAction(self, gameState):
        """
        Picks among the actions with the highest Q(s,a).
        """
        time.sleep(0.02)
        actions = gameState.getLegalActions(self.index)

        # You can profile your evaluation time by uncommenting these lines
        # start = time.time()
        values = [self.evaluate(gameState, a) for a in actions]
        # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

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
            return bestAction

        return random.choice(bestActions)

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

    def evaluate(self, gameState, action):
        """
        Computes a linear combination of features and feature weights
        """
        features = self.getFeatures(gameState, action)
        weights = self.getWeights(gameState, action)
        print("Value: " + str(features * weights))
        return features * weights

    def getFeatures(self, gameState, action):
        """
        Returns a counter of features for the state
        """
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        features['successorScore'] = self.getScore(successor)
        return features

    def getWeights(self, gameState, action):
        """
        Normally, weights do not depend on the gamestate.  They can be either
        a counter or a dictionary.
        """
        return {'successorScore': 1.0}


class OffensiveReflexAgent(ReflexCaptureAgent):
    """
    A reflex agent that seeks food. This is an agent
    we give you to get an idea of what an offensive agent might look like,
    but it is by no means the best or only way to build an offensive agent.
    """
    agents = [0, 0, 0, 0]

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
                        opp_state.isPacman and myState.scaredTimer > 0): #and (opp_pos[0] - 16) < (16 - myPos[0]):
                    distance = self.getMazeDistance(myPos, opp_pos)
                    if distance > opp_timer and distance <= 6:
                        safety_score -= 150 / distance

        print(safety_score)
        return safety_score

    def getFeatures(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        myState = successor.getAgentState(self.index)
        myPos = successor.getAgentPosition(self.index)
        foodList = self.getFood(successor).asList()
        safetyScore = self.getSafetyScore(successor)
        if safetyScore > 50 and len(foodList) > 2:
            features['successorScore'] = -len(foodList) + safetyScore
            opps_index = [(self.index + 1) % 4, (self.index + 3) % 4]
            for opp in opps_index:
                opp_state = successor.getAgentState(opp)
                opp_timer = opp_state.scaredTimer
                opp_pos = successor.getAgentPosition(opp)
                if opp_pos is not None:
                    distance = self.getMazeDistance(myPos, opp_pos)
                    if distance <= 6 and (opp_state.isPacman or opp_timer > distance):
                        features['successorScore'] += 10/distance
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

        if len(foodList) > 0:  # This should always be True,  but better safe than sorry
            myPos = successor.getAgentState(self.index).getPosition()
            minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
            features['distanceToFood'] = minDistance
        return features

    def getWeights(self, gameState, action):
        return {'successorScore': 100, 'distanceToFood': -1}
