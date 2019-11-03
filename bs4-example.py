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

table = soup.find('table', id = 'schedule_table')
# rows = table.findAll('tr')

rows = soup.find_all('tr')
headers_list = [item.getText('th').encode('utf-8') for item in rows[0].find_all('th')]#.pop(0)
headers_list.pop(0)
# remove first item
print json.dumps(headers_list, sort_keys=True, indent=4, ensure_ascii=False)

courses = []
for row in rows:
  idx = 0
  # tabHeaders = {}
  # tabObject = {}
  course = { } #'code': '', 'title': '', 'link': '', 'schedule': { 'mon': '', 'tue': '', 'wed': '', 'thu': '', 'fr': '' } }
  schedule = {}
  title = ''
  for td in row.find_all('td'):
    # print idx
    if idx == 0:
      title = td.find('a')['title'].encode('utf-8').strip() #[item['title'].encode('utf-8') for item in td.find_all('a')]
      #print json.dumps(title, sort_keys=True, indent=4, ensure_ascii=False)
    else:
      course['schedule'] = []
      day = ''
      if idx==1:
        # day = 'mon'
        schedule['mon'] = td.getText('td').encode('utf-8').strip()
      elif idx==2:
        day = 'tue'
        schedule['tue'] = td.getText('td').encode('utf-8').strip()
      elif idx==3:
        # day = 'wed'
        schedule['wed'] = td.getText('td').encode('utf-8').strip()
      elif idx==4:
        # day = 'thu'
        schedule['thu'] = td.getText('td').encode('utf-8').strip()
      elif idx==5:
        # day = 'fr'
        schedule['fri'] = td.getText('td').encode('utf-8').strip()
      # course['schedule'].append(td.getText('td'))
      # schedule.append(td.getText('td'))
      # course['schedule'][day] = td.getText('td')
      #print json.dumps(text, sort_keys=True, indent=4, ensure_ascii=False)
    idx= idx + 1
  course['schedule'] = schedule
  course['title']= title
  courses.append(course)
  # print json.dumps(course, sort_keys=True, indent=4, ensure_ascii=False)
with open(outputFile, 'w') as f:
    json.dump(courses, f, indent=4, ensure_ascii=False)
    # courses.append(course)
# print json.dumps(courses, sort_keys=True, indent=4, ensure_ascii=False)
    # print td.find('a')['title'] if td.find('a') else ''
  # print [item.getText('td').encode('utf-8') for item in row.find_all('td')]
  # print [item['title']. for item in row.find_all('a')]
  

# rows = soup.findAll('td', {
#     'class': ['a61cl', 'a65cr', 'a69cr', 'a73cr', 'a77cr', 'a81cr', 'a85cr',
#     'a89cr', 'a93cr', 'a97cr']})

# headers = soup.findAll('td', {
#     'class': ['a20c','a24c', 'a28c', 'a32c', 'a36c', 'a40c', 'a44c', 'a48c',
#     'a52c']})

# headers_list = [item.getText('div') for item in headers]

# rows_list=[item.getText('div') for item in rows]

# print headers_list
# html_data = """
# <table>
#   <tr>
#     <td>Card balance</td>
#     <td>$18.30</td>
#   </tr>
#   <tr>
#     <td>Card name</td>
#     <td>NAMEn</td>
#   </tr>
#   <tr>
#     <td>Account holder</td>
#     <td>NAME</td>
#   </tr>
#   <tr>
#     <td>Card number</td>
#     <td>1234</td>
#   </tr>
#   <tr>
#     <td>Status</td>
#     <td>Active</td>
#   </tr>
# </table>
# """


# table_data = [[cell.text for cell in row("td")]
#                          for row in BeautifulSoup(html_data)("tr")]
# print json.dumps(dict(table_data))