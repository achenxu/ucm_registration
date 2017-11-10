from splinter import Browser
from email.mime.text import MIMEText
import smtplib, time, sys

username = '<username>'
password = '<password>'
linux_user = '<linux_user>'

course_name = '<course_name>'
section1 = '<section_of_course_to_register_for>'
section2 = '<section_of_course_to_register_for>'

username_email = username + '@ucmerced.edu'
email_to = '<destination_email_here>'
email_from = username_email

email_subject = 'Registered for ' + course_name + '!'
email_message = 'Registered for ' + course_name + '!'

def register(b, section1, section2):
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
    # Register
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

with Browser('chrome', headless=True) as b:
	url = 'https://mystudentrecord.ucmerced.edu/pls/PROD/xhwschedule.P_SelectSubject'
	b.visit(url)
	b.find_by_name('subjcode').first.select('CSE')
	b.find_by_name('openclasses')[1].click()
	b.find_by_css('input[type=submit]').first.click()
	rows = b.find_by_css('table.datadisplaytable > tbody > tr')
	for row in rows:
		if course_name in row.text and section2 in row.text and 'Closed' not in row.text:
			register(b, section1, section2)
			if verify_registration(b, section1):
				email(email_subject, email_message)
				os.system('crontab -u ' + linux_user  + ' -l | grep -v "check_course_availability" | crontab -u ' + linux_user + ' -')
			sys.exit()
