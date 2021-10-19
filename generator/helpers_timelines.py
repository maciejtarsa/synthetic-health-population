#!/usr/bin/python3
from random import choices

# a helper function for setting initial probabilities for each module
def set_initial_prob(module, data, patient, debug):
    """
    Set initial probabilities for each module
    Including recalculating them based on static characteristics
    Parameters:
        module: module name
        data: a dataframe of input settings
        patient: a dictionary of patient object
        debug: boolean, whether to show debugging information
    Returns:
        states: a list of possible states
        posterior_trans_prob: posterior state transition probabilities
    """
    # set states
    states = data.iloc[:,3:-1].columns.tolist()
    # extract the prior transition probabilities
    prior_trans_prob = data.loc[data['type'] == 'PriorTransProb']
    # and static characteristics
    static_char = data.loc[data['type'] == 'StaticChar']
    # set posterior transition probabilities
    posterior_trans_prob = []
    # iterate over a number of states
    for i in range(len(states)):
      posterior_trans_prob.append(prior_trans_prob.iloc[i,3:-1].values.tolist())

    if debug:
      print()
      print(f"Module: {module}")
      print(f"Possible states: {states}")
      print(f"Prior state transition probabilities: "+str([[f"{x:.3f}" for x in y] for y in posterior_trans_prob]))

    ## amend prior transition probabilities based on static characteristics
    for row in static_char.itertuples():
      multiplications, changed = amend_prob_char(row, patient, debug)
      if changed:
        posterior_trans_prob = amend_prob(posterior_trans_prob, [multiplications]*len(states))
        if debug:
          print(f"- Posterior state transition probabilities: "+str([[f"{x:.3f}" for x in y] for y in posterior_trans_prob]))

    return states, posterior_trans_prob

# a helper function for selecting next state from a list of states with probabilities
def mcmc(states, probabilities, initial_state):
  """
  Returns the next state given an initial state
  Parameters:
    states: a list of possble states
    probabilities: a matrix of probabilities of each state turning into another
    initial_state: a string containing one of the possible states
  Returns:
    next_state: next_state calculated based on probabilities
  """
  # first, generate a list of possible transitions
  transitions = []
  # iterate through the transitions twice
  for state1 in states:
    state_transitions = []
    for state2 in states:
      state_transitions.append((state1, state2)) 
      transitions.append(state_transitions)
  # set up an empty return value
  next_state = ''
  # based on given probabilities, choose the next state
  for i in range(len(states)):
      if initial_state == states[i]:
        change = choices(transitions[i], probabilities[i], k=1)[0]
        for j in range(len(states)):
          if change == transitions[i][j]:
            next_state = states[i]
          if change == transitions[i][j]:
            next_state = states[j]
          if change == transitions[i][j]:
            next_state = states[j]
  return next_state

# a fuction to amend probabilities based on multiplication values
def amend_prob(probabilities, amendments):
  """
  Amend probabilities based on provided values
  Parameters:
    probabilities: a list of list of probabilities for transitions
    amendments: a list of lists of values to multiply the probabilities by
  Returns:
    normalised list of lists of probabilities
  """
  for i in range(len(probabilities)):
    probabilities[i] = [a*b for a,b in zip(probabilities[i], amendments[i])]
    # normalise
    probabilities[i] = [float(j)/sum(probabilities[i]) for j in probabilities[i]]
  return probabilities

# a function to check for relevant
def check_char_equality(char, data, debug):
  """
  A function to check if the characteristics is equal, greater than or less than
  Parameters:
    char: details of the characteristic
    data: either patient data, current timeline or previous tmeline
  Returns:
    changed: a boolean value of whether the mutliplications have been changed
    mult: multiplication values to use
  """
  # get the number of possible states
  no_states = len(char[4:-1])
  # by default, set multiplicaton to to a list of 1s
  mult = [1 for i in range(no_states)]
  # set changed to False by default
  changed = False

  # check if it refers to greater than
  if char[3][0] == '>':
    if int(data[char[2]]) > int(char[3][1:]):
      # get multiplication values
      mult = char[4:-1]
      changed = True
      print_multiplications(char[2],char[3], mult, debug)
  # or less than
  elif char[3][0] == '<':
    if int(data[char[2]]) < int(char[3][1:]):
      mult = char[4:-1]
      changed = True
      print_multiplications(char[2],char[3], mult, debug)
  # otherwise assume equals
  else:
    if data[char[2]] == char[3]:
      mult= char[4:-1]
      changed = True
      print_multiplications(char[2],char[3], mult, debug)

  return changed, mult

# a function to multiply probabilities based on characteristics
def amend_prob_char(char, current_data, debug, previous_data = {}):
  """
  A function to iterate over given characteristics and extract relevant
  multiplications.
  Parameters:
    char: a row of a dataframe containing characteristics
    current_data: a dictionary containing patient or timeline information
    debug: boolean, whether to show debugging information
    previous_data: a dictionary containing previous timeline, by default an empty dict
  Returns:
    mult: either list of 1s or multiplication to multiply probabilities by
    changed: a boolean value of whether the mutliplications have been changed
  """
  # get the number of possible states
  no_states = len(char[4:-1])
  # by default, set multiplicaton to to a list of 1s
  mult = [1 for i in range(no_states)]
  # set changed to False by default
  changed = False

  # check for current data
  if char[2] in set(current_data.keys()):
    # get multiplication if relevant
    changed, mult = check_char_equality(char, current_data, debug)

  # check if that characteristic is present in previous timeline
  # this allows for circular dependencies to take effect
  elif (previous_data != None) & (char[2] in set(previous_data.keys())):
    # get multiplication if relevant
    changed, mult = check_char_equality(char, previous_data, debug)

  return mult, changed

# a helper for printing debugging information
def print_multiplications(variable, value, mult, debug):
  """
  A function to print debugging information when relevant
  Paramteres:
    variable: variable name
    value: variable's value
    multiplication: mutliplication values to use
    debug: boolean, whether to show debugging information
  Returns:
    None
  """
  if debug:
    print(f"- Relevant variable: {variable}; value: {value}")
    print(f"- Prior probabilities need multiplying by: {mult}")

# module runner
def run_module(module, data, age_range, patient, current_timeline, previous_timeline, module_dict, debug):
  """
  A function to generate a record for current age range.
  Parameters:
    module: module name
    data: input data for that module
    age_range: current age range
    patient: a dictionary of patient information
    current_timeline: a dictionary of current timeline so far
    previous_timeline: a dictionary of previours timeline
    module_dict: a dictionary of states and probabilities for modules
    debug: boolean, whether to show debugging information
  Returns:
    state: selected state
    module_dict: an updated dictionary of modules
  """
  # get the patients id
  id = patient['id']

  # extract states, t and m probabilities from the module dict
  states = module_dict[module][0]
  posterior_trans_prob = module_dict[module][1]

  # extract the demographic details
  prior_initial_prob = data.loc[data['type'] == 'PriorInitialProb']
  static_char = data.loc[data['type'] == 'StaticChar']
  dynamic_char = data.loc[data['type'] == 'DynamicChar']

  if debug:
    print(f"---------------------")
    print(f"Module: {module}")
    print(f"---------------------")

  # if age range is included in the initial set up
  if age_range in set(prior_initial_prob['value'].values):
    ## initial set up
    # get the relevant prior initial probabilities
    probabilities = prior_initial_prob.loc[prior_initial_prob['value'] == age_range][states].values
    if debug:
      print(f"- Initial probabilities: {probabilities}")
    ## amend initial setup based on static characteristics
    for row in static_char.itertuples():
      mult, changed = amend_prob_char(row, patient, debug)
      if changed:
        probabilities = amend_prob(probabilities, [mult])
        if debug:
          print(f"- Posterior probabilities: "+str([[f"{x:.3f}" for x in y] for y in probabilities]))

    # choose the state
    module_state = choices(states, probabilities[0], k=1)[0]
    if debug:
      print(f"== Selected state: {module_state} ==")

  ## transitions
  # if age_range is not included in the set up
  if age_range not in set(prior_initial_prob['value'].values):
    if debug:
      print(f"- Prior state transition probabilities: "+str([[f"{x:.3f}" for x in y] for y in posterior_trans_prob]))
    # amend transitions based on dynamic characteristics
    for row in dynamic_char.itertuples():
      mult, changed = amend_prob_char(row, current_timeline, debug, previous_timeline)
      if changed:
        posterior_trans_prob = amend_prob(posterior_trans_prob, [mult]*len(states))
        if debug:
          print(f"- Posterior state transition probabilities: "+str([[f"{x:.3f}" for x in y] for y in posterior_trans_prob]))

    # choose the next state
    module_state = mcmc(states, posterior_trans_prob, module_dict[module][2])
  
  # update the module dictionary with new t probabilities
  module_dict[module] = (states, posterior_trans_prob, module_state)

  # return the status for that timeline and module and the update module_dict
  return module_state, module_dict