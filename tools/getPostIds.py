#this script must be run from a source folder. it updates the config.json file to include the information needed to publish the book on blogger

# if a version does not have a "chapters" key, it will be assumed that the chapters are in the blog itself and the script will get the list of chapters from the blog

# this version reads the set of chapters from the blog itself


import xmltodict
import requests
import json
import sys
import os
import markdown

import common # local file

#globals
systemRoot=""
toolPath = '' # this is the path used for config.json
settings={} # to hold settings for the book


def getPostObject(blogName, year, month, postNumber):
  url = f"https://{blogName}.blogspot.com/{year}/{month:02}/{postNumber}.html"
  
  reply = requests.get(url)
  text = reply.text
  
  blogId=text.split("{'blogId': '")[1].split("'")[0]
  postId=text.split("'postId': '")[1].split("'")[0]
  return {"blogId":blogId,"postId":postId}

def main(): 
  global systemRoot 
  global toolPath
  global month
  global year
  global blog
  args=sys.argv
  path=__file__.split(os.path.sep)
  path = os.path.sep.join(path[:-1])
  workingPath = os.getcwd()
  toolPath = path
  print("workingPath",workingPath)
  try:
    with open(os.path.join(workingPath,"settings.json") , "r") as f:
      settings = json.load(f)
  except:
    print()
    print()
    print("You must change to a directory contains settings.json.")
    print("It should be the source folder of a book")
    print()
    print()
    return

  

  for key in settings["versions"]:
    version=settings["versions"][key]
    print(key, version)
    print(version["blog"], version)
    if "chapters" not in version:
      settings["versions"][key]["chapters"]=common.getChaptersForBook(version["blog"],version["year"],version["month"])
    else:
      for chapterKey in version["chapters"]:
        chapter = version["chapters"][chapterKey]
        
        if("postId" not in chapter):
          # need to get the chapter's post id
          print(chapterKey)
          
          if "out" in chapter:
            chap = chapter["out"]
          else:
            chap = int(chapterKey)

          obj=getPostObject(version["blog"],version["year"],version["month"],chap)
          chapter["postId"]=obj["postId"]
          if "blogID" not in version:
            version["blogId"]=obj["blogId"]
      # print("settings", settings)      

  f = open(os.path.join(workingPath,"settings.json"), "w")
  f.write(json.dumps(settings, indent=2))
  f.close()
  print("done.")
      


if __name__=="__main__":
    main()