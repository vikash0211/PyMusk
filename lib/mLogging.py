import datetime
import os
import re
import threading
import smtplib

from mTest import get_duration
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

class logging:

    def __init__(self, logs_dir):

        self.logs_dir = logs_dir
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)

        timestamp = str(datetime.datetime.now())[:-7]
        timestamp = '_'.join(timestamp.split(' '))
        timestamp = '-'.join(timestamp.split(':'))
        self.log_file = os.path.join(self.logs_dir, r'log_{}.log'.format(timestamp))
        self.fh = open(self.log_file, 'w')

    def get_NewLogFile(self):

        logfile = None
        timestamp = str(datetime.datetime.now())[:-7]
        timestamp = '_'.join(timestamp.split(' '))
        timestamp = '-'.join(timestamp.split(':'))
        logfile = os.path.join(self.logs_dir, r'log_{}.log'.format(timestamp))
        return logfile

    def info(self, message, f = None, To_Screen = True):

        t = (str(datetime.datetime.now()))[:-7]
        print_str = '{} | {}'.format(t, threading.currentThread().name)
        print_str = '{} | {}'.format(print_str, f) if f else print_str
        print_str = '{} | INFO: {}'.format(print_str, message)
        self.fh.write('{}\n'.format(print_str))
        self.fh.flush()
        if To_Screen:
            print(print_str)

    def error(self, message, f = None, To_Screen = True):

        t = (str(datetime.datetime.now()))[:-7]
        print_str = '{} | {}'.format(t, threading.currentThread().name)
        print_str = '{} | {}'.format(print_str, f) if f else print_str
        print_str = '{} | ERROR: {}'.format(print_str, message)
        self.fh.write('{}\n'.format(print_str))
        self.fh.flush()
        if To_Screen:
            print(print_str)

    def warning(self, message, f =  None, To_Screen = True):

        t = (str(datetime.datetime.now()))[:-7]
        print_str = '{} | {}'.format(t, threading.currentThread().name)
        print_str = '{} | {}'.format(print_str, f) if f else print_str
        print_str = '{} | WARNING: {}'.format(print_str, message)
        self.fh.write('{}\n'.format(print_str))
        self.fh.flush
        if To_Screen:
            print(print_str)

    def debug(self, message, f = None, To_Screen = True):

        t = (str(datetime.datetime.now()))[:-7]
        print_str = '{} | {}'.format(t, threading.currentThread().name)
        print_str = '{} | {}'.format(print_str, f) if f else print_str
        print_str = '{} | DEBUG: {}'.format(print_str, message)
        self.fh.write('{}\n'.format(print_str))
        self.fh.flush()
        if To_Screen:
            print(print_str)


    def __del__(self):

        self.fh.close()


class smartLogging:

    def __init__(self, log):

        self.logs_dir = log.logs_dir
        self.log_file = log.log_file
        self.smartLogsDir = '.'.join(self.log_file.split('.')[:-1])
        os.mkdir(self.smartLogsDir)

        self.taskStartPattern = r'<Start Task id=(\d+) name=(.*?) time=(.*)>'
        self.taskEndPattern = r'<End Task id=(\d+) result=(PASS|FAIL|BLOCKED) runtime=(.*)>'
        self.testStartPattern = r'<Start Test name=(\w+)>'
        self.testEndPattern = r'<End Test name=(\w+) result=(PASS|FAIL|BLOCKED) runtime=(.*)>'
        self.subtestStartPattern = r'<Start Subtest name=(\w+)>'
        self.subtestEndPattern = r'<End Subtest name=(\w+) result=(PASS|FAIL|BLOCKED) runtime=(.*)>'

        self.colorDict = {'PASS':'#1f7a27', 'FAIL':'#FF0000', 'BLOCKED':'#FFA500'}

    def createSmartLogs(self, job):

        homeFile = os.path.join(self.smartLogsDir, 'home.html')
        fw = open(homeFile, 'w')

        self.user = job['user']
        self.startTime = str(job['startTime'])[:-7]
        self.endTime = str(job['endTime'])[:-7]
        self.runTime = get_duration(job['startTime'], job['endTime'])
        jobName = os.path.split(job['file'])[1]
        self.jobName = jobName.split('.')[0]

        htmldata = """
<html>

    <head>
        <title>{1}</title>
            <meta name = "description" content = "Test Logs" />
            <meta name = "author" content = "Vikash Saini" />
            <meta http-equiv = "Content-Type" content = "text/html; charset = UTF-8" />
    </head>

    <body id="body" style="font-family:calibri">
    <table id="summarry" class="contentTable" cellspacing="0" cellpadding="0" border="0" width="25%">
    <tbody>
    <tr>
    <td>Submitter </td>
    <td>{0}</td>
    </tr>
    <tr>
    <td>Job </td>
    <td>{1}</td>
    </tr>
    <tr>
    <td>Job Start Time</td>
    <td>{2}</td>
    </tr>
    <tr>
    <td>Job Complete Time</td>
    <td>{3}</td>
    </tr>
    <tr>
    <td>Job Duration</td>
    <td>{4}</td>
    </tr>
    </tbody>
    </table>

    <h2>
        <center>Test Results</center>
    </h2>
    <hr />
    """.format(self.user, self.jobName, self.startTime, self.endTime, self.runTime)

        htmldata = htmldata + """
    <style type="text/css">
        table {
            margin-left: auto ;
            margin-right: auto ;
        }
    </style>

    <table id="results" class="contentTable" cellspacing="0" cellpadding="2" border="0" width="50%">
        <thead>
            <tr>
                <th align="left"> Task/Test/Sub Test </th>
                <th align="left"> Result </th>
                <th align="right"> Run Time </th>
            </tr>
        </thead>
        <tbody>
        """
        fw.write('{}\n'.format(htmldata))
        self.createLogs(fw)

        htmldata = """
        </tbody>
        </table>
        <hr />
    </body>
</html>
"""
        fw.write('{}\n'.format(htmldata))
        fw.close()
        return homeFile

    def createLogs(self, fw):

        fr = open(self.log_file, 'r')
        readTaskLog = -1
        taskData = {}
        taskData['logs'] = []
        lineNo = 0
        taskLog = ''
        for line in fr:
            lineNo += 1
            match = re.search(self.taskStartPattern, line)
            if match:
                readTaskLog = 1
                taskData['id'] = match.group(1)
                taskData['name'] = match.group(2)
                taskData['startTime'] = match.group(3)

            match = re.search(self.taskEndPattern, line)
            if match:
                if taskData['id'] == match.group(1):
                    readTaskLog = 0
                    taskLog = 'task_{}.html'.format(taskData['id'])
                    taskData['result'] = match.group(2)
                    taskData['duration'] = match.group(3)
                    #color = self.colorDict[taskData['result']]
                    fw.write('<tr>\n')
                    fw.write('<td align="left"><a href = "{}">Task {}: {}</a></td>\n'.format(taskLog, taskData['id'], taskData['name']))
                    #fw.write('<td align="left"><span style="color:{};">{}</span></td>\n'.format(color, taskData['result']))
                    fw.write('<td></td>\n')
                    fw.write('<td align="right"><span>{}</span></td>\n'.format(taskData['duration']))
                    fw.write('</tr>\n')
                else:
                    raise Exception('Inconsistensy in logs at line No. {}'.format(lineNo))

            if readTaskLog == 1:
                taskData['logs'].append(line)

            if readTaskLog == 0:
                self.createTaskLogs(taskData)
                self.createTestRow(taskData['logs'], fw, taskLog)
                taskData['logs'] = []

        fr.close()

    def createTaskLogs(self, taskData):

        from pyMusk import Data
        logLineNo = 0
        logFile = os.path.join(self.smartLogsDir, 'task_{}.html'.format(taskData['id']))
        fw = open(logFile, 'w')

        prev = next = '#'
        if  1 < int(taskData['id']) < Data.job_dict['taskCount']:
            prev = 'task_{}.html'.format(int(taskData['id'])-1)
            next = 'task_{}.html'.format(int(taskData['id'])+1)
        elif 1 < int(taskData['id']):
            prev = 'task_{}.html'.format(int(taskData['id'])-1)
        elif int(taskData['id']) < Data.job_dict['taskCount']:
            next = 'task_{}.html'.format(int(taskData['id'])+1)

        htmldata = """
<!doctype html>
<html lang="en">

    <head>
        <title>{2}.Task {0}</title>
            <meta name = "description" content = "Test Logs" />
            <meta name = "author" content = "Vikash Saini" />
            <meta http-equiv = "Content-Type" content = "text/html; charset = UTF-8" />
    </head>

    <body id="scrolly" style="font-family:calibri">

        <table id="home" class="contentTable" cellspacing="0" cellpadding="0" border="0" width="20%">
        <tbody>
        <tr>
        <td style="text-align:center"><a href = "{6}" >PREV</a></td>
        <td style="text-align:center"><a href = "home.html" >HOME</a></td>
        <td style="text-align:center"><a href = "{7}" >NEXT</a></td>
        </tr>
        </tbody>
        </table>
        <br />

        <table id="summarry" class="contentTable" cellspacing="0" cellpadding="0" border="0" width="20%">
        <tbody>
        <tr>
        <td>Submitter </td>
        <td>{1}</td>
        </tr>
        <tr>
        <td>Job </td>
        <td>{2}</td>
        </tr>
        <tr>
        <td>Job Start Time</td>
        <td>{3}</td>
        </tr>
        <tr>
        <td>Job Complete Time</td>
        <td>{4}</td>
        </tr>
        <tr>
        <td>Job Duration</td>
        <td>{5}</td>
        </tr>
        </tbody>
        </table>

        <h2>
            <center>Task {0} - {8}</center>
        </h2>
        <hr />
        <br />
        <div id="task_{0}">
        """.format(taskData['id'], self.user, self.jobName, self.startTime, self.endTime, self.runTime, prev, next, taskData['name'])
        htmldata += """
        <style type="text/css">
            table {
                margin-left: auto ;
                margin-right: auto ;
            }
            #scrolly{
                overflow-y: auto;
                white-space: nowrap;
            }
        </style>
        """
        fw.write('{}\n'.format(htmldata))

        # Read logfile and put it in html log
        testId = ''
        subtestId = ''

        color = '#000000'
        for line in taskData['logs']:
            line = line.rstrip()
            if re.search(r'^<.*>$', line):
                match = re.search(self.taskStartPattern, line)
                if match:
                    continue
                match = re.search(self.taskEndPattern, line)
                if match:
                    continue

                match = re.search(self.testStartPattern, line)
                if match:
                    testId = match.group(1).lower()
                    fw.write('<div id="{}">\n'.format(testId))
                    fw.write('<h3 style="font-size:20px;">{}</h3>\n'.format(match.group(1)))
                    continue

                match = re.search(self.testEndPattern, line)
                if match:
                    if testId == match.group(1).lower():
                        fw.write('</div>\n')
                    else:
                        raise Exception('Inconsistensy in logs at line: {}'.format(line))
                    continue

                match = re.search(self.subtestStartPattern, line)
                if match:
                    subtestId = '{}_{}'.format(testId, match.group(1).lower())
                    fw.write('<h4 id="{}" style="font-size:17px;">{}</h4>\n'.format(subtestId, match.group(1)))
                    fw.write('<div style="height:690px;width:100%;border:1px solid #515953;overflow-x:auto;overflow-y:auto;background-color:#eafff0;">\n')
                    fw.write('<p style="line-height:110%;font-size:15px;white-space: pre;">\n')
                    continue

                match = re.search(self.subtestEndPattern, line)
                if match:
                    if subtestId == '{}_{}'.format(testId, match.group(1).lower()):
                        fw.write('</p>\n')
                        fw.write('</div>\n')
                    else:
                        raise Exception('Inconsistensy in logs at line: {}'.format(line))
                    continue

            match = re.search(r'^Result: (\w+)$', line)
            if match:
                res = match.group(1)
                fw.write('\n<span style="background-color:{};font-weight:bold";>Result: {}</span>\n'.format(self.colorDict[res], res))
                continue

            line = line.replace('<', '&lt;')
            line = line.replace('>', '&gt;')

            if 'INFO' in line:
                color = '#000000'
            elif 'DEBUG' in line:
                color = '#07acff'
            elif 'ERROR' in line:
                color = '#FF0000'
            elif 'WARNING' in line:
                color = '#FFA500'
            else:
                fw.write('<span style="color:{};">{}</span>\n'.format(color, line))
                continue

            logLineNo += 1
            fw.write('<span style="color:{};">{} | {}</span>\n'.format(color, logLineNo, line))

        htmldata = """
        </div>
        <br />
        <hr />

        <table id="home" class="contentTable" cellspacing="0" cellpadding="0" border="0" width="20%">
        <tbody>
        <tr>
        <td style="text-align:center"><a href = "{0}" >PREV</a></td>
        <td style="text-align:center"><a href = "home.html" >HOME</a></td>
        <td style="text-align:center"><a href = "{1}" >NEXT</a></td>
        </tr>
        </tbody>
        </table>
    </body>
</html>
""".format(prev, next)
        fw.write('{}\n'.format(htmldata))
        fw.close()

    def createTestRow(self, taskLogs, fw, taskLog):

        readTestLog = -1
        testData = {}
        testData['logs'] = []
        testId = ''
        lineNo = 0
        for line in taskLogs:
            lineNo += 1
            match = re.search(self.testStartPattern, line)
            if match:
                readTestLog = 1
                testData['id'] = match.group(1)

            match = re.search(self.testEndPattern, line)
            if match:
                if testData['id'] == match.group(1):
                    readTestLog = 0
                    testData['result'] = match.group(2)
                    testData['duration'] = match.group(3)
                    testId = testData['id'].lower()
                    url = '{}#{}'.format(taskLog, testId)
                    color = self.colorDict[testData['result']]
                    fw.write('<tr>\n')
                    fw.write('<td align="left"><a href = "{}" style="margin-left: 20px">{}</a></td>\n'.format(url, testData['id']))
                    fw.write('<td align="left"><span style="color:{}; margin-left: 20px;">{}</span></td>\n'.format(color, testData['result']))
                    fw.write('<td align="right"><span>{}</span></td>\n'.format(testData['duration']))
                    fw.write('</tr>\n')
                else:
                    raise Exception('Inconsistensy in logs at line No. {}'.format(lineNo))

            if readTestLog == 1:
                testData['logs'].append(line)

            if readTestLog == 0:
                self.createSubTestRow(testData['logs'], fw, taskLog, testId)
                testData['logs'] = []

    def createSubTestRow(self, testLogs, fw, taskLog, pTestId):

        readTestLog = -1
        testData = {}
        testData['logs'] = []
        lineNo = 0
        testId = ''
        for line in testLogs:
            lineNo += 1
            match = re.search(self.subtestStartPattern, line)
            if match:
                readTestLog = 1
                testData['id'] = match.group(1)

            match = re.search(self.subtestEndPattern, line)
            if match:
                if testData['id'] == match.group(1):
                    readTestLog = 0
                    testData['result'] = match.group(2)
                    testData['duration'] = match.group(3)
                    testId = '{}_{}'.format(pTestId, testData['id'].lower())
                    url = '{}#{}'.format(taskLog, testId)
                    color = self.colorDict[testData['result']]
                    fw.write('<tr>\n')
                    fw.write('<td align="left"><a href = "{}" style="margin-left: 40px">{}</a></td>\n'.format(url, testData['id']))
                    fw.write('<td align="left"><span style="color:{}; margin-left: 40px;">{}</span></td>\n'.format(color, testData['result']))
                    fw.write('<td align="right"><span>{}</span></td>\n'.format(testData['duration']))
                    fw.write('</tr>\n')
                else:
                    raise Exception('Inconsistensy in logs at line No. {}'.format(lineNo))

            if readTestLog == 1:
                testData['logs'].append(line)

            if readTestLog == 0:
                #self.createSubTestLogs(testData['logs'])
                testData['logs'] = []


    def __del__(self):
        pass


def getReport():

    from pyMusk import Data
    smartLogs = smartLogging(Data.logger)
    link = smartLogs.createSmartLogs(Data.job_dict)
    link = link.replace('\\', '/')
    #link = 'file:///" + link
    link = 'http://{}{}{}'.format(os.uname()[1], Data.config['localhost']['domain'], link)
    print(link)

    # Send Mail
    print('Sending Mail... DONE')
    jobfile = os.path.split(Data.job_dict['file'])[1]
    jobfile = jobfile.split('.')[0]
    smtp = Data.config['smtp']
    subject = 'pyMusk Report:- job: {0}, by: {1}, Total: {2}(P:{3} F:{4})'.format(
                jobfile,
                Data.job_dict['user'],
                Data.job_dict['testCount'],
                Data.job_dict['passCount'],
                Data.job_dict['failCount']
            )
    content = []
    content.append('Report: {}'.format(link))
    content.append('')
    content.append('Report Summary:')
    content.append('\tSubmitter\t\t:{:>30}'.format(Data.job_dict['user']))
    content.append('\tJob\t\t\t:{:>30}'.format(jobfile))
    content.append('\tStart Time\t\t:{:>30}'.format(str(Data.job_dict['startTime'])[:-7]))
    content.append('\tEnd Time\t\t:{:>30}'.format(str(Data.job_dict['endTime'])[:-7]))
    content.append('\tTest Duration\t\t:{:>30}'.format(get_duration(Data.job_dict['startTime'], Data.job_dict['endTime'])))
    content.append('\tTotal Test Cases\t\t:{:>30}'.format(Data.job_dict['testCount']))
    content.append('\tPass\t\t\t:{:>30}'.format(Data.job_dict['passCount']))
    content.append('\tFail\t\t\t:{:>30}'.format(Data.job_dict['failCount']))
    content.append('\tBlocked\t\t\t:{:>30}'.format(Data.job_dict['otherCount']))
    content = '\n'.join(content)

    mail = Mail(smtp, subject, content)
    mail_from = Data.config['sender_email']
    mail_to = Data.config['receipients']
    mail.send_mail(mail_from, mail_to)


class Mail:

    def __init__(self, smtp, subject = None, content = None, attachments = None):

        self.smtp_server = smtp['ip']
        self.subject = subject
        self.content = content
        self.attachments = attachments

        if not subject:
            self.subject = 'Test Mail'

        if not content:
            self.content = """
            Test Mail

            """

    def send_mail(self, mailFrom, mailTo = []):

        COMMASPACE = ', '

        # Create a text/plain message
        mail = MIMEText(self.content)

        if not mailTo:
            print('Error: No reciepients')
            return -1

        # Create the container (outer) email message.
        mail = MIMEMultipart()
        mail['Subject'] = self.subject
        mail['From'] = mailFrom
        mail['To'] = COMMASPACE.join(mailTo)
        mail.attach(MIMEText(self.content))
        #mail.preamble = ''

        # Attachments
        if self.attachments:
            if 'str' in str(type(self.attachments)):
                with open(self.attachments, 'rb') as fp:
                    file = MIMEApplication(fp.read())
                mail.attach(file)

            elif 'list' in str(type(self.attachments)):
                for attachment in self.attachments:
                    with open(attachment, 'rb') as fp:
                        file = MIMEApplication(fp.read())
                    mail.attach(file)

        # Send the email via our own SMTP server.
        s = smtplib.SMTP(self.smtp_server)
        s.sendmail(mailFrom, mailTo, mail.as_string())
        s.quit()

