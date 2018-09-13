from shaddai_class import *
from datetime import datetime
import argparse
import sys
import pandas as pd
from os.path import isfile, isdir, basename
from os import mkdir
from urllib.error import URLError
from urllib.request import urlopen

def parseArgs():
  prog = 'SHADDAI'
  vers = '0.1'
  parser = argparse.ArgumentParser(description=str(prog + ' ' + str(vers)))
  parser.add_argument('inputFile', type=str, nargs=1,
                      help=str("Input file containing list of desired observations"))  
  parser.add_argument('-u', '--update', action="store_true", default=False,
                      help=str("Update the PDS Data file"))
  if len(sys.argv[1:]) == 0:
    parser.print_help()
    parser.exit()
  args = parser.parse_args()
  iFile = str(args.inputFile[0])
  update = args.update
  #
  # Check to make sure file exists
  #
  if isfile(iFile):
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
      return observations, update
  else:
    print("""The file {} was not found. Please check your file path
             and try again.""".format(iFile))
    parser.print_help()
    parser.exit()


def testConnection(timeout=60):
  """ This function will test to ensure the user has a valid internet connection """
  try:
    response=urlopen('http://www.google.com',timeout=timeout)
    return True
  except URLError as err: 
    print("You do not appear to have a valid internet connection")
    print("How do you expect to download files...?")
    return False

def getFileList(html):
  MainParser = ParseMainArchive()
  SubParser = ParseSubArchive() 
  html_page = urlopen(html)
  #
  # Feed the content to parser
  #
  try:
    MainParser.feed(str(html_page.read()))
  except URLError as err:
    print("The requested URL does not work or exist")
    print(err)
    quit()
  html_page.close()
  URLs = []
  for _subDir in MainParser.lsData:
    if _subDir[-9:-7] == 's_':
      try:
        html_page = urlopen(html + _subDir[-9:])
      except:
        print(html + _subDir[-9:])
        quit()
      SubParser.feed(str(html_page.read()))
      URLs.append(SubParser.lsData)
  return URLs[-1]

def makeDataFrame(URLs):
  #
  # Initialize empty dataframe
  #
  html = 'http://pds-geosciences.wustl.edu'
  data = {'Obs': [],
          'RGRAM_URL': [],
          'RGRAM_LBL': [],
          'GEOM_URL': [],
          'GEOM_LBL': []}
  for url in URLs:
    data['Obs'].append(url.split('/')[-1].split('_')[1])
    data['RGRAM_URL'].append(url)
    data['RGRAM_LBL'].append(url[:-3] + 'lbl')
    tmp = url.split('/')
    tmp[5] = 'geom'
    tmp2 = tmp[-1]
    tmp[-1] = tmp2.split('_')[0] + '_' + tmp2.split('_')[1] + '_' + 'geom.tab'
    geom = "/".join(tmp)
    data['GEOM_URL'].append(geom)
    data['GEOM_LBL'].append(geom[:-3] + 'lbl')
  PDSFileList = pd.DataFrame(data)
  PDSFileList.to_pickle('../input/PDSFileList.pkl')
  return PDSFileList

def downloadFiles(_file, df, rgrams=True, rgramLBL=False, geoms=True, geomLBL=False):
  if not isdir('../output'):
    mkdir('../output')
  todayDate = datetime.today().strftime('%Y%m%d')
  outDir = '../output/' + todayDate
  rgramOutDir = outDir + '/rgram'
  geomOutDir = outDir + '/geom'
  if not isdir(outDir):
    mkdir(outDir)
  #
  # Select those file we wish to download
  #
  tmp = ['RGRAM_URL', 'RGRAM_LBL', 'GEOM_URL', 'GEOM_LBL']
  idx = []
  if rgrams:
    idx.append(int(0))
    if not isdir(rgramOutDir):
      mkdir(rgramOutDir)
  if rgramLBL:
    idx.append(int(1))
    if not isdir(rgramOutDir):
      mkdir(rgramOutDir)
  if geoms:
    idx.append(int(2))
    if not isdir(geomOutDir):
      mkdir(geomOutDir)
  if geomLBL:
    idx.append(int(3))
    if not isdir(geomOutDir):
      mkdir(geomOutDir)
  dlList = [tmp[_i] for _i in idx]
  #
  # Begin download protocol
  #
  html = 'http://pds-geosciences.wustl.edu' 
  row = df.loc[df['Obs'] == _file] 
  if row.empty:
    print('Observation {} not available on the PDS'.format(_file))
  else:
    for item in row:
      if item == 'Obs':
        continue
      elif item in dlList:
        url = html + row[item].values[0]
        u = urlopen(url)
        if u.status == 200:
          file_name = row[item].values[0].split('/')[-1]
          if item[:3] == 'RGR':
            outFile = rgramOutDir + '/' + file_name
          elif item[:3] == 'GEO':
            outFile = geomOutDir + '/' + file_name
          f = open(outFile, 'wb')
          file_size = int(u.getheader("Content-Length"))
          print("Downloading: {} Bytes: {}".format(file_name, str(file_size)))
          file_size_dl = 0
          block_sz = 8192
          while True:
            buffer = u.read(block_sz)
            if not buffer:
              break
            file_size_dl += len(buffer)
            f.write(buffer)
            status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100 / file_size)
            status = status + chr(8)*(len(status)+1)
            print(status, end="\r")
          f.close()
        else:
          print('File {} not found on the PDS website at {}'.format(file_name, url))
  return

def toPDSName(obsList):
  newObsList = []
  for obs in obsList:
    #
    # Remove trailin zeros; in all cases these are the last 3 characters
    #
    newObsList.append(obs[:-3].zfill(8)) 
  return newObsList
