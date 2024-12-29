import os
def dictionaryContains(theDict, key, value):
  # returns true if dict is a dictionary and it has the specified key value pair
  if isinstance(theDict,dict):
    if key in theDict:
      if theDict[key]==value:
        return True
  return False    


def fixArray(item):
  # if item is an array, returns item, otherwise, returns an array with one value, item
  if isinstance(item,list):
    return item
  return [item]

def intersection(arr1, arr2):
    # returns the intersection of two arrays
    set1 = set(fixArray(arr1))
    set2 = set(fixArray(arr2))
    return list(set1.intersection(set2))

def isBookHome(path):
  # check to see path ends with a folder numbered 
  # 01-12 with a parent that is a four digit year 
  # greater than 1969 and less than 2100.  

  pathList = path.split(os.path.sep)
  if len(pathList) < 2:
    return False  # path not long enough
  
  ultimateFolder=pathList.pop()
  penultimateFolder=pathList.pop()

  if len(ultimateFolder) != 2 or len(penultimateFolder) != 4:
    return False # ending folders not right length
  
  if ultimateFolder.isnumeric() != True or ultimateFolder.isnumeric() != True:
    return False # ending folders not numeric
  
  penultimateFolder=int(penultimateFolder)
  ultimateFolder=int(ultimateFolder)
  
  if ultimateFolder < 1 or ultimateFolder > 12:
    return False # ultimate folder is not a month

  if penultimateFolder < 1970 or penultimateFolder > 2100:
    return False # penultimate folder is not a a valid year
  
  return True # passed all checks
