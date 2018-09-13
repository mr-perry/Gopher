from shaddai_func import *
from shaddai_class import *
import argparse
import sys
from os.path import isfile
from urllib.request import urlopen

def main():
  """ 
      SHARAD Data Download Application (SHADDAI)

      This Python script provides users with a tool to conduct bulk downloads
      from the Mars Reconnaissance Orbiter Shallow Radar (SHARAD) experiment
      data within the PDS.

      Input - Text file containing a list of observation IDs (e.g. ...)
      Output - Requested files

      Written by: Matthew R. Perry
      Last Updated: 12 September 2018
  """
  requestObs, update = parseArgs()
  if testConnection():
    if update:
      html = 'http://pds-geosciences.wustl.edu/mro/mro-m-sharad-5-radargram-v1/mrosh_2001/data/rgram/'
      rgramURLs = getFileList(html) 
      PDSFileDF = makeDataFrame(rgramURLs)
    else:
      PDSFileDF = pd.read_pickle('../input/PDSFileList.pkl')
      for _file in requestObs:
        downloadFiles(_file, PDSFileDF)
  else:
    quit() 
  return

if __name__ == '__main__':
  main()
    
