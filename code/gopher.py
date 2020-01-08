from gopher_funcs import *
import pandas as pd
import os, sys, argparse
from urllib.request import urlopen, urlretrieve

def main():
  """ 
      Gopher: Planetary Orbital Radar Data Download Application

      This Python script provides users with a tool to conduct bulk downloads
      from various orbital radar systems data in the PDS or a PDS equivalent
      archive. 

      Instruments currently available:
        Mars Reconnaissance Orbiter Shallow Radar Experiment

      Instruments to be included:
        Mars Advanced Radar for Subsurface and Ionospheric Sounding
        Lunar Radar Sounder

      Input - Text file containing a list of observation IDs (e.g. ...)
      Output - Requested files

      Written by: Matthew R. Perry
      Last Updated: 13 November 2018
  """
  requestObs, instrument, product, outDir, update = parseArgs()
  if testConnection():
    if update:
      print('Updating database tables, this could take some time...')
      updateTables()
  urlBase, df = loadDF(instrument, product)
  #
  # Gather URLs needed for downloading
  #
  urls = gatherURLs(requestObs, instrument, product, urlBase, df)
  if testConnection():
    #
    # Download 
    #
    downloadFiles(urls, outDir)
  else:
    print('You appear not to be connected to the interwebs...')
    print('Please check you connection and try again')
    quit() 
  return

if __name__ == '__main__':
  main()
