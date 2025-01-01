#this script transcodes original work (usually markdown) into the various HTML files that will be hosted on blogger

import json
import sys
import os
import markdown
from bs4 import BeautifulSoup
from pathlib import Path


import common # local file

#globals
bloggerPath = "" #where the blogger files start in the local file system
workingPath = "" #where the source files are
toolPath = '' # this is the path used for config.json
settings={} # to hold settings for the book

def processOneFile(chapter, version):
  # currently assuming all source files are markdown
 #print ("version",version)
 #print ("chapter",chapter)
 #print ("======",settings["versions"][version])
  if "out" in settings["versions"][version]["chapters"][str(chapter)]:
    outChapter=str(settings["versions"][version]["chapters"][str(chapter)]["out"])    
  else:
    outChapter=str(chapter)

  fileName = outChapter + ".md"
  conditionals = settings["versions"][version]["condition"]
  blog=settings["versions"][version]["blog"]
  year=settings["versions"][version]["year"]
  month=settings["versions"][version]["month"]
  filePath = os.path.join(workingPath,fileName)
  htmlPath = os.path.join(bloggerPath,blog,str(year),f"{month:02}")
  Path(htmlPath).mkdir(parents=True, exist_ok=True)
  htmlPath = os.path.join(htmlPath,str(chapter) + ".html")
  # take in the markdown file
  with open(filePath , "r", encoding='utf-8') as file:
    contents=file.read()

  # split markdown into array based on comments
  content=contents.replace("-->","<!--").split("<!--")  
  
  # handle conditionals  
  for i in range(len(content)-2, -1, -2):
    try:
      obj = json.loads(content[i])
      content[i]=obj
    except:
      obj=content[i]

    if isinstance(obj, dict):
      # entry is a dictionary, we need to process it
      # ============================= processing conditionals =============================
      if "condition" in obj:
        if "content" in obj:
          # condition is an inline condition
          if common.intersection(obj["condition"], conditionals):
            content[i]=obj["content"]
          else:
            content.pop(i)  
        else:  
          # the condition is a block condition
          id = obj["id"]
          content.pop(i)
          if common.intersection(obj["condition"], conditionals):
            # the condition is met.  Include the contents

            # scan to find the end of the condition
            offset=0
            while not common.dictionaryContains(content[i+offset],"endCondition",id):
              offset += 1
            content.pop(i+offset)
            
          else:
            # condition is not met.  Exclude contents  
            # scan to find the end of the condition
            while not common.dictionaryContains(content[i],"endCondition",id):
              content.pop(i) # remove everything until the closing of the conditional
            content.pop(i) #remove the closing conditional

      # other go here...

  htmlFile = markdown.markdown("".join(content))
  soup = BeautifulSoup(htmlFile, 'html5lib')
  sections = soup.find_all('h2')

  #Print the href attribute of each link
  closingTag=""
  html=[]
  sectionCounter=0
  tempFile=htmlFile
  for section in sections:
    #print("=================",section,"=================")
    sectionCounter += 1
    temp = tempFile.split(str(section))
    html.append(temp[0])
    html.append(f'{closingTag}<div class="section" id="section-{sectionCounter}">{str(section)}')
    closingTag = "</div>"
    tempFile=temp[1]

  html.append(tempFile)# add the last section or the whole chapter if no sections are present

  if len(closingTag)>0:
    # Chapter has at least one section, need to close it
    html.append(closingTag)
  
  # ============================= processing images =============================
  images = soup.find_all('img')
  changes=[]
  imageNumber=0
  for image in images:
    imageNumber+=1
    #print("=================",image["alt"],"=================")
    imageData=json.loads(image["alt"])
    if "caption" not in imageData:
      imageData["caption"] = True
    image["id"] = "image-" + imageData["id"]
    caption=image["title"].replace("{-img-}",str(imageNumber))

    image["title"] = caption
    image["alt"] = caption
    changes.append({"find":"{-img-" + imageData["id"] + "-}","replace":str(imageNumber)})

  # ============================= processing links =============================
  links = soup.find_all('a')
  for link in links:
    if link["href"].startswith("http"):
      # external link. Leave it alone
      pass
    elif link["href"].startswith("#"):
      # in-page link. Leave it alone
      pass
    else:
      # relative link. See if it needs to be processed
      
    
    print("=================",link["href"],"=================")
    


  # ============================= adjust the DOM ============================= 
    if image.parent.name=="p":
      image.parent["style"]="text-align:center"

    if imageData["caption"] == True:
      div = soup.new_tag("div")
      div.append(caption)
      div["style"]="text-align:center"
      image.insert_after(div)
    
  htmlText=soup.prettify()

  # we're done with the dom, now processing as a text file

  for change in changes:
   #print("replacing",change['find'],"with",change["replace"])
    htmlText = htmlText.replace(change['find'] , change["replace"])

  htmlText = htmlText.replace("{-chp-}",outChapter)
  # htmlText = htmlText.replace("{-img-1-}","1")

  f = open(htmlPath, "w", encoding='utf-8')
  f.write(htmlText)
  f.close()        

def main(): 
  global toolPath
  global bloggerPath
  global settings
  args=sys.argv
  path=__file__.split(os.path.sep)
  toolPath = os.path.sep.join(path[:-1])
  bloggerPath = os.path.join(os.path.sep.join(path[:-2]),"blogger")
  workingPath = os.getcwd()
  toolPath = path
  
 #print("workingPath",workingPath)
 #print("bloggerPath",bloggerPath)
 #print("toolPath",toolPath)
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


  #we are in a book's source directory
  args.pop(0) # remove the script name
  if len(args)==0:
    # no arguments specified.  read them from build
    version=settings["build"]["version"]
    if "chapters" in settings["build"]:
      chapters=settings["build"]["chapters"]
    else:
      chapters=[]  
  elif len(args)==1:
    # one argument passed.  Assume it is a version name
    version=args[0]
    chapters=[]
  else:
    # assume we have both a version and one or more chapters
    version=args.pop(0)
    chapters=args
 #print(version, chapters) 

  #Now we have version and chapters specified

  # if chapters not specified, build all chapters in version
  if len(chapters) == 0:
    for chap in settings["versions"][version]["chapters"]:
      chapters.append(chap)

  # iterate over chapters and build html
  for chapter in chapters:
   #print (chapter)
    processOneFile(chapter,version)



if __name__=="__main__":
    main()