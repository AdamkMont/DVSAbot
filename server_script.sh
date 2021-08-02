#!/bin/sh

wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
sudo yum install ./google-chrome-stable_current_x86_64.rpm 
pip3 install selenium 
pip3 install boto3
pip3 install chromedriver-autoinstaller

wget https://github.com/AdamkMont/DVSAbot/blob/main/bot.py 
chmod 700 bot.py

#Create cronjob to execute bot every 10 mins
command='python3 bot.py'
job='*/10 * * * * $command'
cat <(fgrep -i -v "$command" <(crontab -l)) <(echo "$job") | crontab -

