import requests
from bs4 import BeautifulSoup
from csv import writer
import re
import json

from selenium import webdriver      #this version of chromedriver.exe supports Chrome v83
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select


## index: index of the subject in the list
## lower_limit: minimum course number returned
## upper_limit: maximum course number returned
def getSubjectHtml(currentTerm, index, lower_limit, upper_limit):
    ## must install selenium and put chrome webdriver in same folder as this file
    # global browser      # keeps browser open after program executes

    browser = webdriver.Chrome()
    browser.get('https://oscar.gatech.edu/pls/bprod/bwckctlg.p_disp_dyn_ctlg')



    ### MUST CHANGE TERM VALUE TO UPDATE FOR NEW SEMESTER ####
    term = Select(browser.find_element_by_name('cat_term_in'))
    term.select_by_visible_text(currentTerm)       ### change this for corresponding update
    browser.find_element_by_xpath("//input[@type='submit']").click()

    ## Select the subject and course range
    Select(browser.find_element_by_id('subj_id')).select_by_index(index)    # selects which subject index
    browser.find_element_by_id('crse_id_from').send_keys(lower_limit)
    browser.find_element_by_id('crse_id_to').send_keys(upper_limit)
    # Select(browser.find_element_by_xpath(/html/body/div[3]/form/table/tbody/tr[2]/td[2]/input[1]))   # enters lower_limit
    # Select(browser.find_element_by_xpath(/html/body/div[3]/form/table/tbody/tr[2]/td[2]/input[2]))   # enters upper_limit
    browser.find_element_by_xpath("//input[@type='submit']").click()
    return browser.page_source



def build_SubjectCourseDict():
    subject_html = getSubjectHtml('Fall 2020', 32, 1999, 5000)       # get subject at this index (Electrical Engineering)
    soup = BeautifulSoup(subject_html, 'html.parser')

    main_site = 'https://oscar.gatech.edu'  # declare the main url that will be added to hrefs

    course_dict = {}
    # create a matrix of all course urls in soup
    for course in soup.find_all(class_='nttitle'):
        url = main_site + course.find('a', href=True)['href']
        # print(url)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')  # get the raw html from the link in text form
        # if soup.find("All Sections for this Course")=="None":
        #     continue

        title = soup.find(class_='nttitle').text     #get the title from the page
        course_key = dict_buildCourseAndTitle(title)

        body = soup.find(class_='ntdefault').text   #get the "Detailed Class Information" from the page
        dict_buildDescAndHours(body,course_key)

        dict_buildPrerequisites(body,course_key)



    return course_dict


def dict_buildCourseAndTitle(title):
    ######## make an edge case for classes not offered anymore ECE 2030 based on All Section for this COurse###
    global course_dict
    """  create a matrix of format, [Department, Course Number, Title]  """
    # print(info)
    tempMatrix = title.split(' - ')

    infoList = ['null', 'null', 'null']         # initialize matrix
    # reorganize string into desired matrix format ['Department', 'Course Number', 'Course Title']
    tempStr = tempMatrix[0]
    department = tempStr[:tempStr.find(' ')]
    courseNumber = tempStr[tempStr.find(' ')+1:len(tempStr)]
    courseTitle = tempMatrix[1]

    course_key = department + courseNumber

    course_dict[course_key] = {}
    course_dict[course_key]['Department'] = department
    course_dict[course_key]['Course Number'] = courseNumber
    course_dict[course_key]['Course Title'] = courseTitle

    return course_key

def dict_buildDescAndHours(body,course_key):
    global course_dict
    pass

def dict_buildPrerequisites(body,course_key):
    #get the "Prerequisites" from the page
    global course_dict

    ########## make edge case if there are no prereqs like CRN 80087#################################################
    try:
        rawPrereqs = body.lower().rsplit('prerequisites:')[1]
        ################ filter out excess text to return only course numbers ##########
        rawPrereqs = re.sub('\sminimum\sgrade\sof\s.','',rawPrereqs)
        # rawPrereqs = rawPrereqs.replace(' minimum grade of c', '').replace(' minimum grade of d', '').replace(' minimum grade of t', '')
        rawPrereqs = rawPrereqs.replace('undergraduate semester level  ','')
        rawPrereqs = rawPrereqs.replace(' and ', ' && ')
        rawPrereqs = rawPrereqs.replace(' or ', ' || ')
        rawPrereqs = rawPrereqs.strip()
        course_dict[course_key]['Prerequisites'] = rawPrereqs

    except IndexError:
        prereqList = []   ## what is inputted when no prerequisite courses are required






# url='https://oscar.gatech.edu/pls/bprod/bwckschd.p_disp_detail_sched?term_in=202008&crn_in=90087'
# course1Info = getInfo(url)
# print(course1Info)

# course1Prereqs = getPrereqs(url)
# print(course1Prereqs)




courses = build_SubjectCourseDict()
for key, value in courses.items():
    print(key, ' : ', value)        ## prints out each entry in the dictionary

## Exports the courses dictionary as a json file
with open('courses.json', 'w') as json_file:
    json.dump(courses, json_file)


# response = requests.get("https://oscar.gatech.edu/pls/bprod/bwckctlg.p_disp_course_detail?cat_term_in=202008&subj_code_in=ECE&crse_numb_in=3084")
# soup = BeautifulSoup(response.text, 'html.parser')  # get the raw html from the link in text form