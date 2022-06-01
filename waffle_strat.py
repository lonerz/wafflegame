from copy import deepcopy
from typing import Dict, List, Optional, Set, Tuple

word_list : List[str] = []

# import words from wordle file
with open('words.txt') as f:
  for word in f.readlines():
    word_list.append(word.strip().upper())

# sample waffle puzzles
tiles = [
  ("C", 0, 0, 0, "green"),
  ("L", 1, 0, 1, "black"),
  ("E", 2, 0, 2, "yellow"),
  ("M", 3, 0, 3, "black"),
  ("H", 4, 0, 4, "green"),
  ("A", 0, 1, 5, "yellow"),
  ("V", 2, 1, 7, "yellow"),
  ("S", 4, 1, 9, "yellow"),
  ("S", 0, 2, 10, "yellow"),
  ("S", 1, 2, 11, "black"),
  ("I", 2, 2, 12, "green"),
  ("S", 3, 2, 13, "green"),
  ("E", 4, 2, 14, "black"),
  ("U", 0, 3, 15, "black"),
  ("R", 2, 3, 17, "black"),
  ("A", 4, 3, 19, "black"),
  ("S", 0, 4, 20, "green"),
  ("D", 1, 4, 21, "yellow"),
  ("K", 2, 4, 22, "black"),
  ("R", 3, 4, 23, "black"),
  ("Y", 4, 4, 24, "green"),
]

tiles = [
  ("M", 0, 0, 0, "green"),
  ("R", 1, 0, 1, "black"),
  ("T", 2, 0, 2, "yellow"),
  ("E", 3, 0, 3, "yellow"),
  ("Y", 4, 0, 4, "green"),
  ("B", 0, 1, 5, "black"),
  ("D", 2, 1, 7, "black"),
  ("E", 4, 1, 9, "black"),
  ("E", 0, 2, 10, "yellow"),
  ("N", 1, 2, 11, "black"),
  ("O", 2, 2, 12, "green"),
  ("I", 3, 2, 13, "black"),
  ("E", 4, 2, 14, "green"),
  ("L", 0, 3, 15, "black"),
  ("D", 2, 3, 17, "green"),
  ("R", 4, 3, 19, "black"),
  ("T", 0, 4, 20, "green"),
  ("N", 1, 4, 21, "yellow"),
  ("A", 2, 4, 22, "yellow"),
  ("A", 3, 4, 23, "black"),
  ("D", 4, 4, 24, "green"),
]

tiles = [
  ("S", 0, 0, 0, "green"),
  ("P", 1, 0, 1, "black"),
  ("U", 2, 0, 2, "yellow"),
  ("D", 3, 0, 3, "black"),
  ("Y", 4, 0, 4, "green"),
  ("I", 0, 1, 5, "yellow"),
  ("U", 2, 1, 7, "black"),
  ("M", 4, 1, 9, "yellow"),
  ("T", 0, 2, 10, "black"),
  ("O", 1, 2, 11, "yellow"),
  ("I", 2, 2, 12, "green"),
  ("L", 3, 2, 13, "black"),
  ("M", 4, 2, 14, "green"),
  ("U", 0, 3, 15, "black"),
  ("W", 2, 3, 17, "black"),
  ("O", 4, 3, 19, "black"),
  ("L", 0, 4, 20, "green"),
  ("P", 1, 4, 21, "yellow"),
  ("M", 2, 4, 22, "green"),
  ("O", 3, 4, 23, "black"),
  ("Y", 4, 4, 24, "green"),
]


# Print text in color, helps with debugging
def colored(color : str, text : str) -> str:
  if color == 'green':
    r, g, b = 0, 255, 0
  elif color == 'yellow':
    r, g, b = 255, 255, 0
  else:
    r, g, b = 255, 255, 255
  return "\033[38;2;{};{};{}m{}\033[38;2;255;255;255m".format(r, g, b, text)


BOARD_SIZE = 5
NUM_TILES = BOARD_SIZE * BOARD_SIZE - (BOARD_SIZE // 2) * (BOARD_SIZE // 2)
NUM_WORDS = (BOARD_SIZE // 2 + 1) * 2


class Tile():
  def __init__(self, letter : str, x : int, y : int, index : int, color : str) -> None:
    self.letter = letter
    self.x = x
    self.y = y
    self.index = index
    self.color = color
    self.words : List[Word] = []
    self.space : Optional[Space] = None

  def __str__(self) -> str:
    return colored(self.color, self.letter)


class Space():
  def __init__(self, index : int, possible_letters : Set[str]) -> None:
    self.index = index
    self.possible_letters = possible_letters
    self.impossible_letters = set()
    self.tile : Optional[Tile] = None

  def add_impossible(self, letter : str) -> None:
    if letter in self.possible_letters:
      self.possible_letters.remove(letter)
    self.impossible_letters.add(letter)

  def add_impossibles(self, letters : Set[str]) -> None:
    self.possible_letters.difference_update(letters)
    self.impossible_letters = self.impossible_letters.union(letters)

  def __str__(self) -> str:
    return 'Possible letters for space {}: '.format(self.index) + ' '.join(sorted(list(self.possible_letters)))


class Word():
  def __init__(self, letters : List[Tile]) -> None:
    self.letters = letters
    self.known_letters : List[str] = []
    self.possible_answers : List[str] = []

  def __str__(self) -> str:
    word = ''
    for letter in self.letters:
      word += str(letter)
    return word


class Board():
  def __init__(self, tiles : List[Tuple[str, int, int, int, str]]) -> None:
    self.board : List[Optional[Tile]] = [None] * (BOARD_SIZE * BOARD_SIZE)
    all_possible_letters : Set[str] = set()
    self.letter_to_tile : Dict[str, List[Tile]] = {}
    for text, x, y, index, color in tiles:
      t = Tile(text, x, y, index, color)
      self.board[t.index] = t
      all_possible_letters.add(t.letter)
      if t.letter not in self.letter_to_tile:
        self.letter_to_tile[t.letter] = []
      self.letter_to_tile[t.letter].append(t)
    
    print('All possible letters: ', ' '.join(sorted(list(all_possible_letters))))
    print()

    self.spaces : List[Optional[Space]] = [None] * (BOARD_SIZE * BOARD_SIZE)
    for i in range(BOARD_SIZE):
      for j in range(BOARD_SIZE):
        if i % 2 and j % 2:
          continue
        idx = i * BOARD_SIZE + j
        self.spaces[idx] = Space(idx, all_possible_letters.copy())
        self.board[idx].space = self.spaces[idx]
        self.spaces[idx].tile = self.board[idx]

    self.words : List[Optional[Word]] = [None] * NUM_WORDS
    for i in range(0, NUM_WORDS, 2):
      letters : List[Tile] = []
      for j in range(BOARD_SIZE):
        letters.append(self.board[i * BOARD_SIZE + j])
      word = Word(letters)
      self.words[i // 2] = word
      for letter in letters:
        letter.words.append(word)
    for i in range(0, NUM_WORDS, 2):
      letters = []
      for j in range(BOARD_SIZE):
        letters.append(self.board[j * BOARD_SIZE + i])
      word = Word(letters)
      self.words[i // 2 + NUM_WORDS // 2] = word
      for letter in letters:
        letter.words.append(word)
    
  def print_board(self):
    for i in range(BOARD_SIZE):
      for j in range(BOARD_SIZE):
        if self.board[i * BOARD_SIZE + j]:
          print(self.board[i * BOARD_SIZE + j], end='')
        else:
          print(' ', end='')
      print()

  
board = Board(tiles)
board.print_board()

def solve(tile : Tile) -> None:
  space = tile.space

  if tile.color == 'green':
    # set all other letters to impossible
    space.add_impossibles(space.possible_letters.difference(set([tile.letter])))

    # add that letter to the for-sure letters of its words
    for word in tile.words:
      word.known_letters.append(tile.letter)

    # if all instances of this letter are solved, remove this letter from the possible letters of all other spaces
    if all([t.color == 'green' for t in board.letter_to_tile[tile.letter]]):
      for t in board.board:
        if t and t.letter != tile.letter:
          t.space.add_impossible(tile.letter)

  elif tile.color == 'yellow':
    # this space cannot be this letter
    space.add_impossible(tile.letter)

    # if this space is not an intersection letter (spans a single word), we know this letter must be in this word
    if tile.x % 2 or tile.y % 2:
      assert(len(tile.words) == 1)
      tile.words[0].known_letters.append(tile.letter)

  else:
    # this space cannot be this letter
    space.add_impossible(tile.letter)

  # we only deal with letters that are the only instance of its letter in its word
  # when there are multiple tiles of the same letter, things get more complicated with the coloring ordering
  for word in tile.words:
    for letter in word.letters:
      if letter == tile:
        continue
      if letter.letter == tile.letter and tile.color != 'green':
        return

  # Remove black letter from all of its words
  if tile.color == 'black':
    for word in tile.words:
      for letter in word.letters:
        letter.space.add_impossible(tile.letter)

  # Remove yellow letters from all letters NOT in its words if it's the only one
  # on the whole board...
  elif tile.color == 'yellow':
    tiles = board.letter_to_tile[tile.letter]
    if len(tiles) == 1:
      current_letters = set()
      for word in tile.words:
        for letter in word.letters:
          current_letters.add(letter)
      for t in board.board:
        if t and t not in current_letters and t.color != 'green':
          t.space.add_impossible(tile.letter)

# wrapper function that iterates over each tile and calls a function on that tile
def apply_func_to_tile(func):
  for tile in board.board:
    if tile:
      func(tile)

def print_possible_answers():
  print()
  apply_func_to_tile(lambda t: print(t.space))

apply_func_to_tile(solve)
print_possible_answers()
print()

# cross reference wordle words with constraints on board
for word in board.words:
  print(word)

  for real_word in word_list:
    possible = True

    # make sure for-sure letters are in the word
    for letter in word.known_letters:
      if letter not in real_word:
        possible = False
        break
    
    if not possible:
      continue

    # make sure all letters in the word satisfy the positional constraints
    union_possible_letters = set()
    for i, tile in enumerate(word.letters):
      if real_word[i] not in tile.space.possible_letters:
        possible = False
        break

    if possible:
      print('Possible word: ', real_word)
      word.possible_answers.append(real_word)

print()

try:
  for word in board.words:
    assert(len(word.possible_answers))
except AssertionError:
  print('No possible answers, check word list')
  exit()

def is_valid_permutation(words : List[str]) -> bool:
  # make sure the word intersections match up
  for i in range(NUM_WORDS // 2):
    for j in range(NUM_WORDS // 2, NUM_WORDS):
      col_idx = 2 * (j - NUM_WORDS // 2)
      if words[i][col_idx] != words[j][2 * i]:
        return False
  # make sure the letter counts are the same
  letter_count : Dict[str, int] = {}
  for word in words:
    for letter in word:
      if letter not in letter_count:
        letter_count[letter] = 0
      letter_count[letter] += 1
  # make sure to account for overcount of the intersection letters
  for i in range(NUM_WORDS // 2):
    for j in range(0, NUM_WORDS, 2):
      letter_count[words[i][j]] -= 1
  for letter, count in letter_count.items():
    if count != len(board.letter_to_tile[letter]):
      return False
  for letter, tiles in board.letter_to_tile.items():
    if len(tiles) != letter_count[letter]:
      return False
  return True

answer : List[List[str]] = []
cur_idxs = [0] * NUM_WORDS

print('Try all possible waffles with possible words')
while True:
  cur_words : List[str] = []
  for i, word in enumerate(board.words):
    cur_words.append(word.possible_answers[cur_idxs[i]])

  # check if the current permutation of possible answers is valid
  # print(cur_words)
  if is_valid_permutation(cur_words):
    print('Valid permutation: ', cur_words)
    answer.append(cur_words)

  # iterate to next permutation of possible answers
  cur_idxs[-1] += 1
  for i in range(NUM_WORDS - 1, 0, -1):
    if cur_idxs[i] == len(board.words[i].possible_answers):
      cur_idxs[i] = 0
      cur_idxs[i - 1] += 1
  if cur_idxs[0] == len(board.words[0].possible_answers):
    break

if not answer:
  print('No valid answer found')
  exit()

print()
print('Valid waffles', answer)

# Deal with swaps now...
current_waffle = [t.letter if t else None for t in board.board]
correct_waffle = [None] * (BOARD_SIZE * BOARD_SIZE)
print('Using valid solution: ', answer[0])

for i in range(NUM_WORDS // 2):
  for j in range(BOARD_SIZE):
    correct_waffle[2 * i * BOARD_SIZE + j] = answer[0][i][j]

for i in range(NUM_WORDS // 2, NUM_WORDS):
  for j in range(BOARD_SIZE):
    if j % 2 == 0:
      assert(correct_waffle[j * BOARD_SIZE + 2 * (i - NUM_WORDS // 2)] == answer[0][i][j])
    correct_waffle[j * BOARD_SIZE + 2 * (i - NUM_WORDS // 2)] = answer[0][i][j]

print('Starting waffle', current_waffle)
print()

letter_to_correct_index : Dict[str, Set[int]] = {}
for i, letter in enumerate(correct_waffle):
  if not letter:
    continue
  # if the letter is already correct, we don't care about it
  if letter == current_waffle[i]:
    continue
  if letter not in letter_to_correct_index:
    letter_to_correct_index[letter] = set()
  letter_to_correct_index[letter].add(i)

queue = [(None, current_waffle, [], letter_to_correct_index)]

while len(queue) > 0:
  last_swapped_index, current_board, current_swaps, letter_to_index = queue.pop(0)

  # we don't care about solutions that are already unoptimized
  if len(current_swaps) > 10:
    continue

  # if we swapped something last time, we should keep swapping it
  if last_swapped_index is not None:
    t = current_board[last_swapped_index]
    for index in letter_to_index[t]:
      new_board = current_board[:]
      new_board[last_swapped_index], new_board[index] = new_board[index], new_board[last_swapped_index]
      new_swaps = current_swaps[:] + [(last_swapped_index, index)]
      new_letter_to_index = deepcopy(letter_to_index)
      new_letter_to_index[t].remove(index)
      swapped_index = None
      if correct_waffle[last_swapped_index] != new_board[last_swapped_index]:
        swapped_index = last_swapped_index
      queue.append((swapped_index, new_board, new_swaps, new_letter_to_index))
    continue

  swapped = False
  for i in range(BOARD_SIZE * BOARD_SIZE):
    t = current_board[i]
    # skip over Nones
    if not t:
      continue
    # if the tile is already correct, skip over it
    if t == correct_waffle[i]:
      continue

    # find a correct tile to swap into
    for index in letter_to_index[t]:
      assert(index != i)
      new_board = current_board[:]
      new_board[i], new_board[index] = new_board[index], new_board[i]
      new_swaps = current_swaps[:] + [(i, index)]
      new_letter_to_index = deepcopy(letter_to_index)
      new_letter_to_index[t].remove(index)
      swapped_index = None
      if correct_waffle[i] != new_board[i]:
        swapped_index = i
      swapped = True
      queue.append((swapped_index, new_board, new_swaps, new_letter_to_index))

  if not swapped:
    print('We found a solution!', current_board, current_swaps)
    break
