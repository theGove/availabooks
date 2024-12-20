import requests
import json
import sys
import os

bookInfo=""  # used to hold book info (hashes) if needed
gasEndPoint = '' # this is used for contacting the google AppsScript blogger code 
toolPath = '' # this is the path used for config.json
bookInfoPostId = '' #this id the post id so we can update the hash when a book is updated


def getBlogInfo(blogName):
  url = f"https://{blogName}.blogspot.com/feeds/posts/default?max-results=0"
  reply = requests.get(url)
  blogId=reply.text.split("blog-")[1].split("<")[0]
  return {'blogId':blogId}

def updateBookInfo():
  global gasEndPoint
  global bookInfoPostId
  global bookInfo
  url = f'https://{bookInfo['blogName']}.blogspot.com/{bookInfo['year']}/{bookInfo['month']}/bookinformation.html'
  

  reply = requests.get(url)
  postId=reply.text.split("'postId': '")[1].split("'")[0]
  fileContents = {"posts": bookInfo['posts']}
  payload = {
      'post': postId
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
      with open(os.path.join(toolPath, 'config.json')) as f:
        config = json.load(f)
      gasEndPoint = 'https://script.google.com/macros/s/'+config["deploymentId"]+'/exec'

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

  with open("script.js", "r") as file:
      contents = file.read()
  with open('config.json') as f:
    config = json.load(f)


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
  jsonObject = json.loads(jsonText)
  jsonObject['names'] = {}
  
  for key in jsonObject['posts']:
    jsonObject['names'][jsonObject['posts'][key]['name']] = {
      'hash':jsonObject['posts'][key]['hash'],
      'id': key
    }

  jsonObject['year'] = year
  jsonObject['month'] = month
  jsonObject['blogName'] = blog
  return jsonObject

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
        
def main(): 
  # If no params are passed, we will look to see if we are in a 
  # folder numbered 01-12 with a parent that is a four digit year greater 
  # than 1969 and less than 2100. If so, this is a full publication of 
  # a book 
  global bookInfo
  global toolPath
  args=sys.argv
  path=__file__.split(os.path.sep)
  path = os.path.sep.join(path[:-1])
  workingPath = os.getcwd()
  toolPath = path
  filePath = os.path.join(path,"args.json")
  print("workingPath",workingPath)
  print("filePath",filePath)

  if workingPath.endswith("system"):
    ## hashes are not kept for system.  we just publish on command
    print("working path is system. push system to all books in this repo")
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
      for fileName in args:
        if fileName == "system.js":
          # need to find the system file and push it to this blog
          print("need to implement publishing system to a single blog")
        else:  
          # must be a regular post
          # print (os.path.join(workingPath,fileName))
          if bookInfo == "":
            # get the book info
            bookInfo = getBookInfo(blog, year, month)
            print (bookInfo)
          filePath = os.path.join(workingPath,fileName)
          if os.path.exists(filePath):
            with open(filePath, "r") as file:
              fileContents = file.read()
            updateOnePost(blog, year, month, fileName, fileContents)
          else:
            print(filePath, " does not exist.")  

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
  if len(args)==1:
    with open(filePath, "r") as file:
      args = json.loads(file.read())
      print(args)
  else:  
    f = open(filePath, "w")
    f.write(json.dumps(args))
    f.close()


  print (args)



if __name__=="__main__":
    main()