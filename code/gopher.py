import os, sys, argparse
import pandas as pd
from urllib.request import urlopen, urlretrieve
from urllib.error import URLError

###########################################################################
#
# General Functions
#
###########################################################################
def parseArgs(platform, pc):
  prog = 'Gopher: Planetary Orbital Radar Data Download Application'
  vers = '0.1'
  outDir = '~' + pc + 'Downloads' + pc
  instruments = ['sharad']
  products = {'sharad': ['edr', 'rdr', 'usrdr'],}
  parser = argparse.ArgumentParser(description=str(prog + ' ' + str(vers)))
  #
  # Input File
  #
  parser.add_argument('inputFile', type=str, nargs=1,
                      help=str("Input file containing list of desired observations"))
  #
  # Output directory
  #
  parser.add_argument('-o', '--output', type=str, nargs=1, default='outDir',
                      help=str("Destination to store the downloads"))
  #
  # Instrument Selection
  #
  parser.add_argument('-i', '--instrument', type=str, nargs=1, default=None,
                      help=str("Select intrument: {}".format(instruments)))
  #
  # Product Selection
  #
  parser.add_argument('-p', '--product', type=str, nargs=1, default=None,
                      help=str("Select products to download ['edr', 'rdr', 'usrdr']"))
  #
  # Update product dataframes
  #
  parser.add_argument('-u', '--update', action="store_true", default=False,
                      help=str("Update the PDS Data file"))
  #
  # Check the length of the command line inputs
  #
  if len(sys.argv[1:]) == 0:
    parser.print_help()
    parser.exit()
  else:
    #
    # Parse the args, yo!
    #
    args = parser.parse_args()
    #
    # Check if the intrument is in the list and pull out appropriate
    # products lists
    #
    if args.instrument[0].lower() in instruments:
      instrument = args.instrument[0].lower()
      products = products[instrument]
    else:
      print('Instrument {} not understood or currently supported'.format(args.instrument[0].lower()))
      parser.print_help()
      parser.exit()
    #
    # Now check the products
    #
    if args.product[0].lower() in products:
      product = args.product[0].lower()
    else:
      print('Product {} not understood or currently supported'.format(args.product[0].lower()))
      parser.print_help()
      parser.exit()
    #
    # Check if input file exits
    #
    iFile = str(args.inputFile[0])
    if os.path.isfile(iFile):
      print("""The file {} was found! Continuing to process request.""".format(iFile))
      #
      # Read file lines into a list of strings
      #
      with open(iFile) as f:
        content = f.readlines()
        observations = [x.strip() for x in content]
        #
        # Check if there are leading zeros
        #
        if observations[0][0] != 0:
          observations = toPDSName(observations)
          #
          # Check if output directory exists
          #
          outDir = str(args.output[0])
          if os.path.isdir(outDir):
            if outDir[-1] != '/':
              outDir += '/'
          else:
            print('WARNING: New directory {} will be created...'.format(outDir))
            os.mkdir(outDir)
          return observations, instrument, product, outDir, args.update
    else:
      print("""The file {} was not found. Please check your file path
             and try again.""".format(iFile))
      parser.print_help()
      parser.exit()
      return

def testConnection(timeout=60):
  """ This function will test to ensure the user has a valid internet connection """
  try:
    response=urlopen('http://www.google.com',timeout=timeout)
    return True
  except URLError as err:
    print("You do not appear to have a valid internet connection")
    print("How do you expect to download files...?")
    return False

def updateTables(outDir='../bin/'):
  #
  # Set column headers for each type
  #
  EDRnames = ['VOLUME_ID',
              'RELEASE_ID',
              'FILE_SPECIFICATION_NAME',
              'PRODUCT_ID',
              'PRODUCT_CREATION_TIME',
              'PRODUCT_VERSION_ID',
              'PRODUCT_VERSION_TYPE',
              'PRODUCT_TYPE',
              'MISSION_PHASE_NAME',
              'ORBIT_NUMBER',
              'START_TIME',
              'STOP_TIME',
              'SPACECRAFT_CLOCK_START_COUNT',
              'SPACECRAFT_CLOCK_STOP_COUNT',
              'MRO:START_SUB_SPACECRAFT_LATITUDE',
              'MRO:STOP_SUB_SPACECRAFT_LATITUDE',
              'MRO:START_SUB_SPACECRAFT_LONGITUDE',
              'MRO:STOP_SUB_SPACECRAFT_LONGITUDE',
              'INSTRUMENT_MODE_ID',
              'DATA_QUALITY_ID']
  RDRnames = EDRnames
  FPBnames = [EDRnames[0],
              EDRnames[2],
              EDRnames[3],
              EDRnames[5],
              EDRnames[4],
              EDRnames[9],
              EDRnames[10],
              EDRnames[11],
              EDRnames[14],
              EDRnames[15],
              EDRnames[16],
              EDRnames[17]]
  BaseURL = 'https://pds-geosciences.wustl.edu/mro/mro-m-sharad-{}-{}-v1/{}'
  arc = [3,4,5]
  ty = ['edr', 'rdr', 'radargram']
  files = ['mrosh_0004/index/cumindex.tab',
           'mrosh_1004/index/cumindex.tab',
           'mrosh_2001/index/index.tab']
  for _t, _type in enumerate(ty):
    url = BaseURL.format(arc[_t],ty[_t],files[_t])
    tmp = urlretrieve(url)
    if _type == 'edr':
      print('Updating EDR index information...')
      edr = pd.read_csv(tmp[0], names=EDRnames, header=None, engine='python')
      edr['Type'] = 'EDR'
      edr.to_pickle(outDir + 'edr.pkl')
    elif _type == 'rdr':
      print('Updating RDR index information...')
      rdr = pd.read_csv(tmp[0], names=RDRnames, header=None, engine='python')
      rdr['Type'] = 'RDR'
      rdr.to_pickle(outDir + 'rdr.pkl')
    elif _type == 'radargram':
      print('Updating radargram index information...')
      radargram = pd.read_csv(tmp[0], names=FPBnames, header=None, engine='python')
      radargram['Type'] = 'RADARGRAM'
      radargram.to_pickle(outDir + 'radargram.pkl')
    os.remove(tmp[0])
  return

def toPDSName(obsList):
  newObsList = []
  for obs in obsList:
    #
    # Remove trailing zeros; in all cases these are the last 3 characters
    #
    newObsList.append(obs)
  return newObsList

def downloadFiles(urls, outDir):
  for url in urls:
    fName = outDir + url.split('/')[-1]
    print('Downloading {}...'.format(url.split('/')[-1]))
    try:
      tmp = urlretrieve(url, fName)
    except URLError as err:
      print('Error downloading {}...'.format(url.split('/')[-1]))
      print('\t{}'.format(err.reason))
      exit()
  return

def loadDF(inst, prod):
  if inst == 'sharad':
    if prod == 'edr':
      urlBase = 'https://pds-geosciences.wustl.edu/mro/mro-m-sharad-3-edr-v1/'
      df = pd.read_pickle('../bin/edr.pkl')
    elif prod == 'rdr':
      urlBase = 'https://pds-geosciences.wustl.edu/mro/mro-m-sharad-4-rdr-v1/'
      df = pd.read_pickle('../bin/rdr.pkl')
    elif prod == 'usrdr':
      urlBase = 'https://pds-geosciences.wustl.edu/mro/mro-m-sharad-5-radargram-v1/'
      df = pd.read_pickle('../bin/radargram.pkl')
  return urlBase, df

def gatherURLs(requestObs, inst, prod, urlBase, df):
  urls = []
  for _file in requestObs:
      df2 = df[df['FILE_SPECIFICATION_NAME'].str.contains(str(_file))==True]
      for ind in df2.index:
        tmp = urlBase + df2['VOLUME_ID'][ind]
        tmp += '/' + df2['FILE_SPECIFICATION_NAME'][ind].strip()
        urls.append(tmp)
        if inst == 'sharad':
          if prod =='edr':
            urls.append(tmp[:-4] + '_A.DAT')
            urls.append(tmp[:-4] + '_S.DAT')
          elif prod == 'rdr':
            urls.append(tmp[:-4] + '.DAT')
          elif prod == 'usrdr':
            if 'RGRAM' in tmp:
              urls.append(tmp[:-4] + '.IMG')
            if 'GEOM' in tmp:
              urls.append(tmp[:-4] + '.TAB')
  return urls

#
# Gopher function
#
def gopher(inputfile, instrument, product, outDir=False, update=False):
  prog = 'Gopher: Planetary Orbital Radar Data Download Application'
  vers = '0.1'
  platform = sys.platform
  linuxUnix = ['linux', 'unix', 'darwin']
  windows = ['win32', 'cygwin']
  if platform in linuxUnix:
    pc = '/'
  if platform in windows:
    pc="\\\\"
  if outDir == False:
    outDir = '~' + pc + 'Downloads' + pc
  if os.path.isdir(outDir):
    if outDir[-1] != pc:
      outDir += pc
  else:
    print('WARNING: New directory {} will be created...'.format(outDir))
    os.mkdir(outDir)
  #
  # Open Log file
  #
  _log = open(outDir + 'gopher.log', 'w')
  _log.write('----------' + prog + ' ' + vers + '----------\n')
  #
  # Check if input file is available and readable
  #
  if os.path.isfile(inputfile):
    if os.access(inputfile, os.R_OK):
      _log.write("The file {} was found! Continuing to process request.\n".format(inputfile))
      #
      # Read file lines into a list of strings
      #
      with open(inputfile) as f:
        content = f.readlines()
        observations = [x.strip() for x in content]
        #
        # Check if there are leading zeros
        #
        if observations[0][0] != 0:
          observations = toPDSName(observations)
  #
  # Available Instruments
  #
  instruments = ['sharad']
  products = {'sharad': ['edr', 'rdr', 'usrdr'],}
  if instrument.lower() in instruments:
    instrument = instrument.lower()
    products = products[instrument]
  else:
    print('Instrument {} not understood or currently supported\n'.format(args.instrument[0].lower()))
    return
  if product.lower() in products:
    product = product.lower()
  _log.write('Retrieving {} {} products specified in {}\n'.format(instrument, product, inputfile))
  if testConnection():
    if update:
      _log.write('Updating database tables, this could take some time...\n')
      updateTables()
  urlBase, df = loadDF(instrument, product)
  #
  # Gather URLs needed for downloading
  #
  urls = gatherURLs(observations, instrument, product, urlBase, df)
  if testConnection():
    #
    # Download
    #
    downloadFiles(urls, outDir)
  else:
    print('You appear not to be connected to the interwebs...')
    print('Please check you connection and try again')
    return

  return


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
  global platform, pc
  platform = sys.platform
  linuxUnix = ['linux', 'unix', 'darwin']
  windows = ['win32', 'cygwin']
  if platform in linuxUnix:
    pc = '/'
  if platform in windows:
    pc="\\\\"
  requestObs, instrument, product, outDir, update = parseArgs(platform, pc)
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
