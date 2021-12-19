from sys import path
from tkinter import EXCEPTION
from tkinter.constants import NUMERIC
from typing import Iterable, Sized
import util
from datetime import datetime

class SearchProblem:

    def getStartState(self):

        util.raiseNotDefined()

    def isGoalState(self, state):

        util.raiseNotDefined()

    def getSuccessors(self, state):

        util.raiseNotDefined()

    def getCostOfpath(self, path):

        util.raiseNotDefined()


def tinyMazeSearch(problem):

    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s, s, w, s, w, w, s, w]


def depthFirstSearch(problem):
    from util import Stack
    startTime = datetime.now()

   
    stack = Stack()
    start = (problem.getStartState(), [], [])
    stack.push(start) 
    visited = []
    coords = []
    while not stack.isEmpty():
        (state, path, coords) = stack.pop()


        if problem.isGoalState(state):
            drawWay(coords)
            break

        visited.append(state)

        for w in problem.getSuccessors(state):
            if w[0] not in visited:
                newPath = path + [w[1]]
                newCoords = coords + [w[0]]
                stack.push((w[0], newPath, newCoords))

    endTime = datetime.now()
    print('Час виконання:', endTime - startTime)

    print('Шлях:')
    print(coords)
    print(f'Довжина шляху {len(coords)}')
    print()
    return path

def breadthFirstSearch(problem):
    from util import Queue
    startTime = datetime.now()

    visited = []
    coords = []

    queue = Queue()
    start = (problem.getStartState(), [], [])
    queue.push(start)

    while not queue.isEmpty():
        (state, path, coords) = queue.pop()

        
        if problem.isGoalState(state):

            drawWay(coords)
            break

        visited.append(state)
        for i in problem.getSuccessors(state):
            if i[0] not in visited:
                queue.push((i[0], path + [i[1]], coords + [i[0]]))

    endTime = datetime.now()
    print('Час виконання:', endTime - startTime)
    
    print('Шлях:')

    print(coords)
    print(f'Довжина шляху {len(coords)}')
    print()
    return path
def uniformCostSearch(problem):

    startTime = datetime.now()
    
    visited = []
    coords = []
    cost = []
    p_queue = util.PriorityQueue()
    p_queue.update((problem.getStartState(), [], 0, []), 0)

    while not p_queue.isEmpty():
        (node, path, cost, coords) = p_queue.pop()

        if problem.isGoalState(node):
            
            drawWay(coords)
            break

        if node not in visited:
            visited.append(node)
            for i in problem.getSuccessors(node):
                p_queue.update((i[0], path + [i[1]], cost + i[2], coords + [i[0]]), cost + i[2])

    endTime = datetime.now()
    print('Час виконання:', endTime - startTime)

    print('Шлях:')
    print(coords)
    print()
    
    print(f'Довжина шляху {len(coords)}')
    print(f'Ціна шляху {cost}')
    return path
def nullHeuristic(state, problem=None):

    return 0
def aStarSearch(problem, heuristic=nullHeuristic):

    startTime = datetime.now()
    
    visited = []
    coords = []
    cost = []
    p_queue = util.PriorityQueue()
    p_queue.update((problem.getStartState(), [], 0, []), 0)

    while not p_queue.isEmpty():
        (node, path, cost, coords) = p_queue.pop()

        
        if problem.isGoalState(node):
            
            drawWay(coords)
            break

        if node not in visited:
            visited.append(node)
            for i in problem.getSuccessors(node):

                #p_queue.update((i[0], path + [i[1]], cost + i[2], coords + [i[0]]), cost + i[2]+heuristic(i[0], problem))

                p_queue.update((i[0], path + [i[1]], cost + i[2], coords + [i[0][0]]), cost + i[2]+heuristic(i[0], problem))


    endTime = datetime.now()
    print('Час виконання:', endTime - startTime)

    print('Шлях:')
    print(coords)
    print()
    print(f'Довжина шляху {len(coords)}')
    print(f'Ціна шляху {cost}')

    return path
    
def drawWay(coords):
    import __main__
    if '_display' in dir(__main__):
        if 'drawExpandedCells' in dir(__main__._display):
            __main__._display.drawExpandedCells(coords)


bfs = breadthFirstSearch
dfs = depthFirstSearch
ucs = uniformCostSearch
astar = aStarSearch


#python pacman.py -l contestClassic -z .5 -p SearchAgent -a fn=astar,heuristic=euclideanHeuristic
#python pacman.py -l mediumMaze -z .5 -p SearchAgent -a fn=astar,heuristic=manhattanHeuristic
#python pacman.py -l mediumMaze -z .5 -p SearchAgent -a fn=astar,heuristic=greedyHeuristic

#python pacman.py -l gM4 -p SearchAgent -a fn=astar,prob=FoodSearchProblem,heuristic=foodHeuristic -z 0.5
#python pacman.py -l mediumCorners -p SearchAgent -a fn=astar,prob=CornersProblem,heuristic=cornersHeuristic -z 0.5
#python pacman.py -l mediumCorners -p SearchAgent -a fn=astar,prob=FoodSearchProblem,heuristic=foodHeuristic -z 0.5