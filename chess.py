import pprint as pp
from chessMove import ChessMove
import copy
import random

black = 'black'
white = 'white'

pawn = 'pawn'
rook = 'rook'
knight = 'knight'
bishop = 'bishop'
queen = 'queen'
king = 'king'

worth = {
    pawn: 1,
    rook: 5,
    knight: 3,
    bishop: 3,
    queen: 9,
    king: 30,
}

symbols = {
    f'{black}_{pawn}': '♟',
    f'{black}_{rook}': '♜',
    f'{black}_{knight}': '♞',
    f'{black}_{bishop}': '♝',
    f'{black}_{queen}': '♛',
    f'{black}_{king}': '♚',
    f'{white}_{pawn}': '♙',
    f'{white}_{rook}': '♖',
    f'{white}_{knight}': '♘',
    f'{white}_{bishop}': '♗',
    f'{white}_{queen}': '♕',
    f'{white}_{king}': '♔',
}

letters = ['0', '1', '2', '3', '4', '5', '6', '7']

START_ARRANGEMENT = {
    f'{black}_{pawn}': {(1, int) for int in range(8)},
    f'{black}_{rook}': {(0, 0), (0, 7)},
    f'{black}_{knight}': {(0, 1), (0, 6)},
    f'{black}_{bishop}': {(0, 2), (0, 5)},
    f'{black}_{queen}': {(0, 3)},
    f'{black}_{king}': {(0, 4)},
    f'{white}_{pawn}': {(6, int) for int in range(8)},
    f'{white}_{rook}': {(7, 0), (7, 7)},
    f'{white}_{knight}': {(7, 1), (7, 6)},
    f'{white}_{bishop}': {(7, 2), (7, 5)},
    f'{white}_{queen}': {(7, 3)},
    f'{white}_{king}': {(7, 4)},
}

class ChessBoard():

    def __init__(self, height: int=8, width: int=8, dict=None):
        if height > 8 or height < 1 or width > 8 or width < 1:
            print('Height and width must be an integer between 1-8, inclusive.')
        
        if not dict:
            dict = START_ARRANGEMENT

        self.height = height
        self.width = width

        # Used to quickly locate information about a piece.
        self.board = {}
        # Used to save all possible moves at any given moment.
        self.black_moves = {}
        self.white_moves = {}

        # Used to store the priority of all moves.
        self.priority = {}

        # Temporary data structure to help set the above data structures.
        black_pieces = set()
        white_pieces = set()

        # Sets the pieces into the board positions.
        for piece, positions in dict.items():
            for index, position in enumerate(positions):
                self.board[position] = {}
                color, name = piece.split('_')
                self.board[position]['name'] = name + str(index)
                self.board[position]['color'] = color
                if color == black:
                    black_pieces.add(position)
                elif color == white:
                    white_pieces.add(position)

        # Set empty spaces in the board.
        for row in range(self.height):
            for col in range(self.width):
                if (row, col) not in self.board:
                    self.board[(row, col)] = None
        
        # Calculate all moves for black pieces on the board.
        chess_move = ChessMove(black, self.board)
        for point in black_pieces:
            piece = self.board[point]
            name = piece['name']
            moves = chess_move.moves(name[:-1], point)
            self.priority.update({move: 0 for move in moves})
            self.black_moves[name] = moves
        
        # Calculate all moves for white pieces on the board.
        chess_move = ChessMove(white, self.board)
        for point in white_pieces:
            piece = self.board[point]
            name = piece['name']
            moves = chess_move.moves(name[:-1], point)
            self.priority.update({move: 0 for move in moves})
            self.white_moves[name] = moves

    # ////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ////////////////////////////////////////////////////////////


    # Adjusts all the stored class variables after a move. Returns nothing.
    def _adjust_positions(self, choice):
        self.black_moves, self.white_moves, self.board = self.adjust_positions(choice, self.black_moves, self.white_moves, self.board)

        for move in self.get_moves(self.black_moves):
            if move not in self.priority:
                self.set_priority(move, 0)
        
        for move in self.get_moves(self.white_moves):
            if move not in self.priority:
                self.set_priority(move, 0)

    
    # ////////////////////////////////////////////////////////////
    # GETTERS
    # ////////////////////////////////////////////////////////////

    # Returns all the moves from a given moves dictionary.
    def get_moves(self, moves_dict):
        all_moves = []
        for moves in moves_dict.values():
            all_moves.extend(list(moves))
        return all_moves

    # Returns the priorty of the given move.
    def get_priority(self, move):
        return self.priority[move]
    
    # Sets the value of the given move.
    def set_priority(self, move, value):
        self.priority[move] = value

    # Returns a list of moves ordered by priority.
    def get_prioritized_moves(self, color):
        all_moves = []
        if color == black:
            for moves in self.black_moves.values():
                all_moves.extend(list(moves))
        elif color == white:
            for moves in self.white_moves.values():
                all_moves.extend(list(moves))
        
        all_moves.sort(key=lambda move: self.get_priority(move), reverse=True)
        return all_moves


    # ////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ////////////////////////////////////////////////////////////

    # Returns a new set of moves and updated board as a result of a move. Does not change the stored class variables. For use in minimax.
    def adjust_positions(self, move, black_moves, white_moves, board):
        # Prepare all the variables.
        previous_position = move[0]
        new_position = move[1]
        black_moves = copy.deepcopy(black_moves)
        white_moves = copy.deepcopy(white_moves)
        board = copy.deepcopy(board)
        same_moves = {
            black: black_moves,
            white: white_moves,
        }

        # In moves, remove all moves belonging to the piece that moved.
        color = board[previous_position]['color']
        name = board[previous_position]['name']
        same_moves[color][name].clear()

        # In moves, if a piece was at the new square, remove that piece from moves.
        if board[new_position]:
            color = board[new_position]['color']
            name = board[new_position]['name']
            same_moves[color].pop(name)

        # In board, change the board so that the piece moves to a new location.
        info = board[previous_position]
        board[new_position] = info
        board[previous_position] = None

        # Add new moves for the moved piece.
        color = board[new_position]['color']
        name = board[new_position]['name']
        chess_move = ChessMove(color, board)
        moves = chess_move.moves(name[:-1], new_position)
        same_moves[color][name].update(moves)

        # Clear all moves of pieces affected by the move, and then add the updated moves.
        squares = chess_move.occupied_squares(new_position)
        for square in squares:
            name = square[0]
            position = square[1]
            color = board[position]['color']
            same_moves[color][name].clear()
            chess_move.color = color
            moves = chess_move.moves(name[:-1], position)
            same_moves[color][name].update(moves)
        
        return black_moves, white_moves, board


    # TODO check if the board is in checkmate or check
    def check(self, player, black_pieces, white_pieces):
        raise NotImplementedError


    # Returns the value of a given board. Currently needs to smartly consider checks and checkmates. For use in minimax.
    # Need to be a lot more effective by not skipping moves that leads to sure wins.
    def evaluate(self, board):
        value = 0
        for info in board.values():
            if info:
                color = info['color']
                if color == black:
                    value += worth[info['name'][:-1]]
                elif color == white:
                    value -= worth[info['name'][:-1]]
        return value
    

    # Returns the player that won if there is one, otherwise None. For use in minimax. 
    def has_won(self, black_moves, white_moves):
        if 'king0' not in white_moves:
            return black
        elif 'king0' not in black_moves:
            return white
        else:
            return None


    # Prints the current board.
    def print_board(self):
        board = [[None for i in range(self.width)] for j in range(self.height)]
        for square, info in self.board.items():
            row = square[0]
            col = square[1]
            if info:
                board[row][col] = f"{info['color']}_{info['name']}"

        print(' ', end='')
        for i in range(self.width):
            print(f' {letters[i]} ', end='')
        print()
        for index, row in enumerate(board):
            print('----' * self.width)
            print(index, end='')
            for cell in row:
                if cell:
                    print(f'|{symbols[cell[:-1]]} ', end='')
                else:
                    print('|  ', end='')
            print(f'|{index}')
        print('----' * self.width)
        print(' ', end='')
        for i in range(self.width):
            print(f' {letters[i]} ', end='')
        print()
        
        
        
'''
chess_board = ChessBoard()
chess_board.print_board()
pp.pprint(chess_board.black_moves)
pp.pprint(chess_board.white_moves)
all_white_moves = []
for value in chess_board.white_moves.values():
    for dict in value:
        moves = dict[move_set]
        all_white_moves.append(moves)
move = random.choice(all_white_moves)
black_moves, white_moves, board = chess_board.adjust_positions(move, chess_board.black_moves, chess_board.white_moves, chess_board.board)
chess_board.board = board
chess_board.print_board()
pp.pprint(black_moves)
pp.pprint(white_moves)'''