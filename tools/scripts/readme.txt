scripts are pre-configured publishing routines.  To make a script, send "save" as the last argument and the script name as the second arguemnt:

PS F:\code\availabooks\book1002\2000\01> python f:/code/availabooks/tools/publish.py system.js chapter1.md save currentsystem

This will run the script and save the parameters for future use, including intermediate steps, such as getting post ids.  Updating from a script will be faster than running with regular parameters specified
