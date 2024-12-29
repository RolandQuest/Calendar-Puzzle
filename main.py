
from enum import Enum, auto

class Weekday(Enum):
    Sunday = auto()
    Monday = auto()
    Tuesday = auto()
    Wednesday = auto()
    Thursday = auto()
    Friday = auto()
    Saturday = auto()

MONTH_MAP = {
    1: (0, 0),
    2: (1, 0),
    3: (2, 0),
    4: (3, 0),
    5: (0, 1),
    6: (0, 2),
    7: (0, 3),
    8: (0, 4),
    9: (0, 5),
    10: (1, 5),
    11: (2, 5),
    12: (3, 5)
}

DAY_MAP = {
    1: (4, 0),
    10: (1, 2),
    11: (2, 2),
    12: (3, 2),
    13: (4, 2),
    14: (7, 5),
    15: (6, 2),
    16: (1, 3),
    17: (2, 3),
    18: (3, 3),
    19: (4, 3),
    2: (5, 0),
    20: (5, 3),
    21: (6, 3),
    22: (1, 4),
    23: (2, 4),
    24: (3, 4),
    25: (4, 4),
    26: (5, 4),
    27: (6, 4),
    28: (4, 5),
    29: (5, 5),
    3: (6, 0),
    30: (6, 5),
    31: (5, 2),
    4: (1, 1),
    5: (2, 1),
    6: (3, 1),
    7: (4, 1),
    8: (5, 1),
    9: (6, 1)
}

DAY_OF_WEEK_MAP = {
    Weekday.Sunday: (8, 4),
    Weekday.Monday: (7, 0),
    Weekday.Tuesday: (8, 0),
    Weekday.Wednesday: (7, 1),
    Weekday.Thursday: (7, 2),
    Weekday.Friday: (7, 3),
    Weekday.Saturday: (8, 3)
}


class Piece:
    
    def __init__(self, pts):
        self.pts = pts
        self.rotations = 0
        self.is_flipped = False
        self._iter_base_case_seen = False
        
    def rotate(self):
        self.pts = [ (y, -x) for x, y in self.pts ]
        self.rotations = (self.rotations + 1) % 4
        
    def flip(self):
        self.pts = [ (-x, y) for x, y in self.pts ]
        self.is_flipped = not self.is_flipped
         
    def clone(self):
        return Piece([ (x, y) for x, y in self.pts ])
    
    def _rebase(self, pt_index: int):
        if pt_index >= len(self.pts):
            return
        x_shift = self.pts[pt_index][0]
        y_shift = self.pts[pt_index][1]
        self.pts = [ (x - x_shift, y - y_shift) for x, y in self.pts ]
    
    def _find_ref_index(self):
        return 
    
    def __iter__(self):
        self._iter_base_case_seen = False
        self._rebase(0)
        if self.is_flipped:
            self.flip()
        while self.rotations != 0:
            self.rotate()
        return self
    
    def __next__(self):
        if not self._iter_base_case_seen:
            self._iter_base_case_seen = True
            return self
        self.rotate()
        if self.rotations == 0:
            self.flip()
            if not self.is_flipped:
                zero_index = (self.pts.index((0, 0)) + 1) % len(self.pts)
                self._rebase(zero_index)
                if zero_index == 0:
                    raise StopIteration
        return self
    
    def __str__(self):
        return f'ref_index: {self.pts.index((0, 0))}, flipped: {self.is_flipped}, rotations: {self.rotations}, pts: {self.pts}'


class Board:
    
    def __init__(self, month: int, day: int, day_of_week: Weekday, pieces: dict = None):
        self.ROWS = 6
        self.COLUMNS = 9
        self.month = month
        self.day = day
        self.day_of_week = day_of_week
        # [column][row]
        self.grid = [ [ 0 for _ in range(self.ROWS) ] for _ in range(self.COLUMNS) ]
        # (x, y): Piece
        self.pieces_played = {}
        if pieces:
            for loc, p in pieces.items():
                if not self.test_piece(loc, p):
                    print('uh oh in cloning board.')
                    input()
                self.play_piece(loc, p)
        pt = MONTH_MAP[month]
        self.grid[pt[0]][pt[1]] = 1
        pt = DAY_MAP[day]
        self.grid[pt[0]][pt[1]] = 1
        pt = DAY_OF_WEEK_MAP[day_of_week]
        self.grid[pt[0]][pt[1]] = 1
        
    def clone(self):
        return Board(self.month, self.day, self.day_of_week, self.pieces_played)
        
    def test_piece(self, loc, piece: Piece):
        for pt in piece.pts:
            
            if loc[0] + pt[0] < 0 or loc[0] + pt[0] >= self.COLUMNS:
                return False
            if loc[1] + pt[1] < 0 or loc[1] + pt[1] >= self.ROWS:
                return False
            if self.grid[loc[0] + pt[0]][loc[1] + pt[1]] == 1:
                return False
        return True
    
    def play_piece(self, loc, piece: Piece):
        for pt in piece.pts:
            self.grid[loc[0] + pt[0]][loc[1] + pt[1]] = 1
        self.pieces_played[loc] = piece.clone()
    
    def print_basic(self):
        to_print = ''
        for y in range(self.ROWS):
            for x in range(self.COLUMNS):
                to_print += f'{self.grid[x][y]} '
            to_print += '\n'
        print(to_print)
    
    def is_full(self):
        for row in self.grid:
            for cell in row:
                if cell == 0:
                    return False
        return True
    
    def find_empty(self):
        for ci, row in enumerate(self.grid):
            for ri, cell in enumerate(row):
                if cell == 0:
                    return (ci, ri)
        return (-1, -1)


def find_solution(board: Board, pieces: list[Piece]):
    
    if board.is_full():
        print('Solution found!')
        board.print_basic()
        input()
    
    pt_gap = board.find_empty()
    
    for pi, piece in enumerate(pieces):
        for layout in piece:
            if board.test_piece(pt_gap, layout):
                new_board = board.clone()
                new_board.play_piece(pt_gap, layout)
                new_pieces = [ p.clone() for i, p in enumerate(pieces) if i != pi  ]
                find_solution(new_board, new_pieces)


MONTH = 12
DAY = 25
DAY_OF_WEEK = Weekday.Wednesday

PIECES = [
    Piece( [ (0, 0), (1, 0), (1, 1), (1, 2), (2, 1) ] ),
    Piece( [ (0, 0), (1, 0), (1, 1), (1, 2), (0, 2) ] ),
    Piece( [ (0, 0), (0, 1), (0, 2), (0, 3), (0, 4) ] ),
    Piece( [ (0, 0), (0, 1), (1, 1), (2, 1), (3, 1) ] ),
    Piece( [ (0, 0), (0, 1), (0, 2), (0, 3), (1, 2) ] ),
    Piece( [ (0, 0), (0, 1), (0, 2), (1, 1), (2, 1) ] ),
    Piece( [ (0, 0), (0, 1), (0, 2), (1, 2), (2, 2) ] ),
    Piece( [ (0, 0), (0, 1), (0, 2), (1, 2), (1, 3) ] ),
    Piece( [ (0, 0), (0, 1), (1, 0), (1, 1), (2, 1) ] ),
    Piece( [ (0, 0), (0, 1), (1, 1), (2, 1), (2, 2) ] )
]


index = 0
for state in PIECES[0]:
    print(state)
    index += 1
print(index)
print(PIECES[0])

board = Board(MONTH, DAY, DAY_OF_WEEK)
board.print_basic()

find_solution(board, PIECES)

