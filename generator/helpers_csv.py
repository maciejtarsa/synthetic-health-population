#!/usr/bin/python3
import csv

# a helper function creates a new empty csv file
def create_csv(location, headers):
  """
  Create an empty csv file with set headers
  Parameters:
    location: file location, incl file name
    headers: list of headers to use
  Returns:
    None
  """
  with open(location, 'w') as f:
    f.write(headers + "\n")
    f.close
  
# a helper function to append to a csv file
def append_to_csv(location, data):
  """
  Append to an existing csv file
  Parameters:
    location: file location, incl file name
    data: data to append
  Returns:
    None
  """
  with open(location, 'a') as f:
        writer = csv.writer(f)
        writer.writerow(data)
