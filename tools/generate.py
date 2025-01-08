#this script transcodes original work (usually markdown) into the various HTML files that will be hosted on blogger

import copy
import re
import json
import sys
import os
import markdown
from bs4 import BeautifulSoup
from pathlib import Path


import common # local file

#globals
bloggerPath = "" #where the blogger files start in the local file system
sourcePath = "" #where the SOURCE files start in the local file system
workingPath = "" #where the source files are
toolPath = '' # this is the path used for config.json
settings={} # to hold settings for the book

def processOneFile(chapter, version):
  # currently assuming all source files are markdown
  print ("==================version:",version,"  chapter:",chapter,"=================")
 #print ("======",settings["versions"][version])
  global sourcePath
  if "out" in settings["versions"][version]["chapters"][str(chapter)]:
    outChapter=str(settings["versions"][version]["chapters"][str(chapter)]["out"])    
  else:
    outChapter=str(chapter)

  fileName = outChapter + ".md"
  if "condition" in settings["versions"][version]:
    conditionals = settings["versions"][version]["condition"]
  else:
      conditionals="only"
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
  
  changes=[] ## used to make a list of text changes that need to be made
  
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
          #print("found a  dictionary",obj)
          id = obj["id"]
          content.pop(i)
          #print("checkiong condition",obj["condition"], conditionals)
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
      elif "id" in obj:
        content[i]=f"~id:{obj['id']}~"


      # others go here...


  # ============================= processing the html =============================      
  htmlFile = markdown.markdown("".join(content))
  soup = BeautifulSoup(htmlFile, 'html5lib')
  
  closingTag=""
  html=[]
  #comment = soup.find("h1").get_text()
  tempFile=htmlFile
  sectionCounter=0
  for section in soup.find_all('h2'):
    #print("=================",section,"=================")
    sectionCounter += 1
    temp = tempFile.split(str(section))
    html.append(temp[0])
    # if(sectionCounter==1):
      # html.append(f"<!--{settings['chapterLabel']} {outChapter}-->")
    html.append(f'{closingTag}<div class="chapter-section" id="section-{sectionCounter}">{str(section)}')
    closingTag = "</div>"
    tempFile=temp[1]

  html.append(tempFile)# add the last section or the whole chapter if no sections are present

  if len(closingTag)>0:
    # Chapter has at least one section, need to close it
    html.append(closingTag)
  
  
  soup = BeautifulSoup("".join(html), 'html5lib')
  
  # ============================= processing images =============================
  images = soup.find_all('img')
  imageNumber=0
  for image in images:
    imageNumber+=1
    #print("=================",image["alt"],"=================")
    imageData=json.loads(image["alt"])
    #print (imageData)
    if "caption" not in imageData:
      imageData["caption"] = True
    image["id"] = "image-" + imageData["id"]
    caption=image["title"].replace("{-img-}",str(imageNumber))

    image["title"] = caption
    image["alt"] = caption
    changes.append({"find":"{-img-" + imageData["id"] + "-}","replace":str(imageNumber)})
    # ============================= adjust the DOM for images============================= 
    if image.parent.name=="p":
      image.parent["style"]="text-align:center"

    if imageData["caption"] == True:
      div = soup.new_tag("div")
      div.append(caption)
      div["style"]="text-align:center"
      image.insert_after(div)

  # ============================= processing links =============================
  # print("settings",settings['versions'])


  links = soup.find_all('a')
  for link in links:
    print("=================",link["href"],"=================")
    if link["href"].startswith("http"):
      # external link. Leave it alone
      pass
    elif link["href"].startswith("#"):
      # in-page link. convert to span with onclick to show part
      id=link["href"][1:]
      print("id",id)

      span = soup.new_tag("span")
      span['onclick'] = f'scroll_to("{id}")'
      span["class"]="span-link"
      span.append("".join(link.decode_contents().split("\n")))
      link.replace_with(span)
      


      pass
    else:
      # relative link. See if it needs to be processed
      components=link["href"].split("/")
      componentCount = len(components)
      lastEntry = components[componentCount-1]
      lastArray = lastEntry.split(".md")
      lastEntry = lastArray[0]
      # print("lastArray",lastArray)


      if len(components) == 1:
        # different chapter, same book
        # print("link to a chapter in the same book")
        match = find_first_match(r'\[([^\]]+)\]',lastEntry)
        # print ("match",match)
        if not match is None:
          #we have a square bracket in the link file name.  It is a chapter link and needs to be converted from a source value to a the output value
          outChap = match
          if "out" in settings["versions"][version]["chapters"][str(match)]:
            outChap=str(settings["versions"][version]["chapters"][str(match)]["out"])
          # print ("version",version)
          # print ("chapter",settings["versions"][version]["chapters"][str(match)])
          lastArray[0] = outChap
          
        link["href"]=".html".join(lastArray)

      elif len(components) == 2:
        # link includes a version, assume is is a version in the same book, chapter may or may not be same
        # print("link to a chapter in a different version of the same book")
        thisVersion = components[0]
        components[0] = f"{settings['versions'][components[0]]['year']}/{settings['versions'][components[0]]['month']:02}"
        #print ("components",components)  

        match = find_first_match(r'\[([^\]]+)\]',lastEntry)
        # print ("match",match)

        if not match is None:
          #we have a square bracket in the link file name.  It is a chapter link and needs to be converted from a source value to a the output value
          outChap = match
          if "out" in settings["versions"][thisVersion]["chapters"][str(match)]:
            outChap=str(settings["versions"][thisVersion]["chapters"][str(match)]["out"])
          lastArray[0] = outChap

        components[1] = ".html".join(lastArray)

        link["href"]="/" + "/".join(components)

      elif len(components) == 3:
        #link includes a book number, assume it is a link to a chapter in another book
        # print("link to a chapter in the chapter in another book")
        # print ("components",components) 
        components[1]=components[1].replace("{-ver-}",version)
        # print ("components",components) 

        #look to see if the path first component is a book number.  If so, load the book settings
        match = find_first_match(r'\[([^\]]+)\]',components[0])
        # print ("match",match)

        bookSettings = copy.deepcopy(settings)

        if not match is None:
          # open the settings for the book
          with open(os.path.join(sourcePath,match,"settings.json") , "r") as f:
            bookSettings = json.load(f)

        # if target book is on the same blog, make it a relative link, otherwise build an absolute  
        if bookSettings['versions'][components[1]]['blog'] == settings['versions'][version]['blog']:
          components[0]=""
        else:
          components[0]=f"https://{bookSettings['versions'][components[1]]['blog']}.blogspot.com"


        # set the year and month for the link
        components[1]=f"{bookSettings['versions'][components[1]]['year']}/{bookSettings['versions'][components[1]]['month']:02}"

        # now adjust the last part of the link
        match = find_first_match(r'\[([^\]]+)\]',lastEntry)
        # print ("match",match)

        if not match is None:
          #we have a square bracket in the link file name.  It is a chapter link and needs to be converted from a source value to a the output value
          outChap = match
          #print(thisVersion,str(match))
          #print(bookSettings["versions"]["leech"])
          if "out" in bookSettings["versions"][thisVersion]["chapters"][str(match)]:
            outChap=str(bookSettings["versions"][thisVersion]["chapters"][str(match)]["out"])

        lastArray[0] = outChap
        components[2] = ".html".join(lastArray)


        link["href"]="/".join(components)


      else:
        # not a recognized format
        print("not a recognized format",link["href"])      

    
    


    


  # ============================= processing paragraph ids =============================
  elems = soup.find_all('p')
  for elem in elems:
    if elem.get_text().startswith('~id:'):
      contents = elem.contents
      p = soup.new_tag("p")
      data=contents[0].split("~")
      p["id"] = data[1].split(":")[1].split("~")[0]

      contents[0].replace_with(data[2])
      p.extend(contents)
      elem.replace_with(p)

  # remove the first H1 tag as it is the title of the chapter and will be placed in the blogger title 
  h1=soup.find("h1")
  title=h1.get_text()
  h1.string=f"{settings['chapterLabel']} {outChapter}: {title}"

  htmlText=soup.prettify()
  # we're done with the dom, now processing as a text file
  # print("changes",changes)
  for change in changes:
   #print("replacing",change['find'],"with",change["replace"])
    htmlText = htmlText.replace(change['find'] , change["replace"])

  htmlText = htmlText.replace("{-chp-}",outChapter)
  # htmlText = htmlText.replace("{-img-1-}","1")

  f = open(htmlPath, "w", encoding='utf-8')
  f.write(htmlText)
  f.close()    


def find_first_match(pattern, text):
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    return None


def main(): 
  global toolPath
  global bloggerPath
  global sourcePath
  global settings
  args=sys.argv
  path=__file__.split(os.path.sep)
  toolPath = os.path.sep.join(path[:-1])
  bloggerPath = os.path.join(os.path.sep.join(path[:-2]),"blogger")
  sourcePath = os.path.join(os.path.sep.join(path[:-2]),"source")
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