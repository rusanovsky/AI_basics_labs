from game import Directions
from game import Agent
from game import Actions
import util
import time
import search
from random import randrange
class GoWestAgent(Agent):

    def getAction(self, state):
        if Directions.WEST in state.getLegalPacmanActions():
            return Directions.WEST
        else:
            return Directions.STOP



class SearchAgent(Agent):

    def __init__(self, fn='depthFirstSearch', prob='PositionSearchProblem', heuristic='nullHeuristic'):
        self.fn = fn
        if fn not in dir(search):
            raise AttributeError(fn + ' is not a search function in search.py.')
        func = getattr(search, fn)
        if 'heuristic' not in func.__code__.co_varnames:
            print(('[SearchAgent] using function ' + fn))
            self.searchFunction = func
        else:
            if heuristic in list(globals().keys()):
                heur = globals()[heuristic]
            elif heuristic in dir(search):
                heur = getattr(search, heuristic)
            else:
                raise AttributeError(heuristic + ' is not a function in searchAgents.py or search.py.')
            print(('[SearchAgent] using function %s and heuristic %s' % (fn, heuristic)))
            self.searchFunction = lambda x: func(x, heuristic=heur)

        if prob not in list(globals().keys()) or not prob.endswith('Problem'):
            raise AttributeError(prob + ' is not a search problem type in SearchAgents.py.')
        self.searchType = globals()[prob]
        print(('[SearchAgent] using problem type ' + prob))

    def registerInitialState(self, state):

        if self.searchFunction == None: raise Exception("No search function provided for SearchAgent")
        starttime = time.time()
        problem = self.searchType(state) 
        self.actions  = self.searchFunction(problem)
        totalCost = problem.getCostOfActions(self.actions)
        print(('Path found with total cost of %d in %.1f seconds' % (totalCost, time.time() - starttime)))
        if '_expanded' in dir(problem): print(('Search nodes expanded: %d' % problem._expanded))

    def getAction(self, state):

        if 'actionIndex' not in dir(self): self.actionIndex = 0
        i = self.actionIndex
        self.actionIndex += 1
        try:
            if i < len(self.actions):
                return self.actions[i]
            else:
                return Directions.STOP
        except TypeError:
            print("Exception: "+ self.fn + " did not return a list")
            exit()

class PositionSearchProblem(search.SearchProblem):


    def __init__(self, gameState, costFn = lambda x: 1, goal=(1,1), start=None, warn=True, visualize=True):

        self.walls = gameState.getWalls()
        self.startState = gameState.getPacmanPosition()
        if start != None: self.startState = start
        self.goal = goal
        self.costFn = costFn
        self.visualize = visualize

        self._visited, self._visitedlist, self._expanded = {}, [], 0

    def getStartState(self):
        return self.startState

    def isGoalState(self, state):
        isGoal = state == self.goal

        return isGoal

    def getSuccessors(self, state):
        successors = []
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x,y = state
            dx, dy = Actions.directionToVector(action)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                nextState = (nextx, nexty)
                cost = self.costFn(nextState)
                successors.append( ( nextState, action, cost) )


        return successors

    def getCostOfActions(self, actions):
        if actions == None: return 999999
        x,y= self.getStartState()
        cost = 0
        for action in actions:
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]: return 999999
            cost += self.costFn((x,y))
        return cost



def manhattanHeuristic(position, problem):
    xy1 = position
    xy2 = problem.goal
    return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])

def euclideanHeuristic(position, problem):
    xy1 = position
    xy2 = problem.goal
    return ((xy1[0] - xy2[0]) ** 2 + (xy1[1] - xy2[1]) ** 2) ** 0.5

def greedyHeuristic(position, problem):
    xy1 = position
    xy2 = problem.goal
    return (xy1[0] - xy2[0]) ** 2 + (xy1[1] - xy2[1]) ** 2

def foodHeuristic(state, problem):
    position, foodGrid = state
    food = foodGrid.asList()

    if len(food) == 0:
        return 0

    val = []
    for s in food:
        val.append(abs(s[0]- state[0][0]) + abs(s[1] -state[0][1]))
    return max(val)

def cornersHeuristic(state, problem):
    corners = problem.corners
    walls = problem.walls 

    coordinates = state[0]
    visited_corners = state[1]
    unvisited_corners = []

    for one_corner in corners:
        if not one_corner in visited_corners:
            unvisited_corners.append(one_corner)

    heuristic_number = 0
        
    while len(unvisited_corners) != 0: 
        manhattan_distances = []
        for each_corner in unvisited_corners:
            get_manhattan = util.manhattanDistance(coordinates, each_corner)
            manhattan_corner = (get_manhattan, each_corner)
            manhattan_distances.append(manhattan_corner)
        minimum, the_corner = min(manhattan_distances)
        coordinates = the_corner
        heuristic_number += minimum
        unvisited_corners.remove(the_corner)
            
    return heuristic_number

class CornersProblem(search.SearchProblem):
 
    def __init__(self, startingGameState):
  
        self.walls = startingGameState.getWalls()
        self.startingPosition = startingGameState.getPacmanPosition()
        top, right = self.walls.height-2, self.walls.width-2
        self.corners = ((1,1), (1,top), (right, 1), (right, top))
        for corner in self.corners:
            if not startingGameState.hasFood(*corner):
                print('Warning: no food in corner ' + str(corner))
        self._expanded = 0 
        self.costFn = lambda x,y: 1
        


    def getStartState(self):
        corner_foods = []
        return (self.startingPosition, corner_foods)


    def isGoalState(self, state):
        position = state[0]
        corner_foods = state[1]
        return len(corner_foods) == 4


    def getSuccessors(self, state):

        
        successors = []
        
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x, y = state[0]
            suc_corners = []
            visited_corners = state[1]
            dx, dy = Actions.directionToVector(action)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                next_state = (nextx, nexty)
                
                for each in visited_corners:
                    suc_corners.append(each)
                
                if next_state in self.corners:
                    if next_state not in suc_corners:
                        suc_corners.append(next_state)
                cost = self.costFn(nextx, nexty)
                successors.append( ((next_state, suc_corners), action, cost) )

            
        self._expanded += 1 
        return successors

    def getCostOfActions(self, actions):

        if actions == None: return 999999
        x,y= self.startingPosition 
        cost = 0

        for action in actions:
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy) 
            if self.walls[x][y]: return 999999
            cost += self.costFn(x,y) 
        return cost



    

class FoodSearchProblem(search.SearchProblem):

    example = True
    def __init__(self, startingGameState):
        self.start = (startingGameState.getPacmanPosition(), startingGameState.getFood())
        self.walls = startingGameState.getWalls()
        self.startingGameState = startingGameState
        self._expanded = 0
        self.heuristicInfo = {}

    def getStartState(self):
        return self.start

    def isGoalState(self, state):
        return state[1].count() == 0

    def getSuccessors(self, state):
        successors = []
        self._expanded += 1 
        for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x, y = state[0]
            dx, dy = Actions.directionToVector(direction)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                nextFood = state[1].copy()
                nextFood[nextx][nexty] = False
                successors.append((((nextx, nexty), nextFood), direction, 1))
        return successors

    def getCostOfActions(self, actions):
        x, y = self.getStartState()[0]
        cost = 0
        for action in actions:
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            cost += 1
        return cost
def mazeDistance(point1, point2, gameState):

    x1, y1 = point1
    x2, y2 = point2
    walls = gameState.getWalls()
    assert not walls[x1][y1], 'point1 is a wall: ' + str(point1)
    assert not walls[x2][y2], 'point2 is a wall: ' + str(point2)
    prob = PositionSearchProblem(gameState, start=point1, goal=point2, warn=False, visualize=False)
    return len(search.bfs(prob))
