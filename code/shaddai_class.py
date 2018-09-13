from html.parser import HTMLParser
import urllib.request as urllib2
from os.path import basename

class ParseMainArchive(HTMLParser):
  #
  # Initializing lists
  #
  lsData = list()
  #
  # HTML Parser Methods
  #
  def handle_starttag(self, tag, attrs):
    #
    # Only parse the 'anchor' tag associated with data products
    #
    if tag == 'a':
      #
      # Check the list of defined attributes
      #
      for name, value in attrs:
        if name == "href":
          self.lsData.append(value)

class ParseSubArchive(HTMLParser):
  #
  # Initialize lists
  #
  lsData = list()
  #
  # HTML Parser Methods
  #
  def handle_starttag(self, tag, attrs):
    if tag == 'a':
      #
      # Check the list of defined attributes
      #
      for name, value in attrs:
        if name == "href" and value[-4:] == '.img':
          self.lsData.append(value)

