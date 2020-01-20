#!/usr/bin/env python3.8

import random

adjectives = ["Bacon", "Dirty", "Parole", "Chest", "Coffee", "Blueberry", "Cookie", "Beetle", "Electric", "Fried", "Fries", "Fudge", "Maybe", "Mister Duck", "Butter Me"]

nouns = ["Farm", "Shirty", "Baby", "Words", "Noodles", "Socks", "Mischief", "Squeeze", "Ham", "Clown", "Matter", "Patrol", "Gravy", "Lumps", "Queasy"]

def gen(l_one: list, l_two: list) -> str:
  return "{} {}".format(
    random.choice(l_one),
    random.choice(l_two)
  )

for _ in range(10):
  print(gen(adjectives, nouns))
