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
        posterior_transition_prob: posterior state transition probabilities
        multiply_transitions: state transition multiplication
    """
    # set states
    states = data.iloc[:,3:-1].columns.tolist()
    # extract the prior transition probabilities
    prior_transition_prob = data.loc[data['type'] == 'PriorTransitionProbabilities']
    # and the multiplication values
    multiplication_values = data.loc[data['type'] == 'MultiplicationValues']
    # and static characteristics
    static_char = data.loc[data['type'] == 'StaticCharacteristics']
    # set posterior transition probabilities and mutliply transitions
    posterior_transition_prob = []
    multiply_transitions = []
    # iterate over a number of states
    for i in range(len(states)):
      posterior_transition_prob.append(prior_transition_prob.iloc[i,3:-1].values.tolist())
      multiply_transitions.append(multiplication_values.iloc[i,3:-1].values.tolist())

    if debug:
      print()
      print(f"Module: {module}")
      print(f"Possible states: {states}")
      print(f"Prior state transition probabilities: "+str([[f"{x:.3f}" for x in y] for y in posterior_transition_prob]))

    ## amend prior transition probabilities based on static characteristics
    for index, row in static_char.iterrows():
      multiplications, changed = amend_prob_char(row, patient, debug)
      if changed:
        posterior_transition_prob = amend_prob(posterior_transition_prob, [multiplications]*len(states))
        if debug:
          print(f"- Posterior state transition probabilities: "+str([[f"{x:.3f}" for x in y] for y in posterior_transition_prob]))

    return states, posterior_transition_prob, multiply_transitions

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

# a function to multiply probabilities based on characteristics
def amend_prob_char(characteristic, current_data, debug, previous_data = {}):
  """
  A function to iterate over given characteristics and extract relevant
  multiplications.
  Parameters:
    characteristics: a row of a dataframe containing characteristics
    current_data: a dictionary containing patient or timeline information
    debug: boolean, whether to show debugging information
    previous_data: a dictionary containing previous timeline, by default an empty dict
  Returns:
    mulitplications: either list of 1s or multiplication to multiply probabilities by
    changed: a boolean value of whether the mutliplications have been changed
  """
  # get the number of possible states
  no_states = len(characteristic[3:-1])

  # set changed to False by default
  changed = False

  # by default, set multiplicaton to to a list of 1s
  multiplications = [1 for i in range(no_states)]

  if characteristic['variable'] in current_data.keys():
    # check if it refers to greater than
    if characteristic['value'][0] == '>':
      if int(current_data[characteristic['variable']]) > int(characteristic['value'][1:]):
        # get multiplication values
        multiplications = characteristic[3:-1].values
        changed = True
        print_multiplications(characteristic['variable'],characteristic['value'], multiplications, debug)
    # or less than
    elif characteristic['value'][0] == '<':
      if int(current_data[characteristic['variable']]) < int(characteristic['value'][1:]):
        multiplications = characteristic[3:-1].values
        changed = True
        print_multiplications(characteristic['variable'],characteristic['value'], multiplications, debug)
    # otherwise assume equals
    else:
      if current_data[characteristic['variable']] == characteristic['value']:
        multiplications = characteristic[3:-1].values
        changed = True
        print_multiplications(characteristic['variable'],characteristic['value'], multiplications, debug)
    
  # check if that characteristic is present in previous timeline
  # this allows for circular dependencies to take effect
  elif (previous_data != None) & (characteristic['variable'] in previous_data.keys()):
    # check if it refers to greater than
    if characteristic['value'][0] == '>':
      if int(previous_data[characteristic['variable']]) > int(characteristic['value'][1:]):
        # get multiplication values
        multiplications = characteristic[3:-1].values
        changed = True
        print_multiplications(characteristic['variable'],characteristic['value'], multiplications, debug)
    # or less than
    elif characteristic['value'][0] == '<':
      if int(previous_data[characteristic['variable']]) < int(characteristic['value'][1:]):
        multiplications = characteristic[3:-1].values
        changed = True
        print_multiplications(characteristic['variable'],characteristic['value'], multiplications, debug)
    # otherwise assume equals
    else:
      if previous_data[characteristic['variable']] == characteristic['value']:
        multiplications = characteristic[3:-1].values
        changed = True
        print_multiplications(characteristic['variable'],characteristic['value'], multiplications, debug)

  return multiplications, changed

# a helper for printing debugging information
def print_multiplications(variable, value, multiplications, debug):
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
    print(f"- Prior probabilities need multiplying by: {multiplications}")

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
  posterior_transition_prob = module_dict[module][1]
  multiply_transitions = module_dict[module][2]

  # extract the demographic details
  prior_probabilities = data.loc[data['type'] == 'PriorProbabilities']
  char_static = data.loc[data['type'] == 'StaticCharacteristics']
  char_dynamic = data.loc[data['type'] == 'DynamicCharacteristics']

  if debug:
    print(f"---------------------")
    print(f"Module: {module}")
    print(f"---------------------")

  # if age range is included in the initial set up
  if age_range in prior_probabilities['value'].values:
    ## initial set up
    # iterate over each variable and amend as relevant
    for index, row in prior_probabilities.iterrows():
      if age_range == row['value']:
        probabilities = row[3:-1].values
        
    if debug:
      print(f"- Initial probabilities: {probabilities}")
    ## amend initial setup based on static characteristics
    for index, row in char_static.iterrows():
      multiplications, changed = amend_prob_char(row, patient, debug)
      if changed:
        probabilities = amend_prob([probabilities], [multiplications])[0]
        if debug:
          print(f"- Posterior probabilities: "+str([f"{x:.3f}" for x in probabilities]))

    # set the state status
    state_status = choices(states, probabilities, k=1)[0]
    if debug:
      print(f"== Selected state: {state_status} ==")

  ## transitions
  # if age_range is not included in the set up
  if age_range not in prior_probabilities['value'].values:
    if debug:
      print(f"- Prior state transition probabilities: "+str([[f"{x:.3f}" for x in y] for y in posterior_transition_prob]))
    # amend transitions based on dynamic characteristics
    for index, row in char_dynamic.iterrows():
      multiplications, changed = amend_prob_char(row, current_timeline, debug, previous_timeline)
      if changed:
        posterior_transition_prob = amend_prob(posterior_transition_prob, [multiplications]*len(states))
        if debug:
          print(f"- Posterior state transition probabilities: "+str([[f"{x:.3f}" for x in y] for y in posterior_transition_prob]))

    # choose the next state
    state_status = mcmc(states, posterior_transition_prob, module_dict[module][3])
    # amend the probabilities based on multiplications
    # ready for the next age range
    posterior_transition_prob = amend_prob(posterior_transition_prob, multiply_transitions)
    if debug:
      print(f"== Selected state: {state_status} ==")
      print(f"- Multiplications to apply for the next state: {multiply_transitions}")
      print(f"- Posterior state transition probabilities: "+str([[f"{x:.3f}" for x in y] for y in posterior_transition_prob]))

  # update the module dictionary with new t probabilities
  module_dict[module] = (states, posterior_transition_prob, multiply_transitions, state_status)

  # return the status for that timeline and module and the update module_dict
  return state_status, module_dict