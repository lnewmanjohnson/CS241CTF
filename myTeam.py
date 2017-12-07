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
               first='TestAgent', second='TestAgent'):
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

class TestAgent(CaptureAgent):
    """
    A Dummy agent to serve as an example of the necessary agent structure.
    You should look at baselineTeam.py for more details about how to
    create an agent as this is the bare minimum.
    """

    beliefs = util.Counter()  # Keep track of beliefs about location of opponents (tuple of 2 positions with prob)
    agents = [0, 0, 0, 0]

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
        self.safety_score = 100

    def chooseAction(self, gameState):
        """
        Picks among actions randomly.
        """

        #teammate_index = (self.index + 2) % 4
        #teammate = gameState.getAgentState(teammate_index)

        # TODO: Update beliefs based on new observations and possible moves

        time.sleep(0.2)

        if TestAgent.agents[self.index] == 0:
            print("Agent %d: Searching" % self.index)
            return self.search(gameState)
        elif TestAgent.agents[self.index] == 1:
            print("Agent %d: Delivering" % self.index)
            return self.deliver_food(gameState)

    def update_safety_score(self, gameState):
        self.safety_score = self.get_safety_score(gameState)

    def get_safety_score(self, gameState):
        my_pos = gameState.getAgentPosition(self.index)
        safety_score = 100
        if(my_pos[0] > 16 and gameState.getAgentState(self.index).scaredTimer == 0):
            return safety_score
        else:
            opps_index = [(self.index + 1) % 4, (self.index + 3) % 4]
            for opp in opps_index:
                opp_state = gameState.getAgentState(opp)
                opp_timer = opp_state.scaredTimer
                opp_pos = gameState.getAgentPosition(opp)
                if opp_pos is not None and (opp_pos[0]-16) < (16 - my_pos[0]):
                    safety_score -= 10 * self.getMazeDistance(my_pos, opp_pos)
            return safety_score

    def search(self, gameState):
        """
        Offense 1: Aggressively searches for food, avoiding ghosts
        """
        def evaluate(self, gameState, action):
            score = 0.0
            successor = self.getSuccessor(gameState, action)
            newPos = successor.getAgentState(self.index).configuration.pos
            if (successor.getAgentState(self.index).numCarrying > gameState.getAgentState(self.index).numCarrying):
                score += 50

            for food in self.getFood(successor).asList():
                score += 10.0 / self.getMazeDistance(newPos, food)

            for index in self.getOpponents(gameState):
                ghost = successor.getAgentState(index)
                opp_pos = successor.getAgentPosition(index)
                if (ghost.scaredTimer > 6 and opp_pos is not None):
                    print(ghost.scaredTimer)
                    score += 100/self.getMazeDistance(newPos, opp_pos)

            score -= len(self.getFood(successor).asList())/10
            score -= self.get_safety_score(successor)
            return score

        self.update_safety_score(gameState)
        if(self.safety_score < 50):
            TestAgent.agents[self.index] = 1
            return self.deliver_food(gameState)

        carrying = gameState.getAgentState(self.index).numCarrying
        if (carrying > 6 or self.safety_score < 50):
            return self.deliver_food(gameState)
        # elif(other_checks): return other)subroutine2(gameState)
        else:
            actions = gameState.getLegalActions(self.index)
            best_action = actions[0]
            best_score = -9999

            for action in actions:
                score = evaluate(self, gameState, action)
                if (score > best_score):
                    best_score = score
                    best_action = action

        return best_action

    def deliver_food(self, gameState):
        """
        Offense 2: Return food to safety
        """

        def evaluate(self, gameState, action):
            score = 0.0
            successor = self.getSuccessor(gameState, action)
            newPos = successor.getAgentState(self.index).configuration.pos
            if(newPos[0] > 16):
                return 10
            safety_spots = [(17, i) for i in [1, 3, 4, 6, 7, 8, 10, 14]]
            for pos in safety_spots:
                score += 10.0 / (self.getMazeDistance(newPos, pos) ** 2)
            score -= self.get_safety_score(successor)/10
            return score

        self.update_safety_score(gameState)
        carrying = gameState.getAgentState(self.index).numCarrying
        if (carrying < 6 and self.safety_score > 60):
            TestAgent.agents[self.index] = 0
            return self.search(gameState)
        else:
            actions = gameState.getLegalActions(self.index)
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
