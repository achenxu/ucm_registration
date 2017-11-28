from splinter import Browser
from email.mime.text import MIMEText
import smtplib, time, sys, os

username = 'UCM_Username'
password = 'UCM_Password'
linux_user = 'OS_Username'
email_to = 'Recipient_Email'

# Find subj_category using browser "Inspect Element"
subj_category = 'MATH'
course_name = 'Numerical Methods Sci & Engr'
section1 = '10590'
section2 = '14076'

# (Optional) To Drop Sections, Change drop to 'True'. Use at your own risk.
drop = False
course_name_drop = 'the night lab'
section1_drop = '10590'
section2_drop = '10754'

# ---------------------End of user inputs---------------------

username_email = username + '@ucmerced.edu'
email_from = username_email
email_subject = 'Registered for ' + course_name + '!'
email_message = 'Registered for ' + course_name + '!'
if drop:
	email_subject = 'You just ditched ' + course_name_drop + ' for ' + course_name + '!'
	email_message = 'You just ditched ' + course_name_drop + ' for ' + course_name + '!'

def drop_sections(b,course_name_drop, section1_drop, section2_drop):
	# Search for classsdrop
	if section1_drop == '':
		section1_drop = 'Empty feilds are very bad here.'
	if section2_drop == '':
		section2_drop = 'Empty feilds are very VERY bad.'
	rows = b.find_by_css('table.datadisplaytable > tbody > tr')
	rowNum = -1	
	for row in rows:
		if section1_drop in row.text or section2_drop in row.text:
			b.find_by_css('select')[rowNum].find_by_css('option')[1].click()
		rowNum += 1
	b.find_by_css('form input[type=submit][value="Submit Changes"]').click()

def register(b, section1, section2, drop, course_name_drop, section1_drop, section2_drop):
	# Login
	url = "https://my.ucmerced.edu/uPortal/f/u20l1s171/normal/render.uP"
	b.visit(url)
	b.fill('username', username)
	b.fill('password', password)
	b.find_by_name('submit').click()
	# Navigate to registration page
	b.find_link_by_partial_text('myRegistration').first.click()
	b.windows.current = b.windows[1]
	b.find_link_by_partial_text('Add').click()
	b.find_by_css('form input[type=submit]')[1].click()
	# Register or Drop and Register
	if drop == True:
		drop_sections(b,course_name_drop, section1_drop, section2_drop)
	b.find_by_id('crn_id1').fill(section1)
	b.find_by_id('crn_id2').fill(section2)
	b.find_by_css('form input[type=submit][value="Submit Changes"]').click()

def verify_registration(b, section1):
	b.windows[1].close()
	b.windows.current = b.windows[0]
	b.find_link_by_partial_text('myRegistration').first.click()
	b.windows.current = b.windows[1]
	b.find_link_by_partial_text('Concise Student Schedule').click()
	b.find_by_css('form input[type=submit]')[1].click()
	elems = b.find_by_css('table.datadisplaytable tr td:first-of-type')
	for e in elems:
		if section1 in e.text:
			return True
	return False		

def email(subject, message):
	msg = MIMEText(message)
	msg['Subject'] = subject
	msg['To'] = email_to
	msg['From'] = username_email
	server=smtplib.SMTP('smtp.office365.com', 587)
	server.starttls()
	server.login(username_email, password)
	server.sendmail(msg['From'], msg['To'], msg.as_string())
	server.quit()
#driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver')
with Browser('chrome', headless=False) as b:
	url = 'https://mystudentrecord.ucmerced.edu/pls/PROD/xhwschedule.P_SelectSubject'
	b.visit(url)
	b.find_by_name('subjcode').first.select(subj_category)
	b.find_by_name('openclasses').first.click()
	b.find_by_css('input[type=submit]').first.click()
	rows = b.find_by_css('table.datadisplaytable > tbody > tr')
	# first check if section2 (discussion/lab) is available.
	sec2found = True # this is default, in case there is no section 2 to add.
	if drop == True:
		sec2found == False
	for row in rows:
		if course_name in row.text and section2 in row.text and 'Closed' not in row.text:
			sec2found = True
			break
	#if section2 was found available, check if section1 is available, and if so, register.
	if sec2found == True:
		for row in rows:
			if course_name in row.text and section1 in row.text and 'Closed' not in row.text:
				register(b, section1, section2, drop, course_name_drop, section1_drop, section2_drop)
				if verify_registration(b, section1):
					email(email_subject, email_message)
					os.system('crontab -u ' + linux_user  + ' -l | grep -v "ucmregister" | crontab -u ' + linux_user + ' -')
				sys.exit()
	sys.exit()
