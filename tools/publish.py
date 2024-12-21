import requests
import json
import sys
import os
import pprint 

pp = pprint.PrettyPrinter(indent=4)

systemRoot=""
bookInfo={
  'posts':{},
  'names':{},
  'year': None,
  'month': None,
  'blogName': None,
  'bookInfoPostId': "",
  'systemPostId': "",
}  # used to hold book info (hashes) and other information about a book

gasEndPoint = '' # this is used for contacting the google AppsScript blogger code 
toolPath = '' # this is the path used for config.json

def getGasEndpoint():
  with open(os.path.join(toolPath, 'config.json')) as f:
    config = json.load(f)
  return 'https://script.google.com/macros/s/'+config["deploymentId"]+'/exec'


def getBlogInfo(blogName):
  url = f"https://{blogName}.blogspot.com/feeds/posts/default?max-results=0"
  reply = requests.get(url)
  blogId=reply.text.split("blog-")[1].split("<")[0]
  return {'blogId':blogId}

def postIdFromUrl(url):
  # takes a url to a blog post and returns its post id
  reply = requests.get(url)
  return reply.text.split("id='post-body-")[1].split("'")[0]


def updateOneSystem(blog, year, month, fileContents):
  global gasEndPoint
  global bookInfo

  if len(bookInfo['systemPostId'])==0:
    bookInfo['systemPostId']=postIdFromUrl('https://' + bookInfo['blogName'] + '.blogspot.com/' + bookInfo['year'] +'/' + bookInfo['month']+'/system.html')

  if gasEndPoint == '':
    gasEndPoint = getGasEndpoint()      
  
  payload = {
      'post': bookInfo['systemPostId']
      ,'blog':getBlogInfo(bookInfo['blogName'])['blogId']
      ,'content':'<pre>' + fileContents +'</pre>'
      , 'mode':'update-post'
      ,'debug': 'true'    
  }

  reply = requests.post(gasEndPoint, json = payload)
  response = json.loads(reply.text)
  print("system Success: " , response['updated'])
  
def updateBookInfo():
  global gasEndPoint
  global bookInfo
  
  if len(bookInfo['bookInfoPostId']==0):
    bookInfo['bookInfoPostId']=postIdFromUrl('https://' + bookInfo['blogName'] + '.blogspot.com/' + bookInfo['year'] +'/' + bookInfo['month']+'/bookinformation.html')

  fileContents = {"posts": bookInfo['posts']}
  payload = {
      'post': bookInfo['bookInfoPostId']
      ,'blog':getBlogInfo(bookInfo['blogName'])['blogId']
      ,'content':'<pre>' + json.dumps(fileContents) +'</pre>'
      , 'mode':'update-post'
      ,'debug': 'true'    
  }

  reply = requests.post(gasEndPoint, json = payload)
  response = json.loads(reply.text)

  print("Hash Success: " , response['updated'])
  


def updateOnePost(blog, year, month, fileName, fileContents):
  global bookInfo
  global gasEndPoint
  fileContentsHash = hash(fileContents)
  fileKey = fileName.split('.')[0]


  if bookInfo['names'][fileKey]['hash'] == fileContentsHash:
    print(fileName + ' already up to date.')
  else:
    if gasEndPoint == '':
      gasEndPoint = getGasEndpoint()
    payload = {
        'post': bookInfo['names'][fileKey]['id']
        ,'blog':getBlogInfo(blog)['blogId']
        ,'content':fileContents
        , 'mode':'update-post'
        ,'debug': 'true'
    }
    reply = requests.post(gasEndPoint, json = payload)
    response = json.loads(reply.text)

    print("Success: " , response['updated'])
    bookInfo['names'][fileKey]['hash'] = fileContentsHash
    bookInfo['posts'][bookInfo['names'][fileKey]['id']]['hash'] = fileContentsHash
    updateBookInfo()

def publishOneFile(args):
  path = args.pop(0)
  blogName = args.pop(0)
  blogInfo = getBlogInfo(blogName)
  blogId = blogInfo["blogId"]
  
  print (blogInfo)
  return



  url = 'https://script.google.com/macros/s/'+config["deploymentId"]+'/exec'
  payload = {
      'post': '5777243347759718755'
      ,'blog':'2088387750640558372'
      ,'content':"<pre>"+contents+"</pre>"
      , 'mode':'update-post'
      ,'debug': 'true'
  }

  reply = requests.post(url, json = payload)
  response = json.loads(reply.text)

  print("Success: " + response.updated)


def getBookInfo(blog, year, month):
  url= f"https://{blog}.blogspot.com/{year}/{month}/bookinformation.html"
  reply = requests.get(url)
  jsonText=reply.text.split("<pre>")[1].split("</pre>")[0]
  
  bookInfo['posts']=json.loads(jsonText)['posts']
  
  for key in bookInfo['posts']:
    bookInfo['names'][bookInfo['posts'][key]['name']] = {
      'hash':bookInfo['posts'][key]['hash'],
      'id': key
    }
  bookInfo['year'] = year
  bookInfo['month'] = month
  bookInfo['blogName'] = blog
  bookInfo["bookInfoPostId"]=reply.text.split("id='post-body-")[1].split("'")[0] # get the post id

  

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
def updateBlog(blog,year,month):
  print("updating:", blog, year, month)

def updatePost(blog, year, month, filename, file):
  print("updating:", blog, year, month, filename)

def updateBookPosts(blog, year, month, postNames):
  # update a set of posts in a given book  

  getBookInfo(blog, year, month)
  for fileName in postNames:
    if fileName == "system.js":
      # need to find the system file and push it to this blog
      systemPath=os.path.join(systemRoot,"system")
      with open(os.path.join(systemPath,"system.js") , "r") as file:
        fileContents = file.read()
      updateOneSystem(blog,year,month,fileContents)
    else:  
      # must be a regular post
      # print (os.path.join(workingPath,fileName))
      filePath = os.path.join(systemRoot,blog,year,month,fileName)
      if os.path.exists(filePath):
        with open(filePath, "r") as file:
          fileContents = file.read()
        updateOnePost(blog, year, month, fileName, fileContents)
      else:
        print(filePath, " does not exist.")  

        
def main(): 
  # If no params are passed, we will look to see if we are in a 
  # folder numbered 01-12 with a parent that is a four digit year greater 
  # than 1969 and less than 2100. If so, this is a full publication of 
  # a book
  global systemRoot 
  global bookInfo
  global toolPath
  args=sys.argv
  path=__file__.split(os.path.sep)
  path = os.path.sep.join(path[:-1])
  workingPath = os.getcwd()
  toolPath = path
  systemRoot = os.path.dirname(toolPath)
  print("workingPath",workingPath)
  print("path",path)
  saveScript=False

  # look for saving parameters and pull them out if found
  if len(args) > 2: # an instruction to save must have at least 4 args: Script name, at least one file to upload, save, and the filename to save
    if args[-2] == "save":
      saveScript = True
      scriptNameToSave = args.pop()
      args.pop()  # remove "save"

  if workingPath.endswith("system"):
    ## hashes are not kept for system.  we just publish on command
    print("working path is system. push system to all books in this repo")
  elif workingPath==path:
    # we are running from inside the "tools" folder.  assume we will be running a script
    if len(args)==1:
      # not command line args were specified, we must run autoexec.json
      scriptName="autoexec.json"
    else:
      # second argument must be the name of the script to run  
      scriptName = args[1]
      if not scriptName.endswith(".json"):
        scriptName=scriptName + ".json"
    #now we have a scriptname ending with ".json"    
    with open(os.path.join(workingPath,"scripts",scriptName)) as f:
      script = json.load(f)
    print("Executing ", scriptName)
    bookInfo = script['bookInfo']  
    args=script['args']
    updateBookPosts(bookInfo['blogName'], bookInfo['year'], bookInfo['month'], args)

  elif isBookHome(workingPath):
    bookPath = workingPath.split(os.path.sep)
    month = bookPath.pop()
    year = bookPath.pop()
    blog = bookPath.pop()
    if len(args) == 1:
      # no args added at command line. publish book
      updateBlog(blog,year,month)
    else:
      # arguments were passed, assume they are file names in the book
      args.pop(0)
      updateBookPosts(blog, year, month, args)
  else:
    print()
    print()
    print("You must change to a directory that is either a the root of a book")
    print("(ends with '/2024/02') or the system folder (ends with '/system')")
    print()
    print("Optionally, you can also specify the particular file")
    print("or files  you want to update.")
    print()
    print()
    return

  # save the script if requested
  if saveScript:
    scriptObject = {
      'bookInfo': bookInfo,
      'args': args
    }

    if not scriptNameToSave.endswith(".json"):
      scriptNameToSave=scriptNameToSave + ".json"

    f = open(os.path.join(toolPath,"scripts",scriptNameToSave), "w")
    f.write(json.dumps(scriptObject))
    f.close()
    print("Successfully wrote " + scriptNameToSave)

  

if __name__=="__main__":
    main()