# Centera Auto Auditor
# Version 1.7.0
# Version notes: Modern organization implemented for webserver

import re
import os
import subprocess
from datetime import datetime

timestamp = datetime.now()

datestamp = timestamp.strftime("%m-%d-%Y")
cMonth = timestamp.strftime("%B")
cYear = timestamp.strftime("%Y")
monthNum = timestamp.strftime("%m")
timestamp2 = str(timestamp)
timestamp2 = timestamp2[0:19]

# Console and auth
logDump = "ConsoleLog.txt"
auC = "Redacted"

# Output text files
todaysAdminLog = "Redacted/Automation/Centera/Human_Admin/" + cMonth + "/Human_Admins-" + datestamp
todaysNonAdminLog = "Redacted/Automation/Centera/Human_Non_Admin/" + cMonth + "/Human_Non_Admins-" + datestamp
todaysServiceLog = "Redacted/Automation/Centera/Service/" + cMonth + "/ServiceplusDefaults-" + datestamp


# Gather Auth
with open(auC, "r") as authFile:
    username = authFile.readline()
    password = authFile.readline()
    username = username.rstrip("\n")

# Open log
with open(logDump, "w") as console:
    def main(ip, altIP):

        def command(failed, failCounter, skip):
            if not failed:
                selectedIP = ip
            elif failed & failCounter == 1:
                selectedIP = altIP
            else:
                print("Alternate IP request failed. Logging this to output file and continuing.", file=console)
                with open(todaysAdminLog, "a") as log:
                    log.write(fullTitle + "\nthe request to the IP failed.\n")
                    log.close()
                with open(todaysNonAdminLog, "a") as log:
                    log.write(fullTitle + "\nthe request to the IP failed.\n")
                    log.close()
                with open(todaysServiceLog, "a") as log:
                    log.write(fullTitle + "\nthe request to the IP failed.\n")
                    log.close()
                skip = True
            if not skip:
                cmdOne = subprocess.Popen(
                    ['java', '-cp', 'E:/Program Files (x86)/EMC/Centera/4_3/GlobalServices/lib/CenteraViewer.jar',
                     'com.filepool.remote.cli.CLI', '-U', username, '-P', password, '-IP', str(selectedIP),
                     '-script', 'Redactedpath'],
                    stdout=subprocess.PIPE)
                stdout, sterr = cmdOne.communicate()
                stdout = stdout.decode("utf-8")
                stdout = stdout.replace("\r", "")
                global stdoutG
                stdoutG = stdout
            else:
                stdoutG = "Empty. Request failed."

        # Set defaults and begin running command
        failed = False
        failCounter = 0
        global failedTotal
        failedTotal = 0
        skip = False
        command(failed, failCounter, skip)

        regexConnectionStatus = re.search("Could not connect", stdoutG)
        if regexConnectionStatus:
            with open(logDump, "a") as console:
                print("Connection to " + ip + " failed. Trying alt...", file=console)
            failed = True
            failCounter += 1
            command(failed, failCounter, skip)
        else:
            with open(logDump, "a") as console:
                print("Finished request evaluation for " + fullTitle, file=console)
            if skip:
                failedTotal += failedTotal
                print("Skip = " + str(skip))
            else:
                with open(logDump, "a") as console:
                    print("Skip = " + str(skip), file=console)

        # Filters for account types
        # Human Admins
        regexEntrySearch = re.findall("[dD][tT][0-9]{6}.+Data Access, Management|"  # Default admin account is only
                                      "[dD][tT][0-9]{5}.+Data Access, Management|"  # management, therefore we can
                                      "[dD][tT][0-9]{6}[^,]+Management|"            # assume management qualifies as
                                      "[dD][tT][0-9]{5}[^,]+Management", stdoutG)   # admin.

        # Human Non-Admins
        regexnonadmin = re.findall("[dD][tT][0-9]{6}.+Data Access|[dD][tT][0-9]{5}.+Data Access", stdoutG)

        # Non Human Accounts
        regexLineSearch = re.findall(
            "(?!\t)([\w 0-9\-]+Data Access, Management|[\w 0-9\-]+Management|[\w 0-9\-]+Data Access)", stdoutG)

        # print(stdoutG)

        # File headers
        if str(ip) == "(IP ADDRESS)":
            # Human Admins
            with open(todaysAdminLog, "w") as clear:
                clear.write("Centera Admin Account Audit\n" + "Collected on: " + str(timestamp2) + "\n")
            clear.close()
            # Human Non Admin
            with open(todaysNonAdminLog, "w") as clear:
                clear.write("Centera Human Non-Admin Audit\n" + "Collected on: " + str(timestamp2) + "\n")
            clear.close()
            # Service/Built-in Etc.
            with open(todaysServiceLog, "w") as clear:
                clear.write("Centera Service/Built-in Audit\n" + "Collected on: " + str(timestamp2) + "\n")
            clear.close()


        with open(todaysAdminLog, "a") as table:
            table.write("\n\n" + fullTitle)
            table.write("\nProfile Name              Home Pool       Enabled  Configured Usage\n"
                        "-----------------------------------------------------------------------------\n")
            for i in regexEntrySearch:
                table.write(i + "\n")
            table.close()

        with open(todaysNonAdminLog, "a") as table:
            table.write("\n\n" + fullTitle)
            table.write("\nProfile Name              Home Pool       Enabled  Configured Usage\n"
                        "-----------------------------------------------------------------------------\n")
            for i in regexnonadmin:
                table.write(i + "\n")
            table.close()

        with open(todaysServiceLog, "a") as table2:
            table2.write("\n\n" + fullTitle)
            table2.write("\nProfile Name              Home Pool       Enabled  Configured Usage\n"
                         "-----------------------------------------------------------------------------\n")
            for i in regexLineSearch:
                regexDTEval = re.match("[dD][tT][0-9]{6}|[dD][tT][0-9]{5}", i)
                if regexDTEval:
                    pass
                else:
                    table2.write(i + "\n")
            table2.close()


    IPList = {
        "Centera - 1 RC": "(IP ADDRESS)",  # 1
        "Centera - 2 RC": "(IP ADDRESS)",  # 2
        "Centera - EFS RC": "(IP ADDRESS)",  # 3
        "Centera - 1 WC": "(IP ADDRESS)",  # 4
        "Centera - 2 WC": "(IP ADDRESS)",  # 5
        "Centera - 3 WC": "(IP ADDRESS)",  # 6
        "Centera - 5 WC": "(IP ADDRESS)",  # 7
        "Centera - EFS WC": "(IP ADDRESS)",  # 8
        "Centera - 1 PD": "(IP ADDRESS)",  # 9
        "Centera - 2 PD": "(IP ADDRESS)",  # 10
        "Centera - 3 PD": "(IP ADDRESS)",  # 11
        "Centera - 5 PD": "(IP ADDRESS)",  # 12
        "Centera - Dev": "(IP ADDRESS)",  # 13
        "Centera - Adelaide": "(IP ADDRESS)",  # 14
        "Centera - Markham": "(IP ADDRESS)",  # 15
        "Centera - Dan Road (BFDS)": "(IP ADDRESS)",  # 16
        "Centera - Crown Colony (BFDS)": "(IP ADDRESS)"  # 17
    }

    IPListalt = ['(IP ADDRESS)', '(IP ADDRESS)', '(IP ADDRESS)', '(IP ADDRESS)', '(IP ADDRESS)',
                 '(IP ADDRESS)',
                 '(IP ADDRESS)', '(IP ADDRESS)', '(IP ADDRESS)', '(IP ADDRESS)', '(IP ADDRESS)',
                 '(IP ADDRESS)',
                 '(IP ADDRESS)', '(IP ADDRESS)', '(IP ADDRESS)', '(IP ADDRESS)', '(IP ADDRESS)']
    indexTracker = 0

if __name__ == '__main__':
    for key, val in IPList.items():
        ip = val
        fullTitle = key + "   IP: " + ip

        altIP = IPListalt[indexTracker]
        main(ip, altIP)
