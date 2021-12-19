from util import manhattanDistance
from game import Directions
import random, util

from game import Agent


def scoreEvaluationFunction(currentGameState):
    
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    

    def __init__(self, evalFn = 'betterEvaluationFunction', depth = '4'):
        self.index = 0 
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)



class AlphaBetaAgent(MultiAgentSearchAgent):
    

    def getAction(self, gameState):
        
        PACMAN = 0
        def max_agent(state, depth, alpha, beta):
            if state.isWin() or state.isLose():
                return state.getScore()
            actions = state.getLegalActions(PACMAN)
            best_score = float("-inf")
            score = best_score
            best_action = Directions.STOP
            for action in actions:
                score = min_agent(state.generateSuccessor(PACMAN, action), depth, 1, alpha, beta)
                if score > best_score:
                    best_score = score
                    best_action = action
                alpha = max(alpha, best_score)
                if best_score > beta:
                    return best_score
            if depth == 0:
                return best_action
            else:
                return best_score

        def min_agent(state, depth, ghost, alpha, beta):
            if state.isLose() or state.isWin():
                return state.getScore()
            next_ghost = ghost + 1
            if ghost == state.getNumAgents() - 1:
                
                next_ghost = PACMAN
            actions = state.getLegalActions(ghost)
            best_score = float("inf")
            score = best_score
            for action in actions:
                if next_ghost == PACMAN: 
                    if depth == self.depth - 1:
                        score = self.evaluationFunction(state.generateSuccessor(ghost, action))
                    else:
                        score = max_agent(state.generateSuccessor(ghost, action), depth + 1, alpha, beta)
                else:
                    score = min_agent(state.generateSuccessor(ghost, action), depth, next_ghost, alpha, beta)
                if score < best_score:
                    best_score = score
                beta = min(beta, best_score)
                if best_score < alpha:
                    return best_score
            return best_score
        return max_agent(gameState, 0, float("-inf"), float("inf"))

class ExpectimaxAgent(MultiAgentSearchAgent):
  

    def getAction(self, gameState):
        
        pacman_legal_actions = gameState.getLegalActions(0) #Доступные движения пакмана
        max_value = float('-inf')
        max_action  = None 

        for action in pacman_legal_actions:   
            action_value = self.Min_Value(gameState.generateSuccessor(0, action), 1, 0)
            if ((action_value) > max_value ): 
                max_value = action_value
                max_action = action

        return max_action 

    def Max_Value (self, gameState, depth):
        

        if ((depth == self.depth)  or (len(gameState.getLegalActions(0)) == 0)):
            return self.evaluationFunction(gameState)

        return max([self.Min_Value(gameState.generateSuccessor(0, action), 1, depth) for action in gameState.getLegalActions(0)])


    def Min_Value (self, gameState, agentIndex, depth):
        

        num_actions = len(gameState.getLegalActions(agentIndex))

        if (num_actions == 0): 
            return self.evaluationFunction(gameState)

        if (agentIndex < gameState.getNumAgents() - 1):
            return sum([self.Min_Value(gameState.generateSuccessor(agentIndex, action), agentIndex + 1, depth) for action in gameState.getLegalActions(agentIndex)]) / float(num_actions)

        else:  
            return sum([self.Max_Value(gameState.generateSuccessor(agentIndex, action), depth + 1) for action in gameState.getLegalActions(agentIndex)]) / float(num_actions)

def betterEvaluationFunction(currentGameState):
    
    def closest_dot(cur_pos, food_pos):
        food_distances = []
        for food in food_pos:
            food_distances.append(util.manhattanDistance(food, cur_pos))
        return min(food_distances) if len(food_distances) > 0 else 1

    def closest_ghost(cur_pos, ghosts):
        food_distances = []
        for food in ghosts:
            food_distances.append(util.manhattanDistance(food.getPosition(), cur_pos))
        return min(food_distances) if len(food_distances) > 0 else 1


    

    def food_stuff(cur_pos, food_positions):
        food_distances = []
        for food in food_positions:
            food_distances.append(util.manhattanDistance(food, cur_pos))
        return sum(food_distances)


    pacman_pos = currentGameState.getPacmanPosition()
    score = currentGameState.getScore()
    food = currentGameState.getFood().asList()
    ghosts = currentGameState.getGhostStates()

    score = score * 3 if closest_dot(pacman_pos, food) < closest_ghost(pacman_pos, ghosts) + 2 else score
    score -= .35 * food_stuff(pacman_pos, food)
    return score

better = betterEvaluationFunction


def contestEvaluationFunc(currentGameState):
   
    def closest_dot(cur_pos, food_pos):
        food_distances = []
        for food in food_pos:
            food_distances.append(util.manhattanDistance(food, cur_pos))
        return min(food_distances) if len(food_distances) > 0 else 1

    def closest_ghost(cur_pos, ghosts):
        food_distances = []
        for food in ghosts:
            food_distances.append(util.manhattanDistance(food.getPosition(), cur_pos))
        return min(food_distances) if len(food_distances) > 0 else 1


    

    def food_stuff(cur_pos, food_positions):
        food_distances = []
        for food in food_positions:
            food_distances.append(util.manhattanDistance(food, cur_pos))
        return sum(food_distances)

    

    def closest_capsule(cur_pos, caps_pos):
        capsule_distances = []
        for caps in caps_pos:
            capsule_distances.append(util.manhattanDistance(caps, cur_pos))
        return min(capsule_distances) if len(capsule_distances) > 0 else 9999999

    def scaredghosts(ghost_states, cur_pos, scores):
        scoreslist = []
        for ghost in ghost_states:
            if ghost.scaredTimer > 8 and util.manhattanDistance(ghost.getPosition(), cur_pos) <= 4:
                scoreslist.append(scores + 50)
            if ghost.scaredTimer > 8 and util.manhattanDistance(ghost.getPosition(), cur_pos) <= 3:
                scoreslist.append(scores + 60)
            if ghost.scaredTimer > 8 and util.manhattanDistance(ghost.getPosition(), cur_pos) <= 2:
                scoreslist.append(scores + 70)
            if ghost.scaredTimer > 8 and util.manhattanDistance(ghost.getPosition(), cur_pos) <= 1:
                scoreslist.append(scores + 90)
        return max(scoreslist) if len(scoreslist) > 0 else scores

    def ghostattack(ghost_states, cur_pos, scores):
        scoreslist = []
        for ghost in ghost_states:
            if ghost.scaredTimer == 0:
                scoreslist.append(scores - util.manhattanDistance(ghost.getPosition(), cur_pos) - 10)
        return max(scoreslist) if len(scoreslist) > 0 else scores

    def scoreagent(cur_pos, food_pos, ghost_states, caps_pos, score):
        if closest_capsule(cur_pos, caps_pos) < closest_ghost(cur_pos, ghost_states):
            return score + 40
        if closest_dot(cur_pos, food_pos) < closest_ghost(cur_pos, ghost_states) + 3:
            return score + 20
        if closest_capsule(cur_pos, caps_pos) < closest_dot(cur_pos, food_pos) + 3:
            return score + 30
        else:
            return score


    capsule_pos = currentGameState.getCapsules()
    pacman_pos = currentGameState.getPacmanPosition()
    score = currentGameState.getScore()
    food = currentGameState.getFood().asList()
    ghosts = currentGameState.getGhostStates()

    #score = score * 2 if closest_dot(pacman_pos, food) < closest_ghost(pacman_pos, ghosts) + 3 else score
    #score = score * 1.5 if closest_capsule(pacman_pos, capsule_pos) < closest_dot(pacman_pos, food) + 4 else score
    score = scoreagent(pacman_pos, food, ghosts, capsule_pos, score)
    score = scaredghosts(ghosts, pacman_pos, score)
    score = ghostattack(ghosts, pacman_pos, score)
    score -= .35 * food_stuff(pacman_pos, food)
    return score