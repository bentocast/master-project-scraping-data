import datetime
import traceback

import requests
from bs4 import BeautifulSoup
import time

import random
import re


def collect_course_data(db, start):

    course_index = 1

    for i in range(106, 0, -1):
        page = requests.get("https://www.skilllane.com/section/latest?page={}".format(i))
        soup = BeautifulSoup(page.content, 'html.parser')
        courses = soup.find_all('a', {'id': 'course_link'})
        for j in range(len(courses), 0, -1):
            course = courses[j-1]
            endpoint = course.get('href')
            course_snapshot = course.find_all('source')[1].get('srcset').split(' ')[2]
            collect_page_informations_and_insert_to_table(db, endpoint, course_snapshot, course_index)
            course_index += 1

            end = time.time()
            print('Finish Page: %s, Course Index: %s, Course: %s, Current Process Time: %s'
                  % (i, j, endpoint, str(datetime.timedelta(seconds=(end - start)))))
            sleep_time = random.randint(10, 20)
            print('Sleep for {} seconds'.format(sleep_time))
            time.sleep(sleep_time)


def collect_page_informations_and_insert_to_table(db, href, course_snapshot, course_index=None):

    endpoint = "https://www.skilllane.com{}".format(href)
    print('Collect data from {}'.format(endpoint))
    course_page = requests.get(endpoint)
    course_soup = BeautifulSoup(course_page.content, 'html.parser')

    course_id_number = get_course_id(course_page.text)
    course_id = 'course_{}'.format(course_id_number)
    curriculum_page = requests.post('https://www.skilllane.com/courses/{}/curriculum'.format(course_id_number))
    curriculum_soup = BeautifulSoup(curriculum_page.content, 'html.parser')

    collect_and_insert_fact_course(db, course_id, course_soup, curriculum_soup)
    collect_and_insert_dim_course(db, course_id, course_soup, endpoint, course_snapshot, course_index)
    collect_and_insert_fact_course_price(db, course_id, course_soup)
    collect_and_insert_fact_course_instructor(db, course_id, course_soup)

    return course_soup, curriculum_soup


def collect_and_insert_fact_course_instructor(db, course_id, course_soup):
    try:
        instructors = course_soup \
            .find("div", {"id": "courseDetailContent"}) \
            .findAll("div", {"class": "instructor-card"})

        list_of_instructor_ids = [f"instructor_{i.a.get('href').strip()[len('/instructors/'):]}" for i in instructors]
        for instructor_id in list_of_instructor_ids:
            fact_course_instructor_values = [
                course_id,
                instructor_id
            ]
            db.insert_fact_course_instructor(fact_course_instructor_values)
    except:
        traceback.print_exc()



def collect_and_insert_fact_course_price(db, course_id, course_soup):
    try:
        fact_course_price_values = [
            course_id,
            None,
            get_full_price(course_soup),
            get_current_price(course_soup),
            get_percent_discount(course_soup),
            get_no_of_registered_users(course_soup),
        ]
    except Exception as e:
        traceback.print_exc()
        fact_course_price_values = [
            course_id,
            None,
            None,
            None,
            None,
            None
        ]
    db.insert_fact_course_price(fact_course_price_values)


def collect_and_insert_dim_course(db, course_id, course_soup, endpoint, course_snapshot, course_index):
    try:
        dim_course_values = [
            course_id,
            find_course_name(course_soup),
            endpoint,
            find_course_description(course_soup),
            course_snapshot,
            "course_index_{:04d}".format(course_index),
            find_course_short_description(course_soup),
            find_course_how_to_learn(course_soup)
        ]
    except Exception as e:
        traceback.print_exc()
        dim_course_values = [
            course_id,
            None,
            endpoint,
            None,
            None,
            None,
            None,
            None
        ]
    db.insert_dim_course(dim_course_values)


def collect_and_insert_fact_course(db, course_id, course_soup, curriculum_soup):
    try:
        fact_course_values = [
            course_id,
            None,
            get_certificate(course_soup),
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
    except Exception as e:
        traceback.print_exc()
        fact_course_values = [
            course_id,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        ]
    db.insert_fact_course(fact_course_values)


def find_course_name(course_soup):
    return course_soup.h1.get_text()


def get_course_id(course_text):
    return re.search("courses\?id=(\d+)", course_text).group(1)


def get_certificate(course_soup):
    result = course_soup \
        .find('div', {'class': 'course-sidebar-container'}) \
        .find('p', text='มีประกาศนียบัตร')
    return 0 if result is None else 1


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

    return sum(map(lambda x: any(m in x.get_text().lower() for m in ['กรณีศึกษา', 'case study']), result))


def get_no_of_tests(curriculum_soup):
    result = curriculum_soup \
        .find('div', {'class': 'box-playlist'}) \
        .findAll('div', {'class': 'text-duration'})

    return sum(map(lambda x: any(m in x.get_text().lower() for m in ['แบบทดสอบ', 'test', 'ข้อสอบ', 'แบบฝึกหัด']), result))


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


def convert_text_duration_to_mins(text_duration):
    time = text_duration.get_text().strip()
    if ':' in time:
        s = time.split(':')
        hours = int(s[-3])  if len(s) > 2 else 0
        minutes = int(s[-2]) if s[-2].isdigit() else 0
        seconds = int(s[-1]) if s[-1].isdigit() else 0
        return (hours * 60 * 60) + (minutes * 60) + seconds

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


def get_current_price(course_soup):
    result = course_soup.find('span', {'class': 'glance-purchase-price-normal'})
    if result is None:
        return 0
    else:
        result2 = re.search(r'([\d.,]+) บาท', result.get_text().strip())
        return 0 if result2.group() is None else float(result2.group(1).replace(',', ''))


def get_full_price(course_soup):
    result = course_soup.find('span', {'class': 'glance-purchase-price-full'})
    if result is None:
        return get_current_price(course_soup)
    else:
        result2 = re.search(r'([\d.,]+) บาท', result.get_text().strip())
        return get_current_price(course_soup) if result2.group() is None else float(result2.group(1).replace(',', ''))


def get_percent_discount(course_soup):
    current = get_current_price(course_soup)
    full = get_full_price(course_soup)
    return (full - current) / full if full != 0 else 0


def find_course_description(course_soup):
    result = str(course_soup.find('div', {'class': 'course-description-content'}))
    return result


def find_course_short_description(course_soup):
    result = str(course_soup.find('div', {'class': 'course-sidebar-container'}))
    return result


def find_course_how_to_learn(course_soup):
    result = str(course_soup.find('div', {'class': 'course-sidebar-container'}).find('p').get_text())
    return result
