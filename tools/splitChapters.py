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


def split_file_by_delimiter(file_path, delimiter):
    # Ensure the file exists
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    # Read the content of the file
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Split the content by the delimiter
    parts = content.split(delimiter)
    
    # Create a directory to store the split files
    base_dir = os.path.dirname(file_path)
    
    # Write each part to a new file
    for i, part in enumerate(parts):
        split_file_path = os.path.join(base_dir, f'{i}.md')
        with open(split_file_path, 'w', encoding='utf-8') as split_file:
            split_file.write(f"# Chapter {i}: "+"\n".join(part.split('\n')[1:]))
    
    print(f"File has been split into {len(parts)} parts and saved")



def main():
  split_file_by_delimiter('full.md', "\nCHAPTER ")
                          

if __name__=="__main__":
    main()