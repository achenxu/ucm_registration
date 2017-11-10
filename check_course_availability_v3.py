import requests, bs4, sys

USERNAME = ''
PASSWORD = ''

PROGRAM_CODE = 'CSE'
TERM_CODE = '201810'
OPEN_CLASSES = 'Y'
NEEDED_SECTIONS = ['10221', '10966']

def soup_html(html):
	return bs4.BeautifulSoup(html,'html.parser')

def courses_available(program_code, term_code, open_classes, needed_sections):
	available_sections = []
	data = {'subjcode': program_code, 'validterm': term_code, 'openclasses': open_classes }
	post_data = requests.post('https://mystudentrecord.ucmerced.edu/pls/PROD/xhwschedule.P_ViewSchedule', data=data)
	soup = soup_html(post_data.text)
	sections = soup.select('tr > td:nth-of-type(1)')
	sections = [s.text for s in sections if s.text != '' and s.text != '\xa0']
	for s in needed_sections:
		if s in sections:
			available_sections.append(s)
	return available_sections

def login_to_portal(username, password):
	s = requests.Session()
	data = { 'username': username, 'password': password }
	resp = s.get('https://cas.ucmerced.edu/cas/login?service=https://my.ucmerced.edu/uPortal/Login%3FrefUrl%3D%2FuPortal%2Ff%2Fu20l1s171%2Fnormal%2Frender.uP')
	soup = soup_html(resp.text)
	inputs_hidden = soup.select('input[type=hidden]')
	for inp in inputs_hidden:
		data[inp['name']] = inp['value']
	resp = s.post('https://cas.ucmerced.edu/cas/login?service=https://my.ucmerced.edu/uPortal/Login%3FrefUrl%3D%2FuPortal%2Ff%2Fu20l1s171%2Fnormal%2Frender.uP', data=data)
	if resp.status_code == 200:
		return s
	else:
		sys.exit()

def register_for_sections(s, term, section_list):
	resp = s.get('https://mystudentrecord.ucmerced.edu/pls/PROD/twbkwbis.P_WWWLogin?ret_code=R')
	data = { 'term_in': term }
	resp = s.post('https://mystudentrecord.ucmerced.edu/pls/PROD/bwskfreg.P_AltPin', data=data)
	soup = soup_html(resp.text)
	data = []
	inputs_hidden = soup.select('input, select')
	for inp in inputs_hidden:	
		name = inp.get('name')
		val = inp.get('value', '')
		if name == 'RSTS_IN' and val == 'RW':
			break
		elif name is not None and name != 'KEYWRD_IN':
			data.append((name, val))
	for i in range(0,10):
		if i < len(section_list):
			data.append(('CRN_IN', section_list[i]))
		else:
			data.append(('CRN_IN', ''))			
		data.append(('assoc_term_in', ''))
		data.append(('start_date_in', ''))
		data.append(('end_date_in', ''))
		data.append(('RSTS_IN', 'RW'))
	input_totals = soup.select('input[name=regs_row], input[name=wait_row], input[name=add_row]')
	for inp in input_totals:
		data.append((inp.get('name', ''), inp.get('value', '')))
	data.append(('REG_BTN', 'Submit Changes'))
	# POST the data
	resp = s.post('https://mystudentrecord.ucmerced.edu/pls/PROD/bwckcoms.P_Regs', data=data)
	
if courses_available(PROGRAM_CODE, TERM_CODE, OPEN_CLASSES ,NEEDED_SECTIONS):
	session = login_to_portal(USERNAME, PASSWORD)
	register_for_sections(session, TERM_CODE, NEEDED_SECTIONS)