#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# read 1-wire sensor
# in case of value exceeding alarm limit
# send email via smtp
# 2013-06-06 V0.1 by Thomas Hoeser
#
 
import sys
import smtplib
 
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
 
mail_server   = 'smtp.web.de'            # Mail Server
mail_account  = 'xxx.yyy@web.de'    # name of mail account
mail_password = 'secretpassword'            # password
addr_sender   = 'bill.gates@microsoft.de'    # sender email
addr_receiver = 'bill.gates@microsoft.de'    # receiver email
 
verbose_level = 2
debug_level   = 0
error_temp = -999
 
# dictionary with for 1-wire sensors: [sensor name] [1-Wire device]
sensor_dict = {    "Wohnzimmer": "28-00000487bb70",
                "Balkon"    : "28-00000487bb70",
                "Speicher"  : "28-000004be39a5"
                }
 
#---------------------------------------------------------------------------------------------
def read_sensor(Sensor):
 
    if verbose_level > 2:  
        print "1++++ read_sensor()"    
        print "sensor:" , Sensor
    if debug_level == 0:
        # get 1-Wire id from dictionary
        sensor_slave = str(sensor_dict.get(Sensor))
        # Open 1-wire slave file
        sensor_device = '/sys/bus/w1/devices/' + str(sensor_slave) + '/w1_slave'
        if verbose_level > 2:  
            print "open: ", sensor_device
        try:
            file = open(sensor_device)
            filecontent = file.read()                         # Read content from 1-wire slave file
            file.close()                                           # Close 1-wire slave file
            stringvalue = filecontent.split("\n")[1].split(" ")[9] # Extract temperature string
            if stringvalue[0].find("YES") > 0:
               temp = error_temp
            else:
               temp = float(stringvalue[2:]) / 1000            # Convert temperature value
            # temp=str(temp)
        except IOError:
            print "PANIC read_sensor - Cannot find file >" + sensor_slave + "< in /sys/bus/w1/devices/"
            print "No sensor attached"
            print "check with > cat /sys/devices/w1_bus_master1/w1_master_slaves"
            temp=("Sensor not attached")
    else:
        # this is dummy function generating a random number
        # ony used for testing purposes
        temp = random.randrange(-10, 30, 2) + 0.3
        # temp = Sensor + " " + str(temp)
 
    return(temp) # exit function read_sensor
 
# --------------------------------------------------------------------------------
def send_mail(title,message):
 
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = title
    msg['From'] = addr_sender
    msg['To'] = addr_receiver
 
    # Create the body of the message (a plain-text and an HTML version).
    text = message
 
    html = """\
<html>
  <head></head>
  <body>
    <h>
"""
 
    html += message
    html += """\
</h>
    <p> This is a service provided by raspberry</p>
  </body>
</html>
"""
    # print html
 
    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
 
    # Attach parts into message container.
    msg.attach(part1)
    msg.attach(part2)
 
    try:
        # Send the message via local SMTP server.
        mailsrv = smtplib.SMTP(mail_server)
        mailsrv.login(mail_account,mail_password)
        # sendmail function takes 3 arguments: sender's address, recipient's address and message to send - here it is sent as one string.
        mailsrv.sendmail(addr_receiver, addr_receiver, msg.as_string())
        mailsrv.quit()
        print "Successfully sent email"
    except:
        print "Error: unable to send email"
 
#---------------------------------------------------------------------------------------------    
if __name__ == "__main__":
 
   alarm_hi = 20.5        # upper alarm level
   alarm_lo = -10.5       # lowe alarm level
 
   cur_temp = read_sensor("Speicher")
   print cur_temp, alarm_hi, alarm_lo
 
   if cur_temp == error_temp:
      print "read error - CRC = NO"
   else:
      if (cur_temp > alarm_hi) or (cur_temp < alarm_lo):
         subject = "Alarm"
         message = "Die Temperatur betraegt: " + str(cur_temp)
         print subject, message
         send_mail(subject,message)
      else:
         print "o.k."
 
   sys.exit(0)

