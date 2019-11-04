import os, sys

bspath = os.path.join(os.path.dirname(os.path.abspath(__file__)),"libraries/backports.functools_lru_cache-1.6.1")
sys.path.append(bspath)
bspath = os.path.join(os.path.dirname(os.path.abspath(__file__)),"libraries/beautifulsoup4-4.8.0")
sys.path.append(bspath)
bspath = os.path.join(os.path.dirname(os.path.abspath(__file__)),"libraries/soupsieve-1.9.5")
sys.path.append(bspath)

import backports.functools_lru_cache
import bs4
import soupsieve
import json
import codecs
import json

from  bs4 import BeautifulSoup
import requests

# config read

mode = "people"

with open(sys.argv[1]) as json_data_file:
    config = json.load(json_data_file)



# Webpage connection
# html = "https://www.csd.uoc.gr/CSD/index.jsp?content=time_schedule&lang=gr"
html = config['urls'][0]
outputFile = config['output']
r=requests.get(html)
c=r.content.decode('utf-8').replace("&nbsp;", " NULL ").replace("\\u00A0", #
                       " ").replace(u"\u0391", "A").replace(u"\u0397", "H").replace("<br />", " ").replace("<br/>", " ").encode('utf-8')
soup=BeautifulSoup(c,"html.parser")
retdata = []

# todo all lines should call another function that try catches and returns
# fail value

if mode == "people":
  prefix = 'http://www.csd.uoc.gr/CSD/'
  elements = soup.find_all('div', {"class": "position-group"})
  for el in elements:
    item = {} 
    # todo add type
    item['type'] = el['group-name'].encode('utf-8')
    item['name'] = el.find('div', {"class": "small_title"}).getText().encode('utf-8').split('-')[0].strip()
    position = ''
    item['personId'] = el.find('div', {"class": "person"})['people_id'].encode('utf-8')
    description = ''
    item['description'] = el.find('div', {"class": "person_text"}).getText().encode('utf-8').strip()
    # url = ''
    pageContainer = el.find('div', {"class": "person_contact"}).find('a')
    # print 
    item['url'] = '' if pageContainer is None else pageContainer['href'].encode('utf-8') #if pageContainer != null # todo add prefix in case or index.jsp leading
    if(item['url'].startswith('index')):
      item['url'] = prefix + item['url']
    item['email'] = el.find('div', {'class': "person_email_container"}).find_all('span')[0].getText().encode('utf-8')
    retdata.append(item)

if mode == "courses":
  table = soup.find('table', id = 'schedule_table')
  # rows = table.findAll('tr')

  rows = soup.find_all('tr')
  headers_list = [item.getText('th').encode('utf-8') for item in rows[0].find_all('th')]#.pop(0)
  headers_list.pop(0)
  # remove first item
  print json.dumps(headers_list, sort_keys=True, indent=4, ensure_ascii=False)

  for row in rows:
    idx = 0
    # tabHeaders = {}
    # tabObject = {}
    item = { } #'code': '', 'title': '', 'link': '', 'schedule': { 'mon': '', 'tue': '', 'wed': '', 'thu': '', 'fr': '' } }
    schedule = {}
    title = ''
    for td in row.find_all('td'):
      # print idx
      if idx == 0:
        title = td.find('a')['title'].encode('utf-8').strip() #[item['title'].encode('utf-8') for item in td.find_all('a')]
        #print json.dumps(title, sort_keys=True, indent=4, ensure_ascii=False)
      else:
        item['schedule'] = []
        day = ''
        if idx==1:
          day = 'mon'
          # schedule['mon'] = td.getText('td').encode('utf-8').strip()
        elif idx==2:
          day = 'tue'
          # schedule['tue'] = td.getText('td').encode('utf-8').strip()
        elif idx==3:
          day = 'wed'
          # schedule['wed'] = td.getText('td').encode('utf-8').strip()
        elif idx==4:
          day = 'thu'
          # schedule['thu'] = td.getText('td').encode('utf-8').strip()
        elif idx==5:
          day = 'fr'
          # schedule['fri'] = td.getText('td').encode('utf-8').strip()
        schedule[day] = td.getText('td').encode('utf-8').strip()
      idx= idx + 1
    item['schedule'] = schedule
    item['title']= title
    
    #append 
    retdata.append(item)


with open(outputFile, 'w') as f:
    json.dump(retdata, f, indent=4, ensure_ascii=False)
