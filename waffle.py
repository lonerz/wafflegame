# Main driver that puts together selenium to control the browser
# and the waffle solving strategy to automate waffle solving

import time
import json
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from copy import deepcopy
from typing import Dict, List, Optional, Set, Tuple


BOARD_SIZE = 5
NUM_TILES = BOARD_SIZE * BOARD_SIZE - (BOARD_SIZE // 2) * (BOARD_SIZE // 2)
NUM_WORDS = (BOARD_SIZE // 2 + 1) * 2


# Print text in color, helps with debugging
def colored(color : str, text : str) -> str:
  if color == 'green':
    r, g, b = 0, 255, 0
  elif color == 'yellow':
    r, g, b = 255, 255, 0
  else:
    r, g, b = 255, 255, 255
  return "\033[38;2;{};{};{}m{}\033[38;2;255;255;255m".format(r, g, b, text)


word_set : Set[str] = set()

# import words from wordle file
with open('words.txt') as f:
  for word in f.readlines():
    word_set.add(word.strip().upper())

driver = webdriver.Chrome()
driver.get('https://wafflegame.net/')

# close the popup
time.sleep(2)
elem = driver.find_element(by=By.CLASS_NAME, value='button--close')
try:
  elem.click()
except:
  print('no popup found at this time')

# Make sure we were able to pull the tiles from the page
tiles = driver.find_elements(by=By.CSS_SELECTOR, value='.tile.draggable')
if not tiles:
  print('No tiles or spaces found')
  driver.quit()
  exit()

assert(len(tiles) == NUM_TILES)


class Tile():
  def __init__(self, letter : str, pos : str, class_attr : str) -> None:
    self.letter = letter
    coords = json.loads(pos)
    self.x = coords['x']
    self.y = coords['y']
    self.index = coords['x'] + coords['y'] * BOARD_SIZE
    class_attrs = class_attr.split(' ')
    if 'tile--' in class_attrs[-1]:
      self.color = 'black'
    else:
      self.color = class_attrs[-1]
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


'''
Example board is like the following:

  A B C D E
  F _ G _ H
  I J K L M
  N _ O _ P
  Q R S T U

words are enumerated rows first and then columns
word 1: ABCDE
word 2: IJKLM
word 3: QRSTU
word 4: AFINQ
word 5: CGKOS
word 6: EHMPU
'''

class Board():
  def __init__(self, tiles : List[WebElement]) -> None:
    self.board : List[Optional[Tile]] = [None] * (BOARD_SIZE * BOARD_SIZE)
    all_possible_letters : Set[str] = set()
    self.letter_to_tile : Dict[str, List[Tile]] = {}
    for tile in tiles:
      t = Tile(tile.text, tile.get_attribute('data-pos'), tile.get_attribute('class'))
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

  for real_word in word_set:
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
  driver.quit()
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
  print('No permutation found to create a valid waffle')
  driver.quit()
  exit()

print()
print('Valid waffles', answer)

# Deal with swaps now...
current_waffle = [t.letter if t else None for t in board.board]
correct_waffle : List[Optional[str]] = [None] * (BOARD_SIZE * BOARD_SIZE)
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

queue : List[Tuple[Optional[int], List[Optional[str]], List[Tuple[int, int]], Dict[str, Set[int]]]] = [(None, current_waffle, [], letter_to_correct_index)]
answer_swaps : Optional[List[Tuple[int, int]]] = None

while len(queue) > 0:
  last_swapped_index, current_board, current_swaps, letter_to_index = queue.pop(0)

  # we don't care about solutions that are already unoptimized
  if len(current_swaps) > 10:
    continue

  # if we swapped something last time, we should keep swapping it
  if last_swapped_index is not None:
    t = current_board[last_swapped_index]
    for index in letter_to_index[t]:
      if last_swapped_index > index:
        continue
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
      if i > index:
        continue
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
    print('We found a solution!', current_swaps)
    answer_swaps = current_swaps
    break

if not answer_swaps:
  print('No valid swap answer found')
  driver.quit()
  exit()

for s1, s2 in answer_swaps:
  time.sleep(0.5)
  s1x, s1y = s1 % BOARD_SIZE, s1 // BOARD_SIZE
  s2x, s2y = s2 % BOARD_SIZE, s2 // BOARD_SIZE
  tile = driver.find_element(By.CSS_SELECTOR, "div.tile.draggable[data-pos='{\"x\":" + str(s1x) + ",\"y\":" + str(s1y) + "}']")
  space = driver.find_element(By.CSS_SELECTOR, "div.space[data-pos='{\"x\":" + str(s2x) + ",\"y\":" + str(s2y) + "}']")
  action_chains = ActionChains(driver)
  action_chains.drag_and_drop(tile, space).perform()

time.sleep(5)
driver.quit()

