import requests
from bs4 import BeautifulSoup
import time
from db_connection import Coursedb
import random
import re

def collect_data_01_course():

    course_db = Coursedb()

    for i in range(1, 104):
    # for i in range(1, 3):
        page = requests.get("https://www.skilllane.com/courses/all?page={}".format(i))
        soup = BeautifulSoup(page.content, 'html.parser')
        courses = soup.find_all('a', {'id': 'course_link'})
        for course in courses:
            collect_page_informations_and_insert_to_table(course['href'], course_db)
            time.sleep(random.randint(10, 30))


def collect_page_informations_and_insert_to_table(href, course_db):
    endpoint = "https://www.skilllane.com{}".format(href)
    course_page = requests.get(endpoint)
    course_soup = BeautifulSoup(course_page.content, 'html.parser')
    course_id_number = get_course_id(course_page.text)
    course_id = 'course_{}'.format(course_id_number)

    curriculum_page = requests.post('https://www.skilllane.com/courses/{}/curriculum'.format(course_id_number))
    curriculum_soup = BeautifulSoup(curriculum_page.content, 'html.parser')

    fact_course_values = [
        course_id,
        'course_category_9999',
        get_no_of_instructors(course_soup),
        get_no_of_documents(curriculum_soup),
        get_no_of_chapters(curriculum_soup),
        get_no_of_case_studies(curriculum_soup),
        get_no_of_tests(curriculum_soup),
        get_no_of_videos(curriculum_soup),
        get_avg_time_of_videos(curriculum_soup),
        get_total_time_of_videos(curriculum_soup),
        get_no_of_free_videos(curriculum_soup),
        get_avg_time_of_free_videos(curriculum_soup),
        get_total_time_of_free_videos(curriculum_soup),
        get_avg_review_score(course_soup),
        get_no_of_registered_users(course_soup),
    ]
    course_db.insert_fact_course(fact_course_values)

    dim_course_values = [
        course_id,
        find_course_name(course_soup),
        endpoint,
    ]
    course_db.insert_dim_course(dim_course_values)


def find_course_name(course_soup):
    return course_soup.h1.get_text()

def get_course_id(course_text):
    return re.search("courses\?id=(\d+)", course_text).group(1)


def get_no_of_instructors(course_soup):
    instructors = course_soup \
        .find("div", {"id": "courseDetailContent"}) \
        .findAll("div", {"class": "instructor-card"})

    list_instructors = [i.a.getText().strip() for i in instructors if i.a.getText().strip() != 'มหาวิทยาลัยธรรมศาสตร์']
    return len(list_instructors)


def get_no_of_documents(curriculum_soup):
    result = curriculum_soup.findAll('i', {'class': 'fa-file-download'})
    return len(result)


def get_no_of_chapters(curriculum_soup):
    result = curriculum_soup \
        .find('div', {'class': 'box-playlist'}) \
        .findAll('div', {'class': 'box-title'})
    return len(result)


def get_no_of_case_studies(curriculum_soup):
    result = curriculum_soup \
        .find('div', {'class': 'box-playlist'}) \
        .findAll('div', {'class': 'box-chapter'})

    return sum(map(lambda x: 'กรณีศึกษา' in x.get_text(), result))


def get_no_of_tests(curriculum_soup):
    result = curriculum_soup \
        .find('div', {'class': 'box-playlist'}) \
        .findAll('div', {'class': 'text-duration'})

    return sum(map(lambda x: any(m in x.get_text() for m in ['แบบทดสอบ']), result))


def get_no_of_videos(curriculum_soup):
    result = get_all_video_information(curriculum_soup)
    return len(result)

def get_avg_time_of_videos(curriculum_soup):
    result = get_all_video_information(curriculum_soup)
    return sum(result) / len(result) if len(result) > 0 else 0


def get_total_time_of_videos(curriculum_soup):
    result = get_all_video_information(curriculum_soup)
    return sum(result)

def get_all_video_information(curriculum_soup):
    result = curriculum_soup \
        .find('div', {'class': 'box-playlist'}) \
        .findAll('div', {'class': 'text-duration'})

    return [convert_text_duration_to_mins(x)
            for x in result
            if any(m in x.get_text() for m in [':', 'นาที'])]


def get_all_free_video_information(curriculum_soup):
    result_free_video_label = curriculum_soup \
        .find('div', {'class': 'box-playlist'}) \
        .findAll('span', {'class': 'label-success'})
    result = [x.find_next('div', {'class': 'text-duration'}) for x in result_free_video_label]

    return [convert_text_duration_to_mins(x)
            for x in result
            if any(m in x.get_text() for m in [':', 'นาที'])]


def convert_text_duration_to_mins(input):
    time = input.get_text().strip()
    if ':' in time:
        s = time.split(':')
        return (int(s[0]) * 60) + int(s[1])
    else:
        return int(time.replace(' นาที', '')) * 60


def get_no_of_free_videos(curriculum_soup):
    result = get_all_free_video_information(curriculum_soup)
    return len(result)


def get_avg_time_of_free_videos(curriculum_soup):
    result = get_all_free_video_information(curriculum_soup)
    return sum(result) / len(result) if len(result) > 0 else 0


def get_total_time_of_free_videos(curriculum_soup):
    result = get_all_free_video_information(curriculum_soup)
    return sum(result)


def get_avg_review_score(course_soup):
    review_array = course_soup.h3.getText().split(' ', 1)
    try:
        return float(review_array[0])
    except:
        return 0.0


def get_no_of_registered_users(course_soup):
    review_array = course_soup.h3.getText().split(' ', 1)
    try:
        return int(review_array[1].split(' ', 1)[0][1:])
    except:
        return 0

