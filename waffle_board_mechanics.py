# Test file for board mechanics + selenium

import time
import json
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By

def colored(color, text):
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

driver = webdriver.Chrome()
driver.get('https://wafflegame.net/')

# close the popup
time.sleep(2)
elem = driver.find_element(by=By.CLASS_NAME, value='button--close')
try:
  elem.click()
except:
  print('no popup found at this time')

tiles = driver.find_elements(by=By.CSS_SELECTOR, value='.tile.draggable')
spaces = driver.find_elements(by=By.CLASS_NAME, value='space')

if not tiles or not spaces:
  print('No tiles or spaces found')
  driver.quit()
  exit()


class Tile():
  def __init__(self, letter, pos, class_attr):
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

  def __str__(self):
    return colored(self.color, self.letter)


class Word():
  def __init__(self, letters):
    self.letters = letters

  def __str__(self):
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
  def __init__(self, tiles):
    self.board = [None] * (BOARD_SIZE * BOARD_SIZE)
    for tile in tiles:
      t = Tile(tile.text, tile.get_attribute('data-pos'), tile.get_attribute('class'))
      self.board[t.index] = t

    self.words = [None] * NUM_WORDS
    for i in range(0, NUM_WORDS, 2):
      letters = []
      for j in range(BOARD_SIZE):
        letters.append(self.board[i * BOARD_SIZE + j])
      self.words[i // 2] = Word(letters)
    for i in range(0, NUM_WORDS, 2):
      letters = []
      for j in range(BOARD_SIZE):
        letters.append(self.board[j * BOARD_SIZE + i])
      self.words[i // 2 + NUM_WORDS // 2] = Word(letters)
  
assert(len(tiles) == NUM_TILES)
assert(len(spaces) == NUM_TILES)

board = Board(tiles)

for word in board.words:
  print(word)

for space in spaces:
  print(space.get_attribute('data-pos'))


tile = driver.find_element(By.CSS_SELECTOR, "div.tile.draggable[data-pos='{\"x\":1,\"y\":0}']")
space = driver.find_element(By.CSS_SELECTOR, "div.space[data-pos='{\"x\":4,\"y\":3}']")

print(tile, space)

time.sleep(1)
action_chains = ActionChains(driver)
action_chains.drag_and_drop(tile, space).perform()

time.sleep(10)
driver.quit()
