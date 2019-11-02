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

from  bs4 import BeautifulSoup



html_data = """
<table>
  <tr>
    <td>Card balance</td>
    <td>$18.30</td>
  </tr>
  <tr>
    <td>Card name</td>
    <td>NAMEn</td>
  </tr>
  <tr>
    <td>Account holder</td>
    <td>NAME</td>
  </tr>
  <tr>
    <td>Card number</td>
    <td>1234</td>
  </tr>
  <tr>
    <td>Status</td>
    <td>Active</td>
  </tr>
</table>
"""


table_data = [[cell.text for cell in row("td")]
                         for row in BeautifulSoup(html_data)("tr")]
print json.dumps(dict(table_data))