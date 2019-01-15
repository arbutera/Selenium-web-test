import os
import sys
import logging
import re
import time
import csv
import pprint

from optparse import OptionParser
from selenium import webdriver

def runTests(test_cases, drivers, user, wait):
  pwd = os.getcwd()

  # mapping of driver name to driver's options class
  optsDict = {
    "chrome": webdriver.chrome.options.Options(),
    "ie": webdriver.ie.options.Options()
    # there is opportunity to add more driver option classes
  }

  # mapping of driver name to driver's class
  driversDict = {
    "chrome": webdriver.Chrome,
    "ie": webdriver.Ie,
    "edge": webdriver.Edge
    # there is opportunity to add more drivers to this dictionary
  }

  # mapping of driver name to location of driver binary
  # binaries are bundled in repo, please add more if needed
  pathsDict = {
    # make sure you have correct binaries downloaded per OS
    "chrome": pwd + r'\chromedriver.exe',
    "ie": pwd + r'\iedriver.exe',
    "edge": pwd + r'\MicrosoftWebDriver.exe'
  }

  # create a results list to append the results of each test case to so we can later export as csv
  results = []
  # for each driver type that the user specified, run all test cases
  for d in drivers:

    # prep URL to login with user credentials via paramater to sign onto OHD once before looping through pages
    loginURL = 'https://d-csc.sys.cigna.com/online/home.asp?EIDPIN=' + user
    print('starting driver %s' % d)
    if d != "edge":
      driverOpts = optsDict[d]
      if d == "chrome":
        driverOpts.add_argument("--headless") 
        driver = driversDict[d](executable_path=pathsDict[d],
                          options=driverOpts)
                        #   service_args=['--verbose', '--log-path=C:/Windows/Logs/DISM/%sdriver.log' % d]) - ALSO THROWING BUGS
        print("logging in via %s" % (loginURL,))
        driver.get(loginURL) # trigger browser to use login url before starting site testing loop
        time.sleep(2) # give the page a couple seconds to render
    else:
      driver = webdriver.Edge(executable_path=pathsDict[d])
      driver.get("https://d-csc.sys.cigna.com/online/Login/")
      time.sleep(3)
      search_box = driver.find_element_by_name('displayEIDPIN')
      search_box.send_keys(user)
      search_box.submit()
      time.sleep(3)

    for idx, testURL in enumerate(test_cases):
      testURL = re.sub(r'.*WebRoot/', 'https://d-csc.sys.cigna.com/', testURL) # replace substring in user input path before 'WebRoot' to convert server path to web url.
      logger.warning("Running test case %s (%s out of %s)" % (testURL, idx+1, len(test_cases))) 
      driver.get(testURL)
 
       # if timeDelay option was set, pause page for specified number of seconds
      if wait > 0:
      	print("waiting for specified time: %s" % (wait,))
      	time.sleep(wait)

      # for all the possible logs for this driver (browser, client, etc), loop through logs 
      for logType in driver.log_types:
      
        print(logType) #logging.info here
        for log in driver.get_log(logType):

          logURL = testURL
          logDriver = d
          logMessageRaw = log['message']
          logMessageParse = logMessageRaw.replace(logURL, "")
          logMessage = logMessageRaw.replace(logURL, "[Page]")
          logLevel = log['level']
          logSource = log['source']
          if logURL in logMessageRaw:
            errorlocation = '[PAGE]'
            parsedError = re.search(r'[^\d+]+(?=[^:\d])\w+', logMessageParse).group().strip() #parse log message and remove line number for page level errors to allow for easier grouping during analysis of csv data
          else:
            errorlocation = re.search(r'(?P<url>https?://[^\s]+)',logMessageRaw).group("url") # parse out url of affected file from console log
            parsedError = logMessage

          result = [logURL, logDriver, logLevel, logMessageRaw, parsedError, logSource, errorlocation]
          results.append(result)   # append new row to the list of all test results

    driver.quit()

  return results

def getDirContents(dir, ignore=[]):
    contents = []

    # get a list of the full directory path for each file and subdirectory in dir
    for subdir, _, files in os.walk(dir):
        for file in files:
            a = True
            path = subdir + os.sep + file
            path = path.replace('\\',"/") # hard code of back slash 
            print(path)
            if len(ignore) > 0:
              for i in ignore:
                if i in path.lower():
                  a = False
                  break
            if a:
              if file.endswith('.asp'):
                contents.append(path)

    return contents

def isValidArgs():

  drivers = ["chrome", "ie", "edge"]
  global options

  if not options.directory:
    return False
  else:
    # specify server directory and drive path
    serverDir = '//ciwiis0d0013/Pages/SYS/CSC/WebRoot/online/'
    serverDir += options.directory 
  if not options.user:
    return False

  if not os.path.isdir(serverDir):
    return False
  else:
    serverDir = os.path.abspath(serverDir)

  # convert comma separated list to python list
  options.drivers = [driver.strip().lower() for driver in options.drivers.split(",")]

  if len(options.drivers) < 1:
    return False

  for driver in options.drivers:
    if driver not in drivers:
      return False

  # parameter which allows webtest to ignore certain files within a selected directory
  options.ignore = [opt.strip().lower() for opt in options.ignore.split(",")]
  options.ignore = [i for i in options.ignore if i != ""]

  return True

def setLogger():
    logging.basicConfig(format='%(asctime)s %(message)s')
    logger = logging.getLogger(__name__)

    return logger

if __name__ == "__main__":
    logger = setLogger()

    parser = OptionParser()
    parser.add_option("-d", "--directory", dest="directory",
                    help="Parent directory containing webpages to test [REQUIRED]", metavar="DIRECTORY")
    parser.add_option("-w", "--web-drivers", dest="drivers", default="chrome",
                    help="Comma seperated list of webdrivers to use for testing (supports chrome, ie, edge) [REQUIRED]", metavar="DRIVERS")
    parser.add_option("-u", "--user", dest="user", default="",
                help="User ID number to authenicate via URL parameter [REQUIRED]", metavar="DRIVERS")
    parser.add_option("-i", "--ignore", dest="ignore", default="",
                help="Comma seperated list of directories to ignore [OPTIONAL]", metavar="DRIVERS")
    parser.add_option("-t", "--timeDelay", dest="delay", default="0", type="float", 
                help="Delay on page load for each tested page [OPTIONAL]", metavar="WAIT")

    (options, args) = parser.parse_args()

    if not isValidArgs():
      parser.print_help()
      sys.exit(1)
    serverDir = '//ciwiis0d0013/Pages/SYS/CSC/WebRoot/online/'
    serverDir += options.directory
    test_cases = getDirContents(dir=serverDir, ignore=options.ignore)
    #print(test_cases) - FOR TESTING PURPOSES
    #sys.exit() - FOR TESTING PURPOSES

    results = runTests(test_cases=test_cases, drivers=options.drivers, user=options.user, wait=options.delay)
   

    header = ["URL", "Web_Driver", "Log_Level", "Log_Msg_Detail", "Log_Msg", "Log_Source", "Affected_File"]
    with open('test_results_%s.csv' % int(time.time()), 'w', newline='') as f:
      writer = csv.writer(f)
      writer.writerow(header)
      writer.writerows(results)
