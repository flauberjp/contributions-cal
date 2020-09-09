#!/usr/bin/env python3

import http.server
import re, requests
from urllib.parse import unquote, parse_qs
import os
import threading
from socketserver import ThreadingMixIn
from os import environ
from time import gmtime, strftime
import subprocess
from sys import argv
from os import environ
import simplejson

try:
    import git
    if git.__version__ < '0.3.1':
        raise ImportError("Your version of git is %s. Upgrade to 0.3.1 or better." % git.__version__)
    have_git = True
except ImportError as e:
    have_git = False
    GIT_MISSING = 'Requires gitpython module, but not installed or incompatible version: %s' % e

print('Working directory (initial): ')
initialWorkingDirectory = os.getcwd()
print(initialWorkingDirectory)

print('git help -a')
print('\n' + subprocess.check_output('git help -a', 
        shell=True).decode())

print('\n' + subprocess.check_output('git --version', 
        shell=True).decode())

main_page_content = '''
<html>  
  <body>
    {content}
  </body>
</html>
'''

my_name = os.environ.get('my_name', 'undefined')
my_user = os.environ.get('my_user', 'undefined')
my_email = os.environ.get('my_email', 'undefined')
my_password = os.environ.get('my_password', 'undefined')

print(
    'my_user: ' + my_user + '\n' + 
    'my_email: ' + my_email + '\n' + 
    'my_password: ' + my_password + '\n')

print('git config --global user.name \"' + my_name + '\"')
print('\n' + subprocess.check_output('git config --global user.name \"' + my_name + '\"', 
        shell=True).decode())

print('git config --global user.email ' + my_email)
print('\n' + subprocess.check_output('git config --global user.email ' + my_email, 
        shell=True).decode())


print('git config --global credential.helper cache')
print('\n' + subprocess.check_output('git config --global credential.helper cache', 
        shell=True).decode())

print('printf \'protocol=https\\nhost=github.com\\nusername=' + my_user + '\\npassword=' + my_password + '\\n\' | git credential approve')
print('\n' + subprocess.check_output('printf \'protocol=https\\nhost=github.com\\nusername=' + my_user + '\\npassword=' + my_password + '\\n\' | git credential approve', 
        shell=True).decode())

repository_url = 'https://github.com/' + my_user + '/contributions-cal'
local_repository_name = repository_url.rsplit('/', 1)[-1]
file_of_evidences = 'index.html'

print('To perform git clone or git fetch and git pull...')
if (os.path.exists(local_repository_name) == False):
    print('git clone ' + repository_url)
    print(subprocess.check_output('git clone ' + repository_url, 
        shell=True).decode())
else:
    print('git fetch ' + repository_url)
    print(subprocess.check_output('git fetch ' + repository_url, 
        shell=True).decode())
    print('git pull ' + repository_url)
    print(subprocess.check_output('git pull ' + repository_url, 
        shell=True).decode())

nextCurrentDirectory = initialWorkingDirectory + '/' +  local_repository_name
if os.name == 'nt':
    nextCurrentDirectory = nextCurrentDirectory.replace('/', '\\') 
print('Changing current directory from ' + initialWorkingDirectory + ' to ' + nextCurrentDirectory)
os.chdir(nextCurrentDirectory)
print('Working directory: ')
cwd = os.getcwd()
print(cwd)

print('git remote -v')
print(subprocess.check_output('git remote -v', shell=True).decode())    

print('Checking existence of \"' + file_of_evidences + '\"...')

if(os.path.exists(file_of_evidences) == False):
    print('FILE DOES NOT EXIST. Creating...') 
    with open(file_of_evidences, 'w'): 
        pass
else:
    print('FILE EXIST')

file_of_evidences_fullPath = '/' +  file_of_evidences
if os.name == 'nt':
    file_of_evidences_fullPath = os.getcwd() + file_of_evidences_fullPath.replace('/', '\\') 
else: 
    file_of_evidences_fullPath = os.getcwd() + file_of_evidences_fullPath 
print('Full path: \"' + file_of_evidences_fullPath + '\"...')

class ThreadHTTPServer(ThreadingMixIn, http.server.HTTPServer):
    "This is an HTTPServer that supports thread-based concurrency."

class Shortener(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        request_path = self.path
        
        print("\n----- Request Start ----->\n")
        print(request_path)
        request_headers = self.headers
        print(request_headers)
        self.data_string = self.rfile.read(int(self.headers['Content-Length']))
        resp_parsed = re.sub(r'^jsonp\d+\(|\)\s+$', '', self.data_string.decode("utf-8"))
        data = simplejson.loads(resp_parsed)
        print(data)
        print("<----- Request End -----\n")

        repository_type = ''
        if 'request' in self.path:
            if('gitlab' in request_headers.as_string().lower()):
                repository_type = 'Gitlab'
                print('The header contain gitlab, so we assume the request is comming from gitlab...')
                author = data['user_username']
                print("Author: {}".format(author))
                hash = data['commits'][0]['id'][0:6] 
                print("Hash: {}".format(hash))
                summary = data['commits'][0]['message'].rstrip()[0:6] + '...'
                print("Summary: {}".format(summary))
            elif('git-event' in request_headers.as_string().lower()):
                repository_type = 'Local Git'
                print('The header contain git-event, so we assume the request is comming from local git...')
                author = data['author']
                print("Author: {}".format(author))
                hash = data['hash'] 
                print("Hash: {}".format(hash))
                summary = data['summary'].rstrip()[0:6] + '...'
                print("Summary: {}".format(summary))
            else:
                repository_type = 'Bitbucket'
                print('The header does NOT contain gitlab, so we assume the request is comming from github...')
                author = data['push']['changes'][0]['new']['target']['author']['user']['username']
                print("Author: {}".format(author))
                hash = data['push']['changes'][0]['new']['target']['hash'][0:6] 
                print("Hash: {}".format(hash))
                summary = data['push']['changes'][0]['new']['target']['message'].rstrip()[0:6] + '...'
                print("Summary: {}".format(summary))

            print("my_user: \"" + my_user.rstrip() + "\"; author: \"" + author.rstrip() + "\"")
            if ( my_user.rstrip() != author.rstrip()):
                print("Disconsidering this change as it was not done by me this time!")
            else:
                repo = git.Repo(".") 
                print("Location "+ repo.working_tree_dir)
                print("Remote: " + repo.remote("origin").url)

                the_date = strftime("%Y-%m-%d", gmtime())
                the_time = strftime("%H:%M:%S", gmtime())

                commit_message = the_date + ' ' + the_time + ' ' + hash + ' ' + summary

                ##
                with open(file_of_evidences_fullPath, "r") as in_file:
                    buf = in_file.readlines()

                with open(file_of_evidences_fullPath, "w") as out_file:
                    for line in buf:
                        if line.strip() == "<tbody>":
                            newContent = "\
                                <tr> \
                                    <td>\
                                        " + the_date + " " + the_time + "\
                                    </td>\
                                    <td>\
                                        " + hash  + " " +  summary + "\
                                    </td>\
                                    <td class=\"" + repository_type + "\">\
                                        " + repository_type + "\
                                    </td>\
                                </tr>\
                                "
                            line = line + newContent
                        out_file.write(line)
                ##

                index = repo.index
                index.add([repo.working_tree_dir + '/*'])
                new_commit = index.commit(commit_message)
                origin = repo.remotes.origin
                origin.push()

        fileName = file_of_evidences_fullPath
            
        f = open(fileName, 'rb') #open requested file  

        #send code 200 response  
        self.send_response(200)  

        #send header first  
        self.send_header('Content-type','text-html')  
        self.end_headers()  

        #send file content to client
        textToBeSent = main_page_content.format(content=f.read().decode("utf-8"))
        #print(textToBeSent)
        self.wfile.write(textToBeSent.encode())
        f.close()  
        return  


    def do_GET(self):
        request_path = self.path        
        print("\n----- Request Start ----->\n")
        print(request_path)
        print(self.headers)
        print("<----- Request End -----\n")

        if 'request' in self.path:
            if not have_git:
                print(GIT_MISSING)
            else:
                repo = git.Repo(".") 
                print("Location "+ repo.working_tree_dir)
                print("Remote: " + repo.remote("origin").url)


                commit_message = strftime("%Y-%m-%d %H:%M:%S", gmtime())

                lastPartOfThePath = self.path.rsplit('/', 1)[-1]
                if(lastPartOfThePath != 'request'):
                    commit_message += ' ' + lastPartOfThePath

                with open(file_of_evidences_fullPath, 'r+') as f:
                    content = f.read()
                    f.seek(0, 0)
                    f.write(commit_message + '<BR>' + content)
                    f.close()

                index = repo.index
                index.add([repo.working_tree_dir + '/*'])
                new_commit = index.commit(commit_message)
                origin = repo.remotes.origin
                origin.push()

        fileName = file_of_evidences_fullPath
        if (self.path.endswith('.html')):
            if os.name == 'nt':
                fileNameTemp = os.getcwd() + self.path.replace('/', '\\') 
            else: 
                fileNameTemp = os.getcwd() + self.path  
            print(fileName)
            if (os.path.exists(fileNameTemp) == False):
                print('\"' + fileName + '\" file not exist')
            else:
                fileName = fileNameTemp
                print('\"' + fileName + '\" file exist')
            
        f = open(fileName, 'rb') #open requested file  

        #send code 200 response  
        self.send_response(200)  

        #send header first  
        self.send_header('Content-type','text-html')  
        self.end_headers()  

        #send file content to client
        textToBeSent = main_page_content.format(content=f.read().decode("utf-8"))
        #print(textToBeSent)
        self.wfile.write(textToBeSent.encode())
        f.close()  
        return  


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8001))   # Use PORT if it's there.
    server_address = ('', port)
    httpd = ThreadHTTPServer(server_address, Shortener)
    httpd.serve_forever()
