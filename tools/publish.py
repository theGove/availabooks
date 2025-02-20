import requests
import json
import sys
import os
import pprint 
import hashlib
import common
from bs4 import BeautifulSoup

bookInfo={
  'posts':{},
  'names':{},
  'year': None,
  'month': None,
  'blogName': None,
  'bookInfoPostId': "",
  'systemPostId': "",
}  # used to hold book info (hashes) and other information about a book

#globals
pp = pprint.PrettyPrinter(indent=4)
systemRoot=""
gasEndPoint = '' # this is used for contacting the google AppsScript blogger code 
toolPath = '' # this is the path used for config.json

def extract_body_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    body = soup.body
    return body.get_text(separator='\n', strip=True) if body else ''

def getGasEndpoint():
  with open(os.path.join(toolPath, 'config.json')) as f:
    config = json.load(f)
  return 'https://script.google.com/macros/s/'+config["deploymentId"]+'/exec'


def getBlogId(blogName):
  if "blogId" in bookInfo:
    return bookInfo["blogId"]
  else:
    return getBlogInfo(blogName)["blogId"]
  
  
def getBlogInfo(blogName):
  url = f"https://{blogName}.blogspot.com/feeds/posts/default?max-results=0"
  reply = requests.get(url)
  blogId=reply.text.split("blog-")[1].split("<")[0]
  bookInfo["blogId"] = blogId
  return {'blogId':blogId}

def postIdFromUrl(url):
  # takes a url to a blog post and returns its post id
  reply = requests.get(url)
  text=reply.text
  postId = text.split("id='post-body-")[1].split("'")[0]
  return postId


def updateOneSystem(blog, fileContents):
  global gasEndPoint
  global bookInfo

  if len(bookInfo['systemPostId'])==0:
    bookInfo['systemPostId']=postIdFromUrl('https://' + bookInfo['blogName'] + '.blogspot.com/1970/01/system.html')

  if gasEndPoint == '':
    gasEndPoint = getGasEndpoint()      
  

  print("bookInfo['systemPostId']",bookInfo['systemPostId'])
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
  print(bookInfo['blogName'], bookInfo['year'], bookInfo['month'])
  if len(bookInfo['bookInfoPostId'])==0:
    url='https://' + bookInfo['blogName'] + '.blogspot.com/' + bookInfo['year'] +'/' + bookInfo['month']+'/bookinformation.html'
    print("url", url)
    bookInfo['bookInfoPostId']=postIdFromUrl(url)

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
  if "updated" in response:
    print("Updated Hashes: " , response['updated'])
  else:
    print("failed Hashes: " , response)
    sys.exit() # done.  We think we out ran the blogger api limits  
  
def createPost(blog, year, month, filename, fileContents):
  global gasEndPoint
  blogId = getBlogId(blog)

  if gasEndPoint == '':
    gasEndPoint = getGasEndpoint()   
  print (gasEndPoint)
  
  payload = {
      'mode':'create-post'
      ,'blog':blogId
      ,'content':fileContents
      ,'debug': 'true'
      ,"published":f"{year}-{month}-01T01:02:20-07:00"    
      ,"title":filename
  }

  reply = requests.post(gasEndPoint, json = payload)
  response = json.loads(reply.text)
  
  print("created Post: " , response['updated'])
  return response['id']


def updateOnePost(blog, year, month, fileName, fileContents, title):
  global bookInfo
  global gasEndPoint
  fileContentsHash = hash_unicode_string(fileContents)
  print("fileName", fileName)
  fileKey = fileName.split('.')[0]

  if fileKey in bookInfo['names'] and bookInfo['names'][fileKey]['hash'] == fileContentsHash:
    print(fileName + ' already up to date.')
  else:
    if gasEndPoint == '':
      gasEndPoint = getGasEndpoint()


    if fileKey not in bookInfo['names']:
      # get any new post information
      chapters=common.getChaptersForBook(blog,year,month)
      # print("chapters", chapters)
      for key, entry in chapters.items():
        # print(key, entry)
        if entry['postId'] not in bookInfo['posts']:
          bookInfo['posts'][entry['postId']] = {
            'name': key,
            'hash': ''
          }
          bookInfo['names'][key] = {
            'hash': '',
            'id': entry['postId']
          }

      
    payload = {
        'post': bookInfo['names'][fileKey]['id']
        ,'blog':getBlogInfo(blog)['blogId']
        ,'title':title
        ,'content':fileContents
        ,'mode':'update-post'
        ,'debug': 'true'
    }
    reply = requests.post(gasEndPoint, json = payload)
    response = json.loads(reply.text)

    if "updated" in response:
      print("Post Updated: " , response['updated'])
    else :
      print("Post Updated: " , response)
      sys.exit() # done.  We think we out ran the blogger api limits  
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



def getBookInfo(blog, year, month):
  url= f"https://{blog}.blogspot.com/{year}/{month}/bookinformation.html"
  reply = requests.get(url)
  if reply.status_code == 200:
    jsonText=reply.text.split("<pre>")[1].split("</pre>")[0]
    bookInfo['posts']=json.loads(jsonText)['posts']
    bookInfo["bookInfoPostId"]=reply.text.split("id='post-body-")[1].split("'")[0] # get the post id
  else:  
    # file not found.  create a new one
    bookInfo["bookInfoPostId"] = createPost(blog, year, month, "bookinformation", '<pre>{"posts": {}}</pre>')
    bookInfo["posts"] = {}
  
  
  for key in bookInfo['posts']:
    bookInfo['names'][bookInfo['posts'][key]['name']] = {
      'hash':bookInfo['posts'][key]['hash'],
      'id': key
    }
  bookInfo['year'] = year
  bookInfo['month'] = month
  bookInfo['blogName'] = blog

def updateBlog(blog,year,month):
  workingPath = os.getcwd()
  print("updating:", blog, year, month, workingPath)
  for root, dirs, files in os.walk(workingPath):
    updateBookPosts(blog, year, month, files)
    # for filename in files:
    #   filePath = os.path.join(root, filename)
    #   print("filename",filename, filename.split(".")[0])
    #   with open(filePath, "r",encoding='utf-8') as file:
    #       fileContents = BeautifulSoup(file.read(), 'html.parser').body.decode_contents()
    #   updateOnePost(blog, year, month, filename, fileContents)

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
      updateOneSystem(blog,fileContents)
    else:  
      # must be a regular post
      # print (os.path.join(workingPath,fileName))
      filePath = os.path.join(systemRoot,"blogger",blog,year,month,fileName)
      if os.path.exists(filePath):
        with open(filePath, "r",encoding='utf-8') as file:
          soup=BeautifulSoup(file.read(), 'html.parser')
          h1=soup.find("h1")
          title = h1.get_text()
          h1.decompose()
          fileContents = soup.body.decode_contents()
        updateOnePost(blog, year, month, fileName, fileContents, title)
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
    print("Executing: ", scriptName)
    bookInfo = script['bookInfo']  
    args=script['args']
    updateBookPosts(bookInfo['blogName'], bookInfo['year'], bookInfo['month'], args)

  elif common.isBookHome(workingPath):
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

def hash_unicode_string(string):
  #Hashes a Unicode string using SHA-256/

  # Encode the string to bytes using UTF-8 encoding
  encoded_string = string.encode('utf-8') 

  # Create a SHA-256 hash object
  hash_object = hashlib.sha256(encoded_string)

  # Get the hexadecimal representation of the hash
  hex_digest = hash_object.hexdigest()

  return hex_digest  

if __name__=="__main__":
    main()