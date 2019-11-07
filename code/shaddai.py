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
  requestObs, update, products, labels, verbose = parseArgs()
  if testConnection():
    if update:
      if products.upper() != 'EDR':  
        html = 'http://pds-geosciences.wustl.edu/mro/mro-m-sharad-5-radargram-v1/mrosh_2001/data/rgram/'
        rgramURLs = getFileList(html) 
        PDSFileDF = makeDataFrame(rgramURLs)
      else:
        html = 'http://pds-geosciences.wustl.edu/mro/mro-m-sharad-3-edr-v1/'
    else:
      PDSFileDF = pd.read_pickle('../input/PDSFileList.pkl')
      rgrams = geoms = tiffs = False
      rgramLBL = geomLBL = tiffLBL = False
      if products == 'all': 
        rgrams = geoms = tiffs = True
        if labels == True:
          rgramLBL = geomLBL = tiffLBL = True
      elif products == 'rgram':
        rgrams = True
        if labels == True:
          rgramLBL = True
      elif products == 'geom':
        geoms = True
        if labels == True:
          geomLBL = True
      elif products == 'tiff':
        tiffs = True
        if labels == True:
          tiffLBL = True
      else:
        print('ERROR: Unknown error')
        exit()
      for _file in requestObs:
        downloadFiles(_file, PDSFileDF, rgrams=rgrams, rgramLBL=rgramLBL, geoms=geoms, geomLBL=geomLBL, tiffs=tiffs, tiffLBL=tiffLBL, verbose=verbose)
  else:
    quit() 
  return

if __name__ == '__main__':
  main()
    
