from typing import Dict, List, Set, Tuple

BOARD_SIZE = 5
NUM_WORDS = 6

first : Dict[str, Set[str]] = {}
middle : Dict[str, Set[str]] = {}
first_middle : Dict[Tuple[str, str], Set[str]] = {}
first_middle_end : Dict[Tuple[str, str, str], Set[str]] = {}

# iterate over all capital letters
for i in range(ord('A'), ord('Z') + 1):
  first[chr(i)] = set()
  middle[chr(i)] = set()

for i in range(ord('A'), ord('Z') + 1):
  for j in range(ord('A'), ord('Z') + 1):
    first_middle[(chr(i), chr(j))] = set()

for i in range(ord('A'), ord('Z') + 1):
  for j in range(ord('A'), ord('Z') + 1):
    for k in range(ord('A'), ord('Z') + 1):
      first_middle_end[(chr(i), chr(j), chr(k))] = set()

with open('words.txt') as f:
  for word in f.readlines():
    word = word.strip().upper()
    first[word[0]].add(word)
    middle[word[2]].add(word)
    first_middle[(word[0], word[2])].add(word)
    first_middle_end[(word[0], word[2], word[-1])].add(word)

def print_words_as_waffle(words : List[str]) -> None:
  waffle : List[List[str]] = []
  for _ in range(BOARD_SIZE):
    waffle.append([' '] * BOARD_SIZE)

  for i in range(NUM_WORDS // 2):
    for j in range(BOARD_SIZE):
      waffle[2 * i][j] = words[i][j]

  for i in range(NUM_WORDS // 2, NUM_WORDS):
    for j in range(BOARD_SIZE):
      if j % 2 == 0:
        assert(waffle[j][2 * (i - NUM_WORDS // 2)] == words[i][j])
      waffle[j][2 * (i - NUM_WORDS // 2)] = words[i][j]

  for i in range(BOARD_SIZE):
    print(''.join(waffle[i]))
  print()

for letter in middle:
  for vert_mid in middle[letter]:
    for horz_mid in middle[letter]:
      if vert_mid == horz_mid:
        continue
      for first_row in middle[vert_mid[0]]:
        if first_row in [vert_mid, horz_mid]:
          continue
        for first_column in first_middle[(first_row[0], horz_mid[0])]:
          if first_column in [first_row, vert_mid, horz_mid]:
            continue
          for last_row in first_middle[(first_column[-1], vert_mid[-1])]:
            if last_row in [vert_mid, horz_mid, first_row, first_column]:
              continue
            for last_column in first_middle_end[(first_row[-1], horz_mid[-1], last_row[-1])]:
              if last_column in [vert_mid, horz_mid, first_row, first_column, last_row]:
                continue
              words = [first_row, horz_mid, last_row, first_column, vert_mid, last_column]
              print_words_as_waffle(words)
