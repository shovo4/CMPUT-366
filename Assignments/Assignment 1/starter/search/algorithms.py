

import heapq
import time

class State:
    """
    Class to represent a state on grid-based pathfinding problems. The class contains two static variables:
    map_width and map_height containing the width and height of the map. Although these variables are properties
    of the map and not of the state, they are used to compute the hash value of the state, which is used
    in the CLOSED list.

    Each state has the values of x, y, g, h, and cost. The cost is used as the criterion for sorting the nodes
    in the OPEN list for both Dijkstra's algorithm and A*. For Dijkstra the cost should be the g-value, while
    for A* the cost should be the f-value of the node.
    """
    map_width = 0
    map_height = 0

    def __init__(self, x, y):
        """
        Constructor - requires the values of x and y of the state. All the other variables are
        initialized with the value of 0.
        """
        self._x = x
        self._y = y
        self._g = 0
        self._h = 0
        self._cost = 0

    def __repr__(self):
        """
        This method is invoked when we call a print instruction with a state. It will print [x, y],
        where x and y are the coordinates of the state on the map.
        """
        state_str = "[" + str(self._x) + ", " + str(self._y) + "]"
        return state_str

    def __lt__(self, other):
        """
        Less-than operator; used to sort the nodes in the OPEN list
        """
        return self._cost < other._cost

    def state_hash(self):
        """
        Given a state (x, y), this method returns the value of x * map_width + y. This is a perfect
        hash function for the problem (i.e., no two states will have the same hash value). This function
        is used to implement the CLOSED list of the algorithms.
        """
        return self._y * State.map_width + self._x

    def __eq__(self, other):
        """
        Method that is invoked if we use the operator == for states. It returns True if self and other
        represent the same state; it returns False otherwise.
        """
        return self._x == other._x and self._y == other._y

    def get_x(self):
        """
        Returns the x coordinate of the state
        """
        return self._x

    def get_y(self):
        """
        Returns the y coordinate of the state
        """
        return self._y

    def get_g(self):
        """
        Returns the g-value of the state
        """
        return self._g

    def get_h(self):
        """
        Returns the h-value of the state
        """
        return self._h

    def get_cost(self):
        """
        Returns the cost of the state (g for Dijkstra's and f for A*)
        """
        return self._cost

    def set_g(self, cost):
        """
        Sets the g-value of the state
        """
        self._g = cost

    def set_h(self, h):
        """
        Sets the h-value of the state
        """
        self._h = h

    def set_cost(self, cost):
        """
        Sets the cost of a state (g for Dijkstra's and f for A*)
        """
        self._cost = cost

class Search:
    """
    Interface for a search algorithm. It contains an OPEN list and a CLOSED list.

    The OPEN list is implemented with a heap, which can be done with the library heapq
    (https://docs.python.org/3/library/heapq.html).

    The CLOSED list is implemented as a dictionary where the state hash value is used as key.
    """
    def __init__(self, gridded_map):
        self.map = gridded_map
        self.OPEN = []
        self.CLOSED = {}

    def search(self, start, goal):
        """
        Search method that needs to be implemented (either Dijkstra or A*).
        """
        raise NotImplementedError()

class Dijkstra(Search):

    def search(self, start, goal):
        """
        Disjkstra's Algorithm: receives a start state and a goal state as input. It returns the
        cost of a path between start and goal and the number of nodes expanded.

        If a solution isn't found, it returns -1 for the cost.
        """
        self.OPEN=[]
        self.CLOSED={}
        heapq.heapify(self.OPEN) #heapifying self.OPEN
        heapq.heappush(self.OPEN,start) #getting the start node in OPEN
        self.CLOSED[State.state_hash(start)] = start #CLOSED is a dictionary thats why getting the start node in CLOSED in this way
        node_expanded = 0

        while len(self.OPEN) != 0: #while open is not empty
            n = heapq.heappop(self.OPEN) #getting n from self.OPEN
            node_expanded += 1

            if State.__eq__(n,goal): #if n equal to goal
                print(self.CLOSED[State.state_hash(n)].get_g()) #printing cost of g
                return self.CLOSED[State.state_hash(n)].get_g(),node_expanded #returning g value in self.CLOSED and increasing node_expanded

            for m in self.map.successors(n): #checking if m in T(n)
                State.set_cost(m, State.get_g(m))
                if State.state_hash(m) not in self.CLOSED: #if m not in self.CLOSED
                    heapq.heappush(self.OPEN, m) #getting m in self.OPEN
                    self.OPEN[self.OPEN.index(m)].set_cost(State.get_g(m))
                    heapq.heapify(self.OPEN)
                    self.CLOSED[State.state_hash(m)] = m

                if (State.state_hash(m) in self.CLOSED and (State.get_cost(m)) < self.CLOSED[State.state_hash(m)].get_cost()):
                    self.CLOSED[State.state_hash(m)].set_g(State.get_g(m))
                    self.CLOSED[State.state_hash(m)].set_cost(State.get_cost(m))

        return -1,0

class AStar(Search):

    def h_value(self, state, goal):
        h = max(abs(state.get_x() - goal.get_x()), abs(state.get_y() - goal.get_y())) + 0.5*min(abs(state.get_x() - goal.get_x()), abs(state.get_y()-goal.get_y()))
        return h

    def search(self, start, goal):
        """
        A* Algorithm: receives a start state and a goal state as input. It returns the
        cost of a path between start and goal and the number of nodes expanded.

        If a solution isn't found, it returns -1 for the cost.
        """
        self.OPEN = []
        self.CLOSED = {}
        self.CLOSED[State.state_hash(start)] = start
        heapq.heapify(self.OPEN)
        #State.set_cost(start, start.get_g() + self.h_value(start, goal))
        heapq.heappush(self.OPEN, start)
        node_expanded = 0
        while len(self.OPEN) != 0:
            n = heapq.heappop(self.OPEN)
            node_expanded += 1
            #self.CLOSED[State.state_hash(n)] = n
            if State.__eq__(n, goal):
                print(self.CLOSED[State.state_hash(n)].get_g())
                return self.CLOSED[State.state_hash(n)].get_g(), node_expanded

            for m in self.map.successors(n):
                State.set_h(m, self.h_value(m, goal))
                State.set_cost(m, State.get_g(m) + State.get_h(m))
                if State.state_hash(m) in self.CLOSED and self.CLOSED[State.state_hash(m)].get_cost() > State.get_cost(m):
                    self.CLOSED[State.state_hash(m)].set_cost(State.get_cost(m))
                    self.CLOSED[State.state_hash(m)].set_g(State.get_g(m))
                    self.CLOSED[State.state_hash(m)].set_h(State.get_h(m))

                if State.state_hash(m) not in self.CLOSED:
                    heapq.heappush(self.OPEN, m)
                    self.CLOSED[State.state_hash(m)] = m
                    heapq.heapify(self.OPEN)

        return -1, 0
