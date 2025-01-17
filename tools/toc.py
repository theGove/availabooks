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

def getGasEndpoint():
  with open(os.path.join(toolPath, 'config.json')) as f:
    config = json.load(f)
  return 'https://script.google.com/macros/s/'+config["deploymentId"]+'/exec'


def isInteger(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    
def postIdFromUrl(url):
  # takes a url to a blog post and returns its post id
  reply = requests.get(url)
  text=reply.text
  postId = text.split("id='post-body-")[1].split("'")[0]
  blogId = text.split("{'blogId': '")[1].split("'")[0]
  
  return {"blogId":blogId,"postId":postId}


def updateOnePost(blogName, year, month, fileContents, title=""):
  global bookInfo
  global gasEndPoint
  if gasEndPoint == '':
    gasEndPoint = getGasEndpoint()


  ids= postIdFromUrl(f'https://{blogName}.blogspot.com/{year}/{month}/toc.html')

      
  payload = {
      'post': ids["postId"]
      ,'blog':ids['blogId']
      ,'content':fileContents
      ,'mode':'update-post'
      ,'debug': 'true'
  }

  if len(title)>0:
    payload["title"] = title # if title is not empty, add it to the payload

  reply = requests.post(gasEndPoint, json = payload)
  response = json.loads(reply.text)

  if "updated" in response:
    print("Post Updated: " , response['updated'])
  else :
    print("Post Failed: " , response)
    print("We think we out ran the blogger api limits")
    sys.exit() # done.  We think we out ran the blogger api limits  



def extract_headings_hierarchy(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    hierarchy = []

    current_level = {i: None for i in range(1, 7)}

    for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        print("heading",heading.get_text(strip=True))
        level = int(heading.name[1])

        if heading.name == "h1": # h1 are chapter names and treated differently
          heading_text = heading.get_text(strip=True).replace(":",chr(30),1).split(chr(30))[1].lstrip()
          heading_id=0
        else:  
          spans = heading.find_all("span")
          heading_text = spans[1].get_text(strip=True)
          heading_id = spans[0].get_text(strip=True).replace(":","").replace(".","-")

        heading_dict = {'text': heading_text,'id': heading_id}

        if level == 1:
            hierarchy.append(heading_dict)
            current_level[1] = heading_dict
        else:
            parent = current_level[level - 1]
            if parent:
              if "sections" not in parent:
                parent['sections']=[]
              parent['sections'].append(heading_dict)

            current_level[level] = heading_dict

        # Reset lower levels
        for i in range(level + 1, 7):
            current_level[i] = None

    return hierarchy


def buildToc(blogName, year, month):
  # update a set of posts in a given book  
  toc=[]
  files_list = []
  for root, dirs, files in os.walk(os.getcwd()):
    for file in files:
      bareFileName = file.split(".")[0]
      if isInteger(bareFileName):
        files_list.append(int(bareFileName))
  files_list.sort()      

  for i in files_list:
    with open(f"{i}.html", "r",encoding='utf-8') as f:
      html_content = f.read()
      bookNumber = json.loads(html_content.split("<!--")[1].split("-->")[0])['bookNumber']
      chapterToc=extract_headings_hierarchy(html_content)[0]
      chapterToc["id"] = str(i)
      toc.append(chapterToc)
  toc[-1]["end"] = True
  
  path=os.getcwd().split("blogger")[0]
  print("path",path)
  with open(os.path.join(path,"source",str(bookNumber),"settings.json") , "r") as f:
    bookSettings = json.load(f)

  
  html=['<div style="display:none" id="toc-json">']
  html.append(json.dumps({"bookInfo":bookSettings["bookInfo"],"chapters":toc}, indent=4))
  html.append("</div     >")# the spaces are to make it different from any div that might end up in the toc

  # build the HTML version of the title page
  html.append(f'<div class="book-title">{bookSettings["bookInfo"]["title"]}</div>')
  html.append(f'<div class="book-author">{joinWithCommasAnd(bookSettings["bookInfo"]["authors"])}</div>')
  html.append(f'<div class="book-toc">')
  html.append(f'<div class="book-chapters">')
  print(year, month)
  
  for chapter in toc:
    html.append(f'<div class="book-chapter"><a href="/{year}/{month}/{chapter["id"]}.html">{bookSettings["bookInfo"]["chapterLabel"]} {chapter["id"]}: {chapter["text"]}</a></div>')
  
  
  html.append(f'</div>')
  html.append(f'</div>')


  updateOnePost(blogName, year, month, "\n".join(html))
  print ("done with book #", bookNumber)
  
def joinWithCommasAnd(lst):
    if not lst:
        return ""
    elif len(lst) == 1:
        return lst[0]
    elif len(lst) == 2:
        return f"{lst[0]} and {lst[1]}"
    else:
        return ", ".join(lst[:-1]) + f", and {lst[-1]}"
      
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


  if common.isBookHome(workingPath):
    bookPath = workingPath.split(os.path.sep)
    month = bookPath.pop()
    year = bookPath.pop()
    blogName = bookPath.pop()
    buildToc(blogName, year, month)
  else:
    print()
    print()
    print("You must change to a directory that is the root of a book")
    print("(ends with something like'/2024/02')")
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