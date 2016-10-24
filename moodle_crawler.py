# -*- coding: utf-8 -*-
"""
Created on Sat Oct 22 14:41:55 2016

@author: Fabian
"""

import urllib
import http.cookiejar
import os
from getpass import getpass
from bs4 import BeautifulSoup
from configparser import ConfigParser


def implement_cookies():
    cookies = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookies))
    urllib.request.install_opener(opener)


def get_moodle_content(username, password):
    
    url = "http://buelearning.hkbu.edu.hk/login/index.php"
    payload = {
       'username': username,
       'password': password
       }
    print('Accessing Moodle')
    data = urllib.parse.urlencode(payload)
    binary_data = data.encode('utf-8') 
    req = urllib.request.Request(url, binary_data)
    response = urllib.request.urlopen(req)
    content = response.read()
    return content
    
def get_course_list(content):
    print('Getting a list of the courses')
    content = str(content)
    course_html = content.split('My courses</a><ul>')[1].split('</li></ul><ul class="dropdown')[0]
    course_list = course_html.split('<li class="clickable-with-children">')
    del course_list[0]
    courses = []
    for course_html in course_list:
        soup =  BeautifulSoup(course_html, "lxml")
        a = soup.find('a')
        course_title = a.get('title')
        course_text = a.text
        course_link = a.get('href')
        courses.append([course_title, course_text, course_link])
    return courses
    
def save_course_files(course):
    print("Downloading files for " + course[0] + "... \n")
    course_shorter = course[0][0:34]
    remove_wrong = str.maketrans(" ", "_", r"/\|:*?<>")
    course_shorter = course_shorter.translate(remove_wrong)
    directory = file_dir + "\\" + course_shorter
    if not os.path.isdir(directory):
        print("Creating dir for " + course[0])
        os.mkdir(directory)
    if not os.getcwd() == directory:
        os.chdir(directory)
    response2 = urllib.request.urlopen(course[2])
    data = response2.read()
    soup = BeautifulSoup(data, 'lxml')
    links = soup.find(class_="course-content").find_all('a')
    for link in links:
        href = link.get('href')
        if 'resource' in str(href):
            web_file = urllib.request.urlopen(href)
            file_name_enc = web_file.geturl().split('/')[-1].split('?')[0]
            file_name = urllib.parse.unquote(file_name_enc)
            if os.path.exists(file_name):
                print(file_name + " already exists")
                continue
            print("Downloading " + file_name)
            new_file = open(file_name, 'wb')
            new_file.write(web_file.read())
            web_file.close()
            new_file.close()
    os.chdir(file_dir)
    if not os.listdir(directory):
        os.rmdir(directory)
        print("Deleting dir for " + course[0])
    print("\n")


def get_user_data():
    if not os.path.exists('user_data.ini'):
        print('Please enter your moodle Username. This will be stored in an .ini file, so you won\'t have to enter it again.')
        username = input()
        print('Please enter your password')
        password = getpass()
        conf_file = open('user_data.ini', 'w')
        conf1 = ConfigParser()
        conf1.add_section('auth')
        conf1.set('auth', 'username', username)
        conf1.set('auth', 'password', password)
        conf1.write(conf_file)
        conf_file.close()   
        print('Your data have been saved into an .ini file next to this application')
    conf = ConfigParser()
    conf.read('user_data.ini')
    username = conf.get("auth", "username")
    password = conf.get("auth", "password")
    return username, password
    



implement_cookies()
username, password = get_user_data()
content = get_moodle_content(username, password)
courses = get_course_list(content)
file_dir = os.path.dirname(os.path.abspath(__file__))
print('Starting to download course files\n')
for course in courses:
    save_course_files(course)

          