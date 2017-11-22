# ucm_registration
Check a if a UC Merced course is available and register for it 


# How to install V2 or V2.1 on Raspberry Pi 
(Tested on RPI3 running Raspbian Stretch Lite W/ PIXEL Desktop Environment)

install python and python-pip
  sudo apt-get install python python-pip

install splinter
  sudo pip install splinter

install selenium
  sudo pip-install selenium

download the chromedriver that's compiled for armhf.
(The latest version did not work for me)
The one I used was: chromium-chromedriver 62.0.3202.89-0ubuntu0.14.04.1213 in armhf (Updates)
get it here:
https://launchpad.net/ubuntu/trusty/+package/chromium-chromedriver

Once downloaded, install by using this command:
  sudo dpkg -i /path/to/deb/file.db
then run
  sudo apt-get install chromium-chromedriver
It will install to this location: /usr/lib/chromium-browser/chromedriver, but we must move it.
  sudo mv /usr/lib/chromium-browser/chromedriver /usr/bin/chromedriver

Now you should be able to run the python file using
  python /path/to/python/file.py


# How to schedule this task:
you can make a bash script and use add the script to the cron table
first create a script that will run the python file, and optionally echo output to a log file.
  nano script.sh

add something like this:
  export DISPLAY=:0.0
  cd /path/to/your/python/directory
  echo "" >> ucmregister_log.txt
  echo "Time: $(date -Iseconds) | Start python script---" >> ucmregister_log.txt
  python check_course_availability_v2.1_with_webdrop.py #Or whatever you named it here
  echo "Time: $(date -Iseconds) | End python script---" >> ucmregister_log.txt

Then edit your crontab
  crontab -e
Make sure that at the top of your crontab, you have the following:
  SHELL=/bin/sh
  PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
and then add your task to repeat:
  * * * * *  /bin/bash /path/to/bash/script.sh
in order to test if it is running, you can either check your log that you created, or you can run the webdriver non-heaadless

