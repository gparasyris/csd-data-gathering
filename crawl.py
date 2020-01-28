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

# def getUrlFromStyle(element):
#   div_style = element['style']
#   style = cssutils.parseStyle(div_style)
#   url = style['background-image']

#   >>> url
#   u'url(/uploads/images/players/16113-1399107741.jpeg)'
#   >>> url = url.replace('url(', '').replace(')', '') 


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


def handlePerson(retdata, position, person, prefix, lang):
    # print( ">>>> " + position)
    item = {}
    # todo add type
    item['_'.join(['position', lang])] = position
    item['_'.join(['name', lang])] = person.find(
        'div', {"class": "small_title"}).getText().encode('utf-8').split('-')[0].strip()
    # position = ''
    description = person.find(
        'div', {"class": "person_text"})
    item['_'.join(['description', lang])] = '' if description is None else description.getText(
    ).encode('utf-8').strip()
    try:
        try:
          imgDiv = person.find('div', {"class": "person_image"})
          item['img'] = prefix + imgDiv['src']
        except (KeyError, ValueError, AttributeError):
          item['img'] = prefix + re.search(r'url\((.+)\)', imgDiv['style']).group(1)
    except (KeyError, ValueError, AttributeError):
        item['img'] = ''
    # url = ''
    pageContainer = person.find(
        'div', {"class": "person_contact"}).find('a')
    # # print
    item['url'] = '' if pageContainer is None else pageContainer['href'].encode(
        'utf-8')  # if pageContainer != null # todo add prefix in case or index.jsp leading
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
        # index = map(operator.attrgetter('id'), my_list).index('specific_id')
        index = [x['personId']
                    for x in retdata].index(item['personId'])
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
			# son_load_byteified(open(outputFile))
			config = json_load_byteified(json_data_file)

	module = config['module']

	# Webpage connection
	# html = "https://www.csd.uoc.gr/CSD/index.jsp?content=time_schedule&lang=gr"
	outputFile = config['output']
	retdata = []
	firstDone = False
	for lang in config['url']:
			# print('******* ---- ' + lang)
			# foreach lang
			html = config['url'][lang]
			r = requests.get(html)
			c = r.content.decode('utf-8').replace("&nbsp;", " NULL ").replace("\\u00A0",
																																				" ").replace(u"\u0391", "A").replace(u"\u0397", "H").replace("<br />", " ").replace("<br/>", " ").encode('utf-8')
			soup = BeautifulSoup(c, "html.parser")

			# todo all lines should call another function that try catches and returns
			# fail value

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
							# print(len(elements))
							for el in elements:
									position = "".join(el['group-name'].encode('utf-8'))
									# print( el['group-name'])
									# # print el
									for person in el.find_all('div', {"class": "person"}):
											handlePerson(retdata, position, person, prefix, lang)
									# # print( ">>>> " + position)
									# item = {}
									# # todo add type
									# item['_'.join(['position', lang])] = position
									# item['_'.join(['name', lang])] = person.find(
									#     'div', {"class": "small_title"}).getText().encode('utf-8').split('-')[0].strip()
									# # position = ''
									# item['personId'] = person['people_id'].encode('utf-8')
									# description = ''
									# item['_'.join(['description', lang])] = person.find(
									#     'div', {"class": "person_text"}).getText().encode('utf-8').strip()
									# # url = ''
									# pageContainer = person.find(
									#     'div', {"class": "person_contact"}).find('a')
									# # # print
									# item['url'] = '' if pageContainer is None else pageContainer['href'].encode(
									#     'utf-8')  # if pageContainer != null # todo add prefix in case or index.jsp leading
									# if(item['url'].startswith('index')):
									#     item['url'] = prefix + item['url']
									# emailDiv = person.find(
									#     'div', {'class': "person_email_container"})
									# item['email'] = '' if emailDiv is None else emailDiv.find_all('span')[
									#     0].getText().encode('utf-8')
									# try:
									#     # index = map(operator.attrgetter('id'), my_list).index('specific_id')
									#     index = [x['personId']
									#              for x in retdata].index(item['personId'])
									# except ValueError:
									#     index = -1
									# if(index != -1):
									#     for key in item:
									#         retdata[index][key] = item[key]
									# else:
									#     retdata.append(item)

	# seems ok - eng missing
			if module == "schedule":
					table = soup.find('table', id='schedule_table')
					# rows = table.findAll('tr')

					rows = soup.find_all('tr')
					headers_list = [item.getText('th').encode('utf-8')
													for item in rows[0].find_all('th')]  # .pop(0)
					headers_list.pop(0)
					# remove first item
					# # print json.dumps(headers_list, sort_keys=True, indent=4, ensure_ascii=False)

					for row in rows:
							idx = 0
							# tabHeaders = {}
							# tabObject = {}
							item = {}  # 'code': '', 'title': '', 'link': '', 'schedule': { 'mon': '', 'tue': '', 'wed': '', 'thu': '', 'fr': '' } }
							schedule = {}
							title = ''
							for td in row.find_all('td'):
									# # print idx
									if idx == 0:
											# [item['title'].encode('utf-8') for item in td.find_all('a')]
											title = td.find('a')['title'].encode('utf-8').strip()
											# # print json.dumps(title, sort_keys=True, indent=4, ensure_ascii=False)
									else:
											item['schedule'] = []
											day = ''
											if idx == 1:
													day = 'mon'
													# schedule['mon'] = td.getText('td').encode('utf-8').strip()
											elif idx == 2:
													day = 'tue'
													# schedule['tue'] = td.getText('td').encode('utf-8').strip()
											elif idx == 3:
													day = 'wed'
													# schedule['wed'] = td.getText('td').encode('utf-8').strip()
											elif idx == 4:
													day = 'thu'
													# schedule['thu'] = td.getText('td').encode('utf-8').strip()
											elif idx == 5:
													day = 'fr'
													# schedule['fri'] = td.getText('td').encode('utf-8').strip()
											schedule[day] = td.getText('td').encode('utf-8').strip()
									idx = idx + 1
							item['schedule'] = schedule
							item['title'] = title

							# append
							retdata.append(item)

	# works
			if module == "contacts":
				canAdd = False
				# at, phone, fax, facebook, link
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
						# label = ''
						# try:
						if divs[i].has_attr("class") and divs[i]['class'] == ['input_label']:
							label = divs[i].getText().encode('utf-8').strip() 
						else:
							img = divs[i].find('img')
							# print( img)
							if img is not None:
								# # print img
								if atRegex.match(img['src']):
									# email['title'] = img['title'].encode('raw_unicode_escape').decode('utf-8').strip()#.encode('utf-8').strip()
									email['title'] = img['title'].encode('utf8').strip() #.decode('latin1').strip()
									email['value'] = divs[i].getText().encode('utf-8').strip()
									item[u'_'.join(['email', lang])] = email
									# # print item
								elif phoneRegex.match(img['src']):
									phone['title'] = img['title'].encode('utf-8').strip()
									phone['value'] = divs[i].getText().encode('utf-8').strip()
									item[u'_'.join(['phone', lang])] = phone
								elif faxRegex.match(img['src']):
									fax['title'] = img['title'].encode('utf-8').strip()
									fax['value'] = divs[i].getText().encode('utf-8').strip()
									item[u'_'.join(['fax', lang])] = fax
								elif linkRegex.match(img['src']):
									link['title'] = img['title'].encode('utf-8').strip()
									link['value'] = divs[i].find('a')["href"].encode('utf-8').strip()
									item[u'_'.join(['link', lang])] = link
								elif facebookRegex.match(img['src']):
									break
						if divs[i].has_attr("class") and divs[i]['class'] == ['field_separator']: 
							if canAdd == True:
								# # print item
								# print( 'appending...')
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
							# # print item
						# except KeyError:
						#   continue



						# try:
						#   if divs[i]['class'] == ['field_separator']: 
						#     i += 1
						#     if divs[i]['class'] == ['input_label']:
						#       if divs[i].getText() == "Social Networks" or divs[i].getText() == "Μέσα Κοινωνικής Δικτύωσης":
						#         break
						#       item["label"] = divs[i].getText().encode('utf-8').strip() 
						#       i += 1

						#     if divs[i].find("img")["title"] == "Secretariat's page":
						#       item["link"] ={}
						#       item["link"]["name"] = divs[i].getText().encode('utf-8').strip()
						#       item["link"]["url"] = divs[i].find('a')["href"].encode('utf-8').strip()
						#       i += 1

						#     if divs[i].find("img")["title"] == "Telephone":
						#       item["telephone"] = divs[i].getText().encode('utf-8').strip()
						#       i += 1

						#     if divs[i].find("img")["title"] == "Fax":
						#       item["fax"] = divs[i].getText().encode('utf-8').strip()
						#       i += 1

						#     emailElement = divs[i].find("img")
						#     if emailElement and emailElement["title"] == "Email address": 
						#       item["email"]= divs[i].find("span").getText().encode('utf-8').strip()
						#       i += 1
						#     retdata.append(item)
						# except KeyError:
						#   continue
				# print( retdata)

	# issue is appending to the same one
			if module == "model-program":
					table = soup.find_all('div', id="currentcontent")
					for tab in table:
							temp = tab
							matrices = []
							for t in temp.find_all("table", {"class": "matrix"}):
									matrices.append(t)
									t.extract()
							# # print temp
							# TODO FIX NULL
							titleArray = res = [i for i in temp.find_all(
									'strong') if i.getText().encode('utf-8').strip() != 'NULL']
							# # print len(titleArray)
							# # print titleArray
							# for t in titleArray:
							#   # print t.getText('td').encode('utf-8').strip()
							if len(matrices) == len(titleArray):
									for i in range(len(matrices)):
											item = {}
											semesterTitle = titleArray[i].getText().encode(
													'utf-8').strip()
											# # print semesterTitle
											item[u'_'.join(['title', lang])] = semesterTitle
											item[u'_'.join(['courses', lang])] = []
											headers = []
											rows = matrices[i].find_all("tr")
											for r in range(len(rows) - 1):
													course = {}
													tds = rows[r].find_all("td")
													for td in range(len(tds)):
															# textValue = u''.join(tds[td].getText().encode('utf-8').strip())
															textValue = tds[td].getText().encode(
																	'utf-8').replace("\xce\x95", "E").replace("\xce\x99", "I").replace("NULL ", "").strip()
															if(r == 0):
																	headers.append(textValue)
															else:
																	course[headers[td]] = textValue
													if(r > 0):
															item[u'_'.join(['courses', lang])].append(course)
											# semesters.append(item)
											# index = map(operator.attrgetter('id'), my_list).index('specific_id')
											if(len(retdata) == len(matrices)):
													# print( 'appending')
													for key in item:
															retdata[i][key] = item[key]
											else:
													retdata.append(item)
									# retdata = semesters

											# # print item
	# fails
			if module == "courses":
					# soup.find_all('a', {'href': re.compile(r'crummy\.com/')})
					course_tables = soup.find_all(
							'tr', {'id': re.compile(r'course[0-9]+')})
					# # print course_tables
					headersMap = {}
					#   "Area": "area_name",
					#   "Code": "code",
					#   "Course Email": "email",
					#   "Description": "description",
					#   "ECTS": "ects",
					#   "Name": "name"
					# }
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
					# headersMap = json.dumps(headerData)
					for table in course_tables:
							# # print table
							# # print '------'
							a_containers = table.find_all('a')
							# # print a_containers
							# for a_container in a_containers:
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
									# # print '---'
									# # print course_details_div
									# # print '---'
									# for el in course_details_div:
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
															prevKey = divs[i].getText().encode('utf-8').strip()
													elif prevKey != '':
															# .encode('utf-8').strip()
															# # print prevKey
															# # print headersMap
															# # print (prevKey in headersMap)
															# # print(headersMap[prevKey] is not None)
															# hasattr(headersMap, prevKey):
															# # print 'val'
															# # print prevKey
															if prevKey in headersMap:
																prefix = headersMap[prevKey]
																if prefix in ["email", "url"]:
																	# import re
																	# q = "winter semester:  http://www.csd.uoc.gr/~hy118a/\nspring semester:  http://www.csd.uoc.gr/~hy118b/"
																	# # print(q.split(['\n',': ']))

																	paragraphs = divs[i].find_all('p')
																	candValues = []
																	single = {}
																	item[prefix] = []
																	if (len(paragraphs)  == 2):
																		for ci in range(len(paragraphs)):
																			# print( 'paragraph*********')
																			# print( paragraphs[ci].getText().encode('utf-8').strip())
																			ciArray = re.split(': |\n',paragraphs[ci].getText().encode('utf-8').strip())
																			single['label'] = headersMap[ciArray[0]] #if ciArray[0] in headersMap else ''
																			single['value'] = ciArray[1]
																			item[prefix].append(single)
																			single = {}
																			# # print '%%%'
																			# for element in re.split(': |\n',paragraphs[ci].getText().encode('utf-8').strip()):
																				# candValues.append(element)
																			# candValues = candValues + re.split(': |\n',paragraphs[ci].getText().encode('utf-8').strip())
																			# # print candValues
																			# # print '%%%'
																	else:
																		candValues = re.split(': |\n',divs[i].getText().encode('utf-8').strip())
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
																	# # print '***'
																	# # print divs[i].find_all('p')
																	# # print prefix
																	# # print paragraphs
																	# # print len(candValues)
																	# # print len(paragraphs)
																	# # print '***'
																	# item[prefix] = []
																	# single ={}
																	# for si in range(len(candValues)):
																	#   # # print '***'
																	#   # # print len(candValues[si])
																	#   # # print si
																	#   if(si == 0 and len(candValues) == 1):
																	#     single['label'] = ''
																	#     single['value'] = candValues[si]
																	#     item[prefix].append(single)
																	#     secondaryKey = ''
																	#     # # print '###'
																	#     # # print single
																	#   else:
																	#     # # print 'vvv'
																	#     # # print secondaryKey
																	#     # # print candValues[si]
																	#     # # print (secondaryKey in headersMap)
																	#     # # print '^^^'
																	#     if secondaryKey == '':
																	#       if candValues[si] in headersMap:
																	#         secondaryKey = candValues[si]
																	#       # # print secondaryKey
																	#     elif secondaryKey in headersMap:
																	#       # single[headersMap[secondaryKey]] = candValues[si]
																				
																	#       single['label'] = headersMap[secondaryKey]
																	#       single['value'] = candValues[si]
																	#       item[prefix].append(single)
																	#       # print '###'
																	#       # print secondaryKey
																	#       # print headersMap[secondaryKey]
																	#       # print candValues[si]
																	#       # print single
																	#       # print '###'
																	#       secondaryKey = ''
																				# # print '>>>'
																				# # print single
																		# if single:
																		#   single ={}
															# # print item
																else:
																  actualKey = prefix if prefix in ["ects"] else '_'.join([prefix, lang])
																  value = divs[i].getText().encode('utf-8').replace("NULL ", "").replace("\r\n\n", "").replace("\r\n", "").replace("\r\n\t\n", " ").replace("\n", " ").strip()
																  item[actualKey] = value

															# item[prevKey] = divs[i].getText().encode('utf-8').strip()
															prevKey = ''
									# print( item)
									index = 0
									try:
											# index = map(operator.attrgetter('id'), my_list).index('specific_id')
											index = [x['courseId']
															for x in retdata].index(item['courseId'])
									except ValueError:
											index = -1
									if(index != -1):
											for key in item:
													retdata[index][key] = item[key]
									else:
											retdata.append(item)
									# if(len(retdata) == len(a_containers)):
									#   for key in item:
									#       retdata[i][key] = item[key]
									# else:
									#     retdata.append(item)
									# retdata.append(item)
							# # print retdata
							# if(tds[1] is not None):
	# works
			if module == "documents":
					prefix = 'http://www.csd.uoc.gr/CSD/'
					elements = soup.find("ol")
					for el in elements.find_all("li"):
							item = {}
							item["label"] = el.getText().split('(')[0].encode('utf-8').strip()
							sourceElements = el.find_all("a")
							item["source"] = {}
							for src in sourceElements:
									if src.getText() == "PDF":
											item["source"]["pdf"] = prefix + src["href"].encode('utf-8').strip()
									if src.getText() == "WORD":
											item["source"]["word"] = prefix + src["href"].encode('utf-8').strip()
							retdata.append(item)
			firstDone = True
			# html = config['url'][lang]
			# r=requests.get(html)``
			# c=r.content.decode('utf-8').replace("&nbsp;", " NULL ").replace("\\u00A0", #
			#                       " ").replace(u"\u0391", "A").replace(u"\u0397", "H").replace("<br />", " ").replace("<br/>", " ").encode('utf-8')
			# soup=BeautifulSoup(c,"html.parser")


	# check if file exists, read it
	if os.path.isfile(outputFile) and os.stat(outputFile).st_size != 0:
			# with open(outputFile) as json_file:
			# with open(outputFile, "rb") as json_file:
					# contents = json_file.read().decode("UTF-8")
					# olddata = json.load(json_file, encoding = "utf-8")
					# retdata = retdata + olddata
			olddata = json_load_byteified(open(outputFile))
			retdata = retdata + olddata

	with open(outputFile, 'w') as f:
	# with io.open(outputFile, 'w', encoding='utf-8') as f:
			# data = json.dumps(retdata, indent=4,   sort_keys=True, ensure_ascii=False)
			# unicode(data) auto-decodes data to unicode if str
			# f.write(unicode(data))
			# json.dump(unicode(retdata), f, indent=4, ensure_ascii=False, sort_keys=True)
			json.dump(retdata, f, indent=4, ensure_ascii=False, sort_keys=True)
