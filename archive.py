class SudokuGame:
    def __init__(self, board=None):
        if board is None:
            board = np.full((9, 9), '_')
        self.board = board
        self.candidates = dict()
        self.editableCells = set()

        # initialize candidates dictionary
        for i in range(9):
            for j in range(9):
                cell = (i,j)  # tupled position
                value = self.board[i][j]  # value at that slot

                if value == '_':  # if this is an empty value
                    self.candidates[cell] = list(range(1,10))
                    self.editableCells.add(cell)
                else:
                    self.candidates[cell] = [value]

    def getValue(self, cell):
        i, j = cell
        return self.board[i][j]
    
    def printBoard(self):
        for i in self.board:
            for j in i[:-1]:
                print(f" {j} ", end='')
            print(f" {i[-1]}")

    def checkBoard(self):
        # check for non-digits or _
        if not set(self.board.flatten()).issubset(set([1,2,3,4,5,6,7,8,9,'_'])):
            return False

        # check each row
        for row in self.board:
            for digit in range(1, 10):
                if list(row).count(digit) > 1:
                    return False

        # check each column
        for i in range(9):
            column = [row[i] for row in self.board]
            for digit in range(1, 10):
                if column.count(digit) > 1:
                    return False

        # check each subgrid
        subgrids = [self.board[:3, :3], self.board[:3, 3:6], self.board[:3, 6:], 
                    self.board[3:6, :3], self.board[3:6, 3:6], self.board[3:6, 6:], 
                    self.board[6:, :3], self.board[6:, 3:6], self.board[6:, 6:]]

        for subgrid in subgrids:
            flattened_subgrid = subgrid.flatten()
            for digit in range(1, 10):
                if list(flattened_subgrid).count(digit) > 1:
                    return False

        return True
    
    def getWhichSubgrid(self, cell):
        i, j = cell
        return ((i // 3)*3 , (j // 3)*3)
    
    def conflicts(self, cell, value):
        row, col = cell
        numConflicts = 0

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
        total = 0
        for i in range(9):
            for j in range(9):
                value = self.board[i][j]
                total += self.conflicts((i, j), value)
                
        return total
    
def randomSwapMinConflicts(game, max_steps):
    board = game.board
    conflictingCells = set()
    stepsWithoutSwap = 0

    # initial assignment
    for cell in game.editableCells:
            i, j = cell
            board[i][j] = random.randint(1,9)

    # at this point, the board is complete

    # iterate
    for step in range(max_steps):

        # if swaps are not working:
        if stepsWithoutSwap > 50:
            #print("Plateau, resetting")
            # re-randomize
            for cell in game.editableCells:
                i, j = cell
                board[i][j] = random.randint(1,9)
            stepsWithoutSwap = 0

        #print(f"Step {i}")

        # copy the board
        currentConflicts = game.totalConflicts()

        if currentConflicts == 0:
            print(f'Solved the game in {step} steps.')
            return game.board

        conflictingCells.clear()

        # inventory a list of conflicting cells
        for cell in game.editableCells:
                if game.conflicts(cell, game.getValue(cell)):
                    conflictingCells.add(cell)

        # randomly choose a conflicting cell
        randomCell = random.choice(list(conflictingCells))
        row, col = randomCell

        # get eligible cells to be swapped with
        swapCandidates = [cell for cell in game.editableCells if cell != randomCell and (
            cell[0] == randomCell[0] 
            or cell[1] == randomCell[1] 
            or game.getWhichSubgrid(cell) == game.getWhichSubgrid(randomCell))]

        #print("swap candidates", swapCandidates)

        # now perform the swap
        #print(f"Current conflicts: {currentConflicts}")
        swapPartner = random.choice(swapCandidates)
        i, j = randomCell
        k, l = swapPartner
        #print(f"Swapping ({i}, {j}) with ({k}, {l})")
        game.board[i][j], game.board[k][l] = game.board[k][l], game.board[i][j]

        # evaluate the swap
        print(f"New conflicts: {game.totalConflicts()}")
        if game.totalConflicts() > currentConflicts:
            print("Rejecting the swap")
            # Revert the swap
            game.board[i][j], game.board[k][l] = game.board[k][l], game.board[i][j]
            stepsWithoutSwap += 1
        else:
            stepsWithoutSwap = 0
    print("Reached maximum steps.")
    return game.board

def randomAssignMinConflicts(game, max_steps):
    board = game.board
    conflictingCells = set()
    plateauCounter = 0

    # initial assignment
    for cell in game.editableCells:
            i, j = cell
            board[i][j] = random.randint(1,9)

    # at this point, the board is complete

    # iterate
    for step in range(max_steps):
        print(f"Step {step}")

        # copy current conflicts
        currentConflicts = game.totalConflicts()

        if currentConflicts == 0:
            print(f'Solved the game in {step} steps.')
            return game.board
        
        # randomize if there is a plateau
        if plateauCounter > 20:
            for cell in game.editableCells:
                i, j = cell
                game.board[i][j] = random.randint(1,9)
            plateauCounter = 0
            print('PLATEAU')

        conflictingCells.clear()

        # inventory a list of conflicting cells
        for cell in game.editableCells:
                if game.conflicts(cell, game.getValue(cell)):
                    conflictingCells.add(cell)

        print("Current conflicts:", currentConflicts)
        print("Conflicting cells:", conflictingCells)

        # randomly choose a conflicting cell
        randomCell = random.choice(list(conflictingCells))

        print("Chosen cell:", randomCell)
        print("Current value is", game.getValue(randomCell))

        bestValue = minConflictValue(game, randomCell)

        print("The value that minimizes conflicts is", bestValue)
        row, col = randomCell

        game.board[row][col] = bestValue

        if not game.totalConflicts() < currentConflicts:
            plateauCounter += 1
        else:
            plateauCounter = 0
        print("Updated conflicts:", game.totalConflicts())

    print("Reached maximum steps.")
    return game.board

def minConflictValue(game, cell):
    row, col = cell
    conflict_counts = {}

    for value in range(1, 10):
        game.board[row][col] = value
        conflict_counts[value] = game.totalConflicts()
    
    game.board[row][col] = '_'

    minNumConflicts = float('inf')
    bestValue = 0

    for value in conflict_counts:
        if conflict_counts[value] < minNumConflicts:
            bestValue = value
            minNumConflicts = conflict_counts[value]

    return bestValue

sol1 = np.array([   [5,3,4,6,7,8,9,1,2],
                    [6,7,2,1,9,5,3,4,8],
                    [1,9,8,3,4,2,5,6,7],
                    [8,5,9,7,6,1,4,2,3],
                    [4,2,6,8,5,3,7,9,1],
                    [7,1,3,9,2,4,8,5,6],
                    [9,6,1,5,3,7,2,8,4],
                    [2,8,7,4,1,9,6,3,5],
                    [3,4,5,2,8,6,1,7,9]])

board1 = np.array([ [5,3,"_","_",7,"_","_","_","_"],
                    [6,"_","_",1,9,5,"_","_","_"],
                    ["_",9,8,"_","_","_","_",6,"_"],
                    [8,"_","_","_",6,"_","_","_",3],
                    [4,"_","_",8,"_",3,"_","_",1],
                    [7,"_","_","_",2,"_","_","_",6],
                    ["_",6,"_","_","_","_",2,8,"_"],
                    ["_","_","_",4,1,9,"_","_",5],
                    ["_","_","_","_",8,"_","_",7,9]])

sol2 = np.array([   [7,8,2,9,1,3,4,5,6],
                    [1,4,5,8,7,6,9,2,3],
                    [6,9,3,4,5,2,7,1,8],
                    [2,7,9,5,3,1,8,6,4],
                    [5,6,4,2,9,8,1,3,7],
                    [3,1,8,7,6,4,5,9,2],
                    [4,5,1,6,2,7,3,8,9],
                    [9,2,7,3,8,5,6,4,1],
                    [8,3,6,1,4,9,2,7,5]])

game = SudokuGame(board1)

game.board