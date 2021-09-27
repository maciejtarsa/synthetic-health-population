#!/usr/bin/python3
import random

# a helper function that generates a random id number
def generate_random_id():
  """
  Generate a random 7 digit id number
  Parameters:
    none
  Returns:
    id: a randomly generated id number
  """
  return ''.join(str(random.randint(0,9)) for _ in range(7))

# a helper function that generates a New Zealand NHI number
def generate_nhi_id():
  """
  Generates a valid NHI number
  Parameters:
    none
  Returns:
    id: a valid NHI number
  """
  # set a list of letters - does not contain `O` or `I`
  letters = "ABCDEFGHJKLMNPQRSTUVWXYZ"
  # set the valid variable to False
  valid = False
  # iterate until a valid id is generated
  while not(valid):
    # generate 3 random letters
    alpha = ''.join(random.choice(letters) for _ in range(3))
    # generate 3 random numbers
    numeric = ''.join(str(random.randint(0,9)) for _ in range(3))
    # calculate the sum of letters
    alpha_values = [letters.index(char) + 1 for char in alpha]
    alpha_sum = sum([a * b for a, b in zip(alpha_values, [7, 6, 5])])
    # calculate the sum of numbers
    numeric_sum = int(numeric[0])*4 + int(numeric[1])*3 + int(numeric[2])*2
    # calculate the check sum
    check_sum = (alpha_sum + numeric_sum)%11
    if check_sum != 0:
      check_digit = 11 - check_sum
      if check_digit == 10:
        check_digit = 0
      valid = True
      id = alpha + numeric + str(check_digit)
      return id

