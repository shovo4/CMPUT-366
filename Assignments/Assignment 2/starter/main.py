import time
import matplotlib.pyplot as plt
import numpy as np


class PlotResults:
    """
    Class to plot the results.
    """

    def plot_results(self, data1, data2, label1, label2, filename):
        """
        This method receives two lists of data point (data1 and data2) and plots
        a scatter plot with the information. The lists store statistics about individual search
        problems such as the number of nodes a search algorithm needs to expand to solve the problem.

        The function assumes that data1 and data2 have the same size.

        label1 and label2 are the labels of the axes of the scatter plot.

        filename is the name of the file in which the plot will be saved.
        """
        _, ax = plt.subplots()
        ax.scatter(data1, data2, s=100, c="g", alpha=0.5,
                   cmap=plt.cm.coolwarm, zorder=10)

        lims = [
            np.min([ax.get_xlim(), ax.get_ylim()]),  # min of both axes
            np.max([ax.get_xlim(), ax.get_ylim()]),  # max of both axes
        ]

        ax.plot(lims, lims, 'k-', alpha=0.75, zorder=0)
        ax.set_aspect('equal')
        ax.set_xlim(lims)
        ax.set_ylim(lims)
        plt.xlabel(label1)
        plt.ylabel(label2)
        plt.grid()
        plt.savefig(filename)


class Grid:
    """
    Class to represent an assignment of values to the 81 variables defining a Sudoku puzzle.

    Variable _cells stores a matrix with 81 entries, one for each variable in the puzzle.
    Each entry of the matrix stores the domain of a variable. Initially, the domains of variables
    that need to have their values assigned are 123456789; the other domains are limited to the value
    initially assigned on the grid. Backtracking search and AC3 reduce the the domain of the variables
    as they proceed with search and inference.
    """

    def __init__(self):
        self._cells = []
        self._complete_domain = "123456789"
        self._width = 9

    def copy(self):
        """
        Returns a copy of the grid.
        """
        copy_grid = Grid()
        copy_grid._cells = [row.copy() for row in self._cells]
        return copy_grid

    def get_cells(self):
        """
        Returns the matrix with the domains of all variables in the puzzle.
        """
        return self._cells

    def get_width(self):
        """
        Returns the width of the grid.
        """
        return self._width

    def read_file(self, string_puzzle):
        """
        Reads a Sudoku puzzle from string and initializes the matrix _cells.

        This is a valid input string:

        4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......

        This is translated into the following Sudoku grid:

        - - - - - - - - - - - - -
        | 4 . . | . . . | 8 . 5 |
        | . 3 . | . . . | . . . |
        | . . . | 7 . . | . . . |
        - - - - - - - - - - - - -
        | . 2 . | . . . | . 6 . |
        | . . . | . 8 . | 4 . . |
        | . . . | . 1 . | . . . |
        - - - - - - - - - - - - -
        | . . . | 6 . 3 | . 7 . |
        | 5 . . | 2 . . | . . . |
        | 1 . 4 | . . . | . . . |
        - - - - - - - - - - - - -
        """
        i = 0
        row = []
        for p in string_puzzle:
            if p == '.':
                row.append(self._complete_domain)
            else:
                row.append(p)

            i += 1

            if i % self._width == 0:
                self._cells.append(row)
                row = []

    def print(self):
        """
        Prints the grid on the screen. Example:

        - - - - - - - - - - - - -
        | 4 . . | . . . | 8 . 5 |
        | . 3 . | . . . | . . . |
        | . . . | 7 . . | . . . |
        - - - - - - - - - - - - -
        | . 2 . | . . . | . 6 . |
        | . . . | . 8 . | 4 . . |
        | . . . | . 1 . | . . . |
        - - - - - - - - - - - - -
        | . . . | 6 . 3 | . 7 . |
        | 5 . . | 2 . . | . . . |
        | 1 . 4 | . . . | . . . |
        - - - - - - - - - - - - -
        """
        for _ in range(self._width + 4):
            print('-', end=" ")
        print()

        for i in range(self._width):

            print('|', end=" ")

            for j in range(self._width):
                if len(self._cells[i][j]) == 1:
                    print(self._cells[i][j], end=" ")
                elif len(self._cells[i][j]) > 1:
                    print('.', end=" ")
                else:
                    print(';', end=" ")

                if (j + 1) % 3 == 0:
                    print('|', end=" ")
            print()

            if (i + 1) % 3 == 0:
                for _ in range(self._width + 4):
                    print('-', end=" ")
                print()
        print()

    def print_domains(self):
        """
        Print the domain of each variable for a given grid of the puzzle.
        """
        for row in self._cells:
            print(row)

    def is_solved(self):
        """
        Returns True if the puzzle is solved and False otherwise.
        """
        for i in range(self._width):
            for j in range(self._width):
                if len(self._cells[i][j]) != 1:
                    return False
        return True


class VarSelector:
    """
    Interface for selecting variables in a partial assignment.

    Extend this class when implementing a new heuristic for variable selection.
    """

    def select_variable(self, grid):
        pass


class FirstAvailable(VarSelector):
    def select_variable(self, grid):
        # Implement here the first available heuristic
        for row in range(grid.get_width()):
            for col in range(grid.get_width()):

                if len(grid.get_cells()[row][col]) > 1: #checking for the first cell found with the largest domain
                    return (row, col) #returning the index of the cell found with the largest domain


class MRV(VarSelector):
    def select_variable(self, grid):
        # Implement here the mrv heuristic
        tupple = [] #for storing value
        minimum = 10
        for row in range(grid.get_width()):

            for col in range(grid.get_width()):
                length= len(grid.get_cells()[row][col])
                #using a heuristic that finds the cell with the smallest domain

                if length > 1: #checking if the domain > 1
                    if length < minimum: #checking if the length is smaller than the minimum value of the domain
                        tupple = (row,col)
                        minimum = length
        return tupple


class AC3:
    """
    This class implements the methods needed to run AC3 on Sudoku.
    """

    def remove_domain_row(self, grid, row, column):
        """
        Given a matrix (grid) and a cell on the grid (row and column) whose domain is of size 1 (i.e., the variable has its
        value assigned), this method removes the value of (row, column) from all variables in the same row.
        """
        variables_assigned = []

        for j in range(grid.get_width()):
            if j != column:
                new_domain = grid.get_cells()[row][j].replace(
                    grid.get_cells()[row][column], '')

                if len(new_domain) == 0:
                    return None, True

                if len(new_domain) == 1 and len(grid.get_cells()[row][j]) > 1:
                    variables_assigned.append((row, j))

                grid.get_cells()[row][j] = new_domain

        return variables_assigned, False

    def remove_domain_column(self, grid, row, column):
        """
        Given a matrix (grid) and a cell on the grid (row and column) whose domain is of size 1 (i.e., the variable has its
        value assigned), this method removes the value of (row, column) from all variables in the same column.
        """
        variables_assigned = []

        for j in range(grid.get_width()):
            if j != row:
                new_domain = grid.get_cells()[j][column].replace(
                    grid.get_cells()[row][column], '')

                if len(new_domain) == 0:
                    return None, True

                if len(new_domain) == 1 and len(grid.get_cells()[j][column]) > 1:
                    variables_assigned.append((j, column))

                grid.get_cells()[j][column] = new_domain

        return variables_assigned, False

    def remove_domain_unit(self, grid, row, column):
        """
        Given a matrix (grid) and a cell on the grid (row and column) whose domain is of size 1 (i.e., the variable has its
        value assigned), this method removes the value of (row, column) from all variables in the same unit.
        """
        variables_assigned = []

        row_init = (row // 3) * 3
        column_init = (column // 3) * 3

        for i in range(row_init, row_init + 3):
            for j in range(column_init, column_init + 3):
                if i == row and j == column:
                    continue

                new_domain = grid.get_cells()[i][j].replace(
                    grid.get_cells()[row][column], '')

                if len(new_domain) == 0:
                    return None, True

                if len(new_domain) == 1 and len(grid.get_cells()[i][j]) > 1:
                    variables_assigned.append((i, j))

                grid.get_cells()[i][j] = new_domain
        return variables_assigned, False

    def pre_process_consistency(self, grid):
        """
        This method enforces arc consistency for the initial grid of the puzzle.

        The method runs AC3 for the arcs involving the variables whose values are
        already assigned in the initial grid.
        """
        Q = [] #list for the assigned variables
        for row in range(grid.get_width()):

            for col in range(grid.get_width()):

                if len(grid.get_cells()[row][col]) == 1: #checking if the cell has only 1 domain
                    Q.append((row, col)) #storing the value in Q

        self.consistency(grid, Q) #calling consistancy here

    def consistency(self, grid, Q):
        """
        This is a domain-specific implementation of AC3 for Sudoku.

        It keeps a set of variables to be processed (Q) which is provided as input to the method.
        Since this is a domain-specific implementation, we don't need to maintain a graph and a set
        of arcs in memory. We can store in Q the cells of the grid and, when processing a cell, we
        ensure arc consistency of all variables related to this cell by removing the value of
        cell from all variables in its column, row, and unit.

        For example, if the method is used as a preprocessing step, then Q is initialized with
        all cells that start with a number on the grid. This method ensures arc consistency by
        removing from the domain of all variables in the row, column, and unit the values of
        the cells given as input. Like the general implementation of AC3, the method adds to
        Q all variables that have their values assigned during the propagation of the contraints.

        The method returns True if AC3 detected that the problem can't be solved with the current
        partial assignment; the method returns False otherwise.
        """
        while len(Q) != 0:
            var = Q.pop() #popping the position from the soduku
            row = var[0]
            col = var[1]

            #checking arc consistancy of a position for row , column and unit constraint
            remove_row, row_failure = self.remove_domain_row(grid,
                                                                row, col)
            remove_col, col_failure = self.remove_domain_column(grid,
                                                                row, col)
            remove_unit, unit_failure = self.remove_domain_unit(grid,
                                                                row, col)

            if row_failure or col_failure or unit_failure: #if arc consistancy fails returning False
                return False

            #putting the reduced domain in the list of the positions
            for row in remove_row:
                Q.append(row)

            for col in remove_col:
                Q.append(col)

            for unit in remove_unit:
                Q.append(unit)

        return True #if the position is arc consistant


class Backtracking:
    """
    Class that implements backtracking search for solving CSPs.
    """

    def search(self, grid, var_selector):
        A = AC3() #instance of function AC3

        if grid.is_solved(): #if all the cells are assigned with solution
            grid.print() #printing the solved soduku
            return grid


        var = var_selector.select_variable(grid) #either MRV or FirstAvailable for the method
        row = var[0]
        col = var[1]


        for d in grid.get_cells()[row][col]: #if unassigned variable is in the domain of the selected variable
            copy_grid = grid.copy()
            copy_grid.get_cells()[row][col] = d

            if A.consistency(copy_grid, [(row, col)]): #checking if the selected variable is  arc consisitant
                backtrack = Backtracking().search(copy_grid, var_selector) #recursion

                if backtrack is not False:
                    return backtrack

        return False


#file = open('tutorial_problem.txt', 'r')
file = open('top95.txt', 'r')
problems = file.readlines()
Runtime_MRV=[]
Runtime_FirstAvailable=[]
for p in problems:
    # Read problem from string
    g: Grid = Grid()
    g.read_file(p)

    # Print the grid on the screen
    print('Puzzle')
    g.print()
    # Print the domains of all variables
    #print('Domains of Variables')
    #g.print_domains()
    #print()



    # Make a copy of a grid
    copy_g = g.copy()
    A = AC3()
    backtrack = Backtracking()
    select = MRV()
    A.pre_process_consistency(copy_g)
    start_time = time.time()
    backtrack.search(copy_g, select)
    end_time= time.time()
    Runtime_MRV.append(end_time - start_time)

    select = FirstAvailable()
    A.pre_process_consistency(copy_g)
    start_time = time.time() #time function
    backtrack.search(copy_g, select)
    end_time = time.time()
    Runtime_FirstAvailable.append(end_time - start_time)

plotter = PlotResults()
plotter.plot_results(Runtime_MRV,Runtime_FirstAvailable,"Running Time Backtracking (MRV)","Running Time Backtracking (FA)", "running_time")
#producing plots of MRV and Firstavaible

#print('Copy (copy_g): ')
    #copy_g.print()
    #print()

    #rint('Original (g): ')
    #g.print()
    #print()

    # Removing 2 from the domain of the variable in the first row and second column
    # copy_g.get_cells()[0][1] = copy_g.get_cells()[0][1].replace('2', '')

    # The domain (0, 1) of copy_g shouldn't have 2 (first list, second element)
    #print('copy_g')
    #copy_g.print_domains()
    #print()

    # The domain of variable g shouldn't have changed though
    #print('g')
    #g.print_domains()
    #print()

    # Instance of AC3 Object


    #Making all variables in the first row arc consistent with (0, 0), whose value is 4
    #variables_assigned, failure = ac3.remove_domain_row(g, 0, 0)

    #The domain of all variables in the first row must not have 4
    #print('Removed all 4s from the first row')
    #g.print_domains()

    #variables_assigned contains all variables whose domain reduced to size 1 in the remove_domain_row opeation
    #print('Variables that were assigned by remove_domain_row: ', variables_assigned)

    #failture returns True if any of the variables in the row were reduced to size 0
    #print('Failure: ', failure)
    #print()

    #Making all variables in the first column arc consistent with (0, 0), whose value is 4
    #variables_assigned, failure = ac3.remove_domain_column(g, 0, 0)

    #The domain of all variables in the first column must not have 4
    #print('Removed all 4s from the first column')
    #g.print_domains()
    #print()

    # Making all variables in the first unit arc consistent with (0, 0), whose value is 4
    #variables_assigned, failure = ac3.remove_domain_unit(g, 0, 0)

    # The domain of all variables in the first column must not have 4
    #print('Removed all 4s from the first unit')
    #g.print_domains()
    #print()
