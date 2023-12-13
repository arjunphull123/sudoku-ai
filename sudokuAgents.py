"""
sudokuAgents.py

Author: Arjun Phull
Course: ISTA 450, Fall 2023
Date: 13 December 2023
"""

import random, time
import numpy as np
from tqdm import tqdm

class SudokuGame:
    """Defines a 9x9 Sudoku game to be solved.
    """
    def __init__(self, board=None):
        if board is None:  # generate an empty board
            board = np.full((9, 9), "_")

        self.board = board  # game board
        self.candidates = {}  # for use in constraintProp
        self.editableCells = set()  # to keep track of givens versus blanks

        # initialize candidates dictionary and editable cells
        for i in range(9):
            for j in range(9):
                cell = (i,j)  # tupled position, iterating across the board
                value = self.getValue(cell)  # value at that slot

                if value == '_':  # if this is an empty value
                    self.candidates[cell] = self.getCandidates(cell)  # calculate the candidates
                    self.editableCells.add(cell)  # add it to the editableCells set
                else:
                    self.candidates[cell] = [value]  # the only candidate for this cell is its value

    def getCandidates(self, cell):
        """Traverses the row, column, and subgrid of a cell, and returns
        the possible values for that cell according to Sudoku rules.

        :param cell: a tuple (i, j)
        :return: a list of possible values for the given cell
        """
        possible = list(range(1,10))  # initialize possible values as all digits
        i, j = cell

        for k in range(9):  # iterate across rows and columns
            # eliminate row dupes:
            if self.getValue((i, k)) in possible:
                possible.remove(self.getValue((i, k)))

            # eliminate column dupes:
            if self.getValue((k, j)) in possible:
                possible.remove(self.getValue((k, j)))

            # eliminate subgrid dupes:
            r, c = self.getWhichSubgrid(cell)
            for row in range(r, r+3):
                for col in range(c, c+3):
                    if self.getValue((row, col)) in possible:
                        possible.remove(self.getValue((row, col)))

        return possible


    def getValue(self, cell):
        """Returns the value of a cell.

        :param cell: a tuple (i, j)
        :return: the board's value at that cell.
        """
        i, j = cell
        return self.board[i][j]

    def printBoard(self):
        """Prints the board to the console.
        """
        for i in self.board:
            for j in i[:-1]:
                print(f" {j} ", end='')
            print(f" {i[-1]}")

    def getWhichSubgrid(self, cell):
        """Given a cell, returns the upper-left corner of the cell's subgrid.

        :param cell: a tuple (i, j)
        :return: the upper-left corner of the cell's subgrid.
        """
        i, j = cell
        return ((i // 3)*3 , (j // 3)*3)

    def conflicts(self, cell, value):
        """Calculates the number of conflicts across rows, columns, and subgrids,
        that result from assigning a value to a cell.

        :param cell: a tuple (i, j)
        :param value: an integer value between 1 and 9
        :return: the number of conflicts caused by assigning value to cell.
        """
        row, col = cell
        numConflicts = 0  # initialize no conflicts

        # check for row and column conflicts
        for i in range(9):
            # check for a row conflict
            if self.board[row][i] == value and i != col:
                numConflicts += 1

            # check for a column conflict
            if self.board[i][col] == value and i != row:
                numConflicts += 1

        # check for subgrid conflicts
        row_start = (row // 3) * 3
        col_start = (col // 3) * 3

        for i in range(row_start, row_start + 3):
            for j in range(col_start, col_start + 3):
                if self.board[i][j] == value and not (i == row and j == col):
                    numConflicts += 1

        return numConflicts

    def totalConflicts(self):
        """Calculates the total number of conflicts on the board.

        :return: total number of conflicts.
        """
        total = 0
        for i in range(9):
            for j in range(9):
                # iterating across the board
                value = self.board[i][j]
                total += self.conflicts((i, j), value)

        return total

    def isComplete(self):
        """Returns False if there are empty values on the board, True otherwise.
        """
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == '_':
                    return False

        return True

## util - for board generation

def redactCells(board, k):
    """Removes k values from a complete Sudoku board.

    :param board: a 9x9 array
    :param k: the number of values to remove
    :return: a partial Sudoku board.
    """
    newBoard = board.copy().astype(object)  # create a deep copy
    cellsToBlock = set()  # initialize a list of cells to remove
    while len(cellsToBlock) < k:
        # add a random cell
        cellsToBlock.add((random.randint(0,8), random.randint(0,8)))

    for cell in cellsToBlock:
        # erase each cell in cellsToBlock
        i, j = cell
        newBoard[i][j] = '_'

    return newBoard

## solver algorithms

def minConflicts(game, maxSteps=1000, plateauThreshold=10, printOutput=True):
    """Randomly assigns values to a partial Sudoku board. Then, iteratively selects
    a random cell and assigns it to the value that minimizes total conflicts. Returns
    after a maximum number of iterations or if the solution is found.

    :param game: SudokuGame
    :param maxSteps: maximum number of iterations, defaults to 1000
    :param plateauThreshold: threshold for re-randomizing the board, defaults to 10
    :param printOutput: whether to print to the console, defaults to True
    :return: a list of the number of conflicts at each step.
    """
    # initially, assign random values to each editable cell
    for cell in game.editableCells:
        i, j = cell
        game.board[i][j] = random.randint(1,9)

    # storage variables
    plateauTracker = 0
    conflictsLog = []

    for step in tqdm(range(maxSteps), desc="minConflicts"):  # iterate for maxSteps
        # if steps are not improving conflicts
        if plateauTracker > plateauThreshold:
            # re-randomize editable cells
            for cell in game.editableCells:
                i, j = cell
                game.board[i][j] = random.randint(1,9)

        # log the number of conflicts at this step
        conflictsLog.append(game.totalConflicts())

        # if a solution is found
        if game.totalConflicts() == 0:
            if printOutput:
                print(f"Solved the board in {step} steps.")
                game.printBoard()
            return conflictsLog

        # otherwise, assemble a list of conflicting cells
        conflictingCells = []

        for cell in game.editableCells:
            numConflicts = game.conflicts(cell, game.getValue(cell))
            if numConflicts > 0:
                conflictingCells.append(cell)

        # now, choose a conflicting cell at random
        var = random.choice(conflictingCells)
        i, j = var
        conflictsFromValues = {}
        currentConflicts = game.totalConflicts()

        # find the value that minimizes conflicts
        for value in range(1,10):
            game.board[i][j] = value
            conflictsFromValues[value] = game.totalConflicts()

        game.board[i][j] = "_"
        leastConflicts = min(conflictsFromValues.values())
        bestValues = [value for value in conflictsFromValues \
                      if conflictsFromValues[value] == leastConflicts]

        # randomly break ties
        bestValue = random.choice(bestValues)

        # and assign the cell
        game.board[i][j] = bestValue

        # if this didn't improve the situation
        if game.totalConflicts() >= currentConflicts:
            plateauTracker += 1
        else:
            plateauTracker = 0

    # if this point is reached, no solution was found :(
    if printOutput:
        print("Max steps reached.")

    return conflictsLog

def backtrackingSearch(game, printOutput=True):
    """Implements backtracking search to solve a Sudoku game.

    :param game: SudokuGame
    :param printOutput: whether to print to the console, defaults to True
    :return: the found solution, if there is one, and the time elapsed
    """
    start = time.time()
    result = backtrack(game, 0, printOutput)
    end = time.time()
    return result, end-start


def backtrack(game, step, printOutput):
    """Recursive helper function for backtracking.

    :param game: SudokuGame
    :param step: current iteration
    :param printOutput: whether to print to the console
    :return: the found solution, if there is one
    """
    # if there are no conflicts, the solution is found
    if game.totalConflicts() == 0 and game.isComplete():
        if printOutput:
            print(f"Solution found in {step} steps!")
            game.printBoard()
        return game.board

    # otherwise, select the first empty cell
    var = selectEmptyCell(game)

    # if there are no empty cells and there are still conflicts, the game is impossible
    if var is None:
        if game.totalConflicts() > 0:
            if printOutput:
                print("No possible solution")
        return None

    # unpack the cell
    i, j = var

    for value in range(1,10):  # iterate across domain
        # if setting the cell to this value does not cause conflicts, try it
        if game.conflicts(var, value) == 0:
            game.board[i][j] = value

            # recursive call
            result = backtrack(game, step + 1, printOutput)

            if result is not None:  # if the assignment was successful
                return result

            # otherwise, backtrack and reset the value to empty
            game.board[i][j] = '_'

    if step == 0:  # if no solution was found:
        if printOutput:
            print("No solution found")
    return None

def selectEmptyCell(game):
    """Helper function for backtracking. Returns the first empty cell on the board.

    :param game: SudokuGame
    :return: the position of the first empty cell
    """
    emptyCells = []  # get a list of empty cells

    for i in range(9):
        for j in range(9):
            # iterating across the board
            if game.board[i][j] == '_':
                emptyCells.append((i, j))

    if len(emptyCells) == 0:  # if there are no empty cells
        return None

    # return the first empty cell
    # different implementations could experiment with returning the last empty cell or a random cell
    return emptyCells[0]

def constraintProp(game, step=0, printOutput=True):
    """Recursive implementation of a constraint propagation backtracking algorithm.

    :param game: SudokuGame
    :param step: current iteration, defaults to 0
    :param printOutput: whether to print to the console, defaults to True
    :return: the found solution, if there is one, and the time elapsed
    """
    start = time.time()  # get the start time


    # if there are no conflicts, the solution is found
    if game.isComplete() and game.totalConflicts() == 0:
        end = time.time()  # grab the end time
        if printOutput:
            print(f"Solution found in {step} steps.")
            game.printBoard()
        return game.board, end - start

    # otherwise, use the Minimum Remaining Values heuristic to select an empty cell
    var = selectMRVCell(game)

    if var is None:  # if there are no empty cells, there is no solution
        end = time.time()
        return None, end - start

    i, j = var  # unpack the chosen cell
    # create a deep copy of the cell's candidates
    originalCandidates = game.candidates[var].copy()

    for value in originalCandidates:  # iterating across candidates
        game.board[i][j] = value  # assign the value
        game.candidates[var] = [value]  # update that cell's candidates to itself

        # if this assignment does not cause any cell to have no candidates,
        # recursively call constraintProp
        if updateCandidates(game) and constraintProp(game, step+1, printOutput)[0] is not None:
            # once the solution is found
            end = time.time()
            return game.board, end - start

        # otherwise, the assignment led to failure, so backtrack and revert it
        game.board[i][j] = '_'
        game.candidates[var] = originalCandidates

    # if no solution was found
    end = time.time()
    return None, end - start

def selectMRVCell(game):
    """Helper function for constraintProp. Selects the cell with the minimum remaining values.

    :param game: SudokuGame
    :return: the cell with the least candidates
    """
    min_candidates = 10  # initial value greater than the number of possible candidates
    selected_cell = None  # initialize a placeholder for the cell

    for cell in game.editableCells:  # iterate across editableCells
        num_candidates = len(game.candidates[cell])  # get the number of candidates
        # if this cell is empty and has fewer candidates:
        if num_candidates < min_candidates and game.getValue(cell) == '_': 
            min_candidates = num_candidates  # log it
            selected_cell = cell  # log it

    return selected_cell

def updateCandidates(game):
    """Helper function for constraintProp. Updates all empty cells' candidates.
    If any cell does not have any candidates, returns False. Otherwise, returns True.

    :param game: SudokuGame
    :return: True if all cells have at least one candidate, False otherwise.
    """
    # for all empty cells:
    for cell in [x for x in game.editableCells if game.getValue(x) == '_']:
        # update the cell's candidates
        game.candidates[cell] = game.getCandidates(cell)

        # if a cell has no candidates
        if len(game.candidates[cell]) == 0:
            return False

    return True
