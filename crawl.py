# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from data_diff import Diff
import codecs
import json
import soupsieve
import bs4
import backports.functools_lru_cache
import os
import sys
import io
import re

bspath = os.path.join(os.path.dirname(os.path.abspath(
    __file__)), "libraries/backports.functools_lru_cache-1.6.1")
sys.path.append(bspath)
bspath = os.path.join(os.path.dirname(os.path.abspath(
    __file__)), "libraries/beautifulsoup4-4.8.0")
sys.path.append(bspath)
bspath = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "libraries/soupsieve-1.9.5")
sys.path.append(bspath)


def get_param_from_url(url, param_name):
    return [i.split("=")[-1] for i in url.split("?", 1)[-1].split("&") if i.startswith(param_name + "=")][0]


def json_load_byteified(file_handle):
    return _byteify(
        json.load(file_handle, object_hook=_byteify),
        ignore_dicts=True
    )


def json_loads_byteified(json_text):
    return _byteify(
        json.loads(json_text, object_hook=_byteify),
        ignore_dicts=True
    )

def _byteify(data, ignore_dicts=False):
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [_byteify(item, ignore_dicts=True) for item in data]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    # if it's anything else, return it in its original form
    return data


def removeNullAndTrim(text):
	if text is not None:
		return text.replace(" NULL ", " ").strip()
	else:
		return text



def handlePerson(retdata, position, person, prefix, lang):
    item = {}
    item['_'.join(['position', lang])] = position
    item['_'.join(['name', lang])] = removeNullAndTrim(person.find(
        'div', {"class": "small_title"}).getText().encode('utf-8').split('-')[0])#.strip()
    description = person.find(
        'div', {"class": "person_text"})
    item['_'.join(['description', lang])] = '' if description is None else removeNullAndTrim(description.getText(
    ).encode('utf-8'))#.strip()
    try:
        try:
          imgDiv = person.find('div', {"class": "person_image"})
          item['img'] = prefix + imgDiv['src']
        except (KeyError, ValueError, AttributeError):
          item['img'] = prefix + re.search(r'url\((.+)\)', imgDiv['style']).group(1)
    except (KeyError, ValueError, AttributeError):
        item['img'] = ''
    pageContainer = person.find(
        'div', {"class": "person_contact"}).find('a')
    item['url'] = '' if pageContainer is None else pageContainer['href'].encode(
        'utf-8')
    if(item['url'].startswith('index')):
        item['url'] = prefix + item['url']
    emailDiv = person.find(
        'div', {'class': "person_email_container"})
    if emailDiv is not None:
        try:
            item['email'] = '' if emailDiv is None else emailDiv.find_all('span')[
            0].getText().encode('utf-8')
        except:
            try:
                item['email'] = '' if emailDiv is None else emailDiv.getText().encode('utf-8')
            except:
                item['email'] = ''
    else:
        item['email'] = ''
    id = person.get("people_id", None)
    item['personId'] = id.encode('utf-8') if id is not None else item['email']
    try:
        index = [x['personId']
                    for x in retdata].index(item['personId'])
    except ValueError:
        index = -1
    if(index != -1):
        for key in item:
            retdata[index][key] = item[key]
    else:
        retdata.append(item)

def handleStream(retdata, lang, stream, iType):
    a_containers = stream.find_all('li')
    for ni in a_containers:
        date = removeNullAndTrim(ni.find('div', {'class': 'ann_date'}
                       ).getText().encode('utf-8'))#.strip()
        type = 'pinned' if ni.has_attr('pinned_id') else iType
        titleContainer = ni.find('div', {'class': 'ann_title'}).find('a')
        title = None
        newsId = None
        url = ''
        if titleContainer is not None:
            title = removeNullAndTrim(titleContainer.getText().encode('utf-8'))#.strip()
            try:
                url = removeNullAndTrim(titleContainer['href'].encode('utf-8'))#.strip()
            except (KeyError, ValueError, AttributeError):
                url = ''
            try:
                newsId = re.search("ann=([0-9]+)&?", url).group(1)
            except (KeyError, ValueError, AttributeError):
                newsId = None

        if newsId is not None:
            news_request = requests.get(url)  # // todo below function
            news_response = news_request.content.decode('utf-8').replace("&nbsp;", " NULL ").replace("\\u00A0",
                                                                                                     " ").replace(u"\u0391", "A").replace(u"\u0397", "H").replace("<br />", " ").replace("<br/>", " ").encode('utf-8')
            news_soup = BeautifulSoup(news_response, "html.parser")

            descriptionHtml = news_soup.find(
                'div', {'class': 'announcement_body'})
            description = removeNullAndTrim(str(descriptionHtml).decode(
                'utf-8').encode(
                'utf-8')) if descriptionHtml is not None else ''
            item = {}
            item['_'.join(['description', lang])] = description
            item['_'.join(['title', lang])] = title
            item['date'] = date
            item['type'] = type
            item['url'] = url
            item['newsId'] = newsId

            try:
                index = [x['newsId']
                         for x in retdata].index(item['newsId'])
            except ValueError:
                index = -1
            if(index != -1):
                for key in item:
                    retdata[index][key] = item[key]
            else:
                retdata.append(item)
# config read


def crawlModule(configPath):
	with open(configPath) as json_data_file:
			config = json_load_byteified(json_data_file)
	module = config['module']

	# Webpage connection
	# html = "https://www.csd.uoc.gr/CSD/index.jsp?content=time_schedule&lang=gr"
	outputFile = config['output']
	retdata = []
	firstDone = False
	for lang in config['url']:
			html = config['url'][lang]
			r = requests.get(html)
			c = r.content.decode('utf-8').replace("&nbsp;", " NULL ").replace("\\u00A0",
																																				" ").replace(u"\u0391", "A").replace(u"\u0397", "H").replace("<br />", " ").replace("<br/>", " ").encode('utf-8')
			parser = config['parser'] if 'parser' in config else 'html.parser'
			soup = BeautifulSoup(c, parser)

	# academic_staff works
			if module == "people":
					prefix = 'http://www.csd.uoc.gr/CSD/'
					mode = config.get("mode", None)
					if mode == "text_field":
							for person in soup.find_all('div', {"class": "text_field"}):
									position = config.get("position", {}).get(lang, "")
									handlePerson(retdata, position, person, prefix, lang)
					elif mode == "person":
							for person in soup.find_all('div', {"class": "person"}):
									position = config.get("position", {}).get(lang, "")
									handlePerson(retdata, position, person, prefix, lang)
					elif mode == "position-group":
							elements = soup.find_all('div', {"class": "position-group"})
							for el in elements:
									position = "".join(el['group-name'].encode('utf-8'))
									for person in el.find_all('div', {"class": "person"}):
											handlePerson(retdata, position, person, prefix, lang)

	# seems ok - eng missing
			if module == "schedule":
					table = soup.find('table', id='schedule_table')

					rows = soup.find_all('tr')
					headers_list = [item.getText('th').encode('utf-8')
													for item in rows[0].find_all('th')]
					headers_list.pop(0)

					for row in rows:
							idx = 0
							item = {} 
							schedule = {}
							title = ''
							for td in row.find_all('td'):
									if idx == 0:
											title = removeNullAndTrim(td.find('a')['title'].encode('utf-8'))#.strip()
									else:
											item['schedule'] = []
											day = ''
											if idx == 1:
													day = 'mon'
											elif idx == 2:
													day = 'tue'
											elif idx == 3:
													day = 'wed'
											elif idx == 4:
													day = 'thu'
											elif idx == 5:
													day = 'fr'
											schedule[day] = removeNullAndTrim(td.getText('td').encode('utf-8'))#.strip()
									idx = idx + 1
							item['schedule'] = schedule
							item['title'] = title
							retdata.append(item)

	# works
			if module == "contacts":
				canAdd = False
				atRegex = re.compile('.*at-icon.*')
				phoneRegex = re.compile('.*phone-icon.*')
				faxRegex = re.compile('.*fax-icon.*')
				facebookRegex = re.compile('.*facebook-icon.*')
				linkRegex = re.compile('.*link-icon.*')
				social = [ ]
				email = { }
				phone = { }
				fax = { } 
				link = { }
				create_real_email_spans = soup.find_all('span', {"class": "create_real_email"})
				for each in create_real_email_spans:
					each.extract()
				elements = soup.find_all('div', {"class": "contact_department_container"})
				itemsAdded = 0
				for el in elements:
					item = { }
					divs = el.find_all('div',recursive=False)
					for i in range(len(divs)):
						if divs[i].has_attr("class") and divs[i]['class'] == ['input_label']:
							label = removeNullAndTrim(divs[i].getText().encode('utf-8'))#.strip() 
						else:
							img = divs[i].find('img')
							if img is not None:
								if atRegex.match(img['src']):
									email['title'] = removeNullAndTrim(img['title'].encode('utf8'))#.strip() #.decode('latin1').strip()
									email['value'] = removeNullAndTrim(divs[i].getText().encode('utf-8'))#.strip()
									item[u'_'.join(['email', lang])] = email
								elif phoneRegex.match(img['src']):
									phone['title'] = removeNullAndTrim(img['title'].encode('utf-8'))#.strip()
									phone['value'] = removeNullAndTrim(divs[i].getText().encode('utf-8'))#.strip()
									item[u'_'.join(['phone', lang])] = phone
								elif faxRegex.match(img['src']):
									fax['title'] = removeNullAndTrim(img['title'].encode('utf-8'))#.strip()
									fax['value'] = removeNullAndTrim(divs[i].getText().encode('utf-8'))#.strip()
									item[u'_'.join(['fax', lang])] = fax
								elif linkRegex.match(img['src']):
									link['title'] = removeNullAndTrim(img['title'].encode('utf-8'))#.strip()
									link['value'] = removeNullAndTrim(divs[i].find('a')["href"].encode('utf-8'))#.strip()
									item[u'_'.join(['link', lang])] = link
								elif facebookRegex.match(img['src']):
									break
						if divs[i].has_attr("class") and divs[i]['class'] == ['field_separator']: 
							if canAdd == True:
								item[u'_'.join(['label', lang])] = label
								if(firstDone):
									for key in item:
										retdata[itemsAdded][key] = item[key]
								else:
									retdata.append(item)
								itemsAdded = itemsAdded + 1
								email = { }
								phone = { }
								fax = { } 
								link = { }
								item = { }
								label = ''
							else:
								canAdd = True
	# issue is appending to the same one
			if module == "model-program":
					table = soup.find_all('div', id="currentcontent")
					for tab in table:
							temp = tab
							matrices = []
							for t in temp.find_all("table", {"class": "matrix"}):
									matrices.append(t)
									t.extract()
							titleArray = res = [i for i in temp.find_all(
									'strong') if i.getText().encode('utf-8').strip() != 'NULL']
							if len(matrices) == len(titleArray):
									for i in range(len(matrices)):
											item = {}
											semesterTitle = removeNullAndTrim(titleArray[i].getText().encode(
													'utf-8'))#.strip()
											item[u'_'.join(['title', lang])] = semesterTitle
											item[u'_'.join(['courses', lang])] = []
											headers = []
											rows = matrices[i].find_all("tr")
											for r in range(len(rows) - 1):
													course = {}
													tds = rows[r].find_all("td")
													for td in range(len(tds)):
															textValue = tds[td].getText().encode(
																	'utf-8').replace("\xce\x95", "E").replace("\xce\x99", "I").replace("NULL ", "").strip()
															if(r == 0):
																	headers.append(textValue)
															else:
																	course[headers[td]] = textValue
													if(r > 0):
															item[u'_'.join(['courses', lang])].append(course)
											if(len(retdata) == len(matrices)):
													for key in item:
															retdata[i][key] = item[key]
											else:
													retdata.append(item)
	# fails
			if module == "courses":
					course_tables = soup.find_all(
							'tr', {'id': re.compile(r'course[0-9]+')})
					headersMap = {}
					headersMap["Area"]="area_name"
					headersMap["Code"]="code"
					headersMap["Course email"] ="email"
					headersMap["Course website"] = "url"
					headersMap["Description"]= "description"
					headersMap["ECTS"]="ects"
					headersMap["Name"]="name"
					headersMap["Program"]="program"
					headersMap["Prerequisites"]="prerequisites"
					headersMap["Suggested"]="suggested"
					headersMap["winter semester"]="winter_semester"
					headersMap["spring semester"]="spring_semester"

					headersMap["Περιοχή"]="area_name"
					headersMap["Κωδικός"]="code"
					headersMap["Email μαθήματος"] ="email"
					headersMap["Ιστοσελίδα μαθήματος"] = "url"
					headersMap["Περιγραφή"]= "description"
					headersMap["ECTS"]="ects"
					headersMap["Όνομα"]="name"
					headersMap["Πρόγραμμα"]="program"
					headersMap["Προαπαιτούμενα"]="prerequisites"
					headersMap["Προτεινόμενα"]="suggested"
					headersMap["χειμερινό εξάμηνο"]="winter_semester"
					headersMap["εαρινό εξάμηνο"]="spring_semester"
					for table in course_tables:
							a_containers = table.find_all('a')
							for ci in range(len(a_containers)):
									course_url = a_containers[ci]['href'].encode('utf-8')
									course_request = requests.get(course_url)
									course_response = course_request.content.decode('utf-8').replace("&nbsp;", " NULL ").replace("\\u00A0",
																																																							" ").replace(u"\u0391", "A").replace(u"\u0397", "H").replace("<br />", " ").replace("<br/>", " ").encode('utf-8')
									course_soup = BeautifulSoup(course_response, "html.parser")
									create_real_email_spans = course_soup.find_all('span', {"class": "create_real_email"})
									for each in create_real_email_spans:
										each  .extract()
									course_details_div = course_soup.find(
											'div', {'class': 'text_field rel hidden'})
									divs = course_details_div.find_all('div', recursive=False)
									shouldAddFields = False
									item = {}
									courseId = get_param_from_url(course_url, 'course')
									item["courseId"] = courseId
									prevKey = ''
									secondaryKey = ''
									for i in range(len(divs)):
											if divs[i]['class'] == ['text_field_label_smaller']:
													shouldAddFields = True
											elif shouldAddFields == True:
													if divs[i]['class'] == ['input_label']:
															prevKey = removeNullAndTrim(divs[i].getText().encode('utf-8'))#.strip()
													elif prevKey != '':
															if prevKey in headersMap:
																prefix = headersMap[prevKey]
																if prefix in ["email", "url"]:
																	paragraphs = divs[i].find_all('p')
																	candValues = []
																	single = {}
																	item[prefix] = []
																	if (len(paragraphs)  == 2):
																		for ci in range(len(paragraphs)):
																			ciArray = re.split(': |\n',removeNullAndTrim(paragraphs[ci].getText().encode('utf-8')))
																			single['label'] = headersMap[ciArray[0]] #if ciArray[0] in headersMap else ''
																			single['value'] = ciArray[1]
																			item[prefix].append(single)
																			single = {}
																	else:
																		candValues = re.split(': |\n',removeNullAndTrim(divs[i].getText().encode('utf-8')))
																		if(len(candValues) > 1):
																			for si in range(len(candValues) - 1):
																				single['label'] = headersMap[candValues[si]] if candValues[si] in headersMap else ''
																				single['value'] = candValues[si+1]
																				item[prefix].append(single)
																				single = {}
																				si = si +1
																		else:
																			single['label'] = ''
																			single['value'] = candValues[0]
																			item[prefix].append(single)
																			single = {}
																else:
																  actualKey = prefix if prefix in ["ects"] else '_'.join([prefix, lang])
																  value = divs[i].getText().encode('utf-8').replace("NULL ", "").replace("\r\n\n", "").replace("\r\n", "").replace("\r\n\t\n", " ").replace("\n", " ").strip()
																  item[actualKey] = value

															prevKey = ''
									index = 0
									try:
											index = [x['courseId']
															for x in retdata].index(item['courseId'])
									except ValueError:
											index = -1
									if(index != -1):
											for key in item:
													retdata[index][key] = item[key]
									else:
											retdata.append(item)
			if module == "documents":
					prefix = 'http://www.csd.uoc.gr/CSD/'
					elements = soup.find("ol")
					for el in elements.find_all("li"):
							item = {}
							item["label"] = removeNullAndTrim(el.getText().split('(')[0].encode('utf-8'))#.strip()
							sourceElements = el.find_all("a")
							item["source"] = {}
							for src in sourceElements:
									if src.getText() == "PDF":
											item["source"]["pdf"] = prefix + removeNullAndTrim(src["href"].encode('utf-8'))#.strip()
									if src.getText() == "WORD":
											item["source"]["word"] = prefix + removeNullAndTrim(src["href"].encode('utf-8'))#.strip()
							retdata.append(item)
			if module in ['announcements', 'news'] :
					newsStream = soup.find_all(
                    'div', {'class': 'announcements_cont'})
					for stream in newsStream:
						handleStream(retdata, lang, stream, 'stream')
					newsImportant = soup.find_all(
                    'div', {'class': 'important_announcements_cont'})
					for stream in newsImportant:
						handleStream(retdata, lang, stream, 'important')
			# check if firstDone is actually needed
			firstDone = True

	# check if file exists, read it
	if os.path.isfile(outputFile) and os.stat(outputFile).st_size != 0:
			olddata = json_load_byteified(open(outputFile))
			retdata = retdata + olddata

	with open(outputFile, 'w') as f:
			json.dump(retdata, f, indent=4, ensure_ascii=False, sort_keys=True)
