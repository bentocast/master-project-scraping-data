import datetime

import requests
from bs4 import BeautifulSoup
import time

from src.course import collect_course
import random
import re
import urllib3
import traceback

def collect_instructor_data(db, start):

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    page = requests.get("https://www.skilllane.com/instructors")
    soup = BeautifulSoup(page.content, 'html.parser')
    instructors = soup \
        .find('div', {'id': 'courses_categories'}) \
        .findAll('a')

    # for instructor in instructors:
    for i in range(0, 1075):
        instructor = instructors[i]
        get_instructor_info(instructor.get('href'), db)

        end = time.time()
        print('Finish Instructor %s, Current Process Time: %s' % (i, str(datetime.timedelta(seconds=(end - start)))))
        sleep_time = random.randint(2, 20)
        print('Sleep for {} seconds, after getting an instructor info'.format(sleep_time))
        time.sleep(sleep_time)

def is_instructor_page_existing(instructor_soup):
    return instructor_soup.find('h4', string='ไม่พบหน้าที่ต้องการ') is not None \
           or \
           instructor_soup.find('title').get_text() == 'SkillLane | ผู้เชี่ยวชาญที่สอนกับ SkillLane'


def get_instructor_info(href, db):
    endpoint = "https://www.skilllane.com{}".format(href)
    print('Get data from: {}'.format(endpoint))
    instructor_page = requests.get(endpoint)
    instructor_soup = BeautifulSoup(instructor_page.content, 'html.parser')

    course_package_links = instructor_soup.find('h4', string="คอร์สแพ็กเกจ")
    if course_package_links is None:
        return
    else:
        all_course_package_links = course_package_links \
            .find_parent() \
            .next_sibling.next_sibling \
            .find_all('a', {'id': 'course_link'})
        for link in all_course_package_links:
            href = link.get('href')
            package_endpoint = "https://www.skilllane.com{}".format(href)
            print('Found Course Package: {}'.format(package_endpoint))
            db.insert_dim_course_package([None, None, package_endpoint])

    # if is_instructor_page_existing(instructor_soup):
    #     print('skip, as this instructor page does not exist')
    #     return
    #
    # instructor_id = 'instructor_{}'.format(href[13:])
    # course_curriculum_soups = get_course_and_cirriculum_soups(db)
    # collect_and_insert_dim_instructor(endpoint, db, instructor_id, instructor_soup)
    # collect_and_insert_fact_instructor(course_curriculum_soups, db, instructor_id, instructor_soup)


def collect_and_insert_fact_instructor(course_curriculum_soups, db, instructor_id, instructor_soup):
    try:
        fact_instructor_value = [
            instructor_id,
            get_education_id(instructor_soup),
            get_gender_id(instructor_soup),
            get_is_tutor(instructor_soup),
            get_is_founder(instructor_soup),
            get_is_school(instructor_soup),
            get_no_of_year_experience(instructor_soup),
            get_no_of_background_bullets(instructor_soup),
            get_no_of_courses(course_curriculum_soups),
            get_no_of_avg_documents(course_curriculum_soups),
            get_no_of_avg_tests(course_curriculum_soups),
            get_no_of_avg_chapters(course_curriculum_soups),
            get_no_of_avg_case_studies(course_curriculum_soups),
            get_no_of_avg_videos(course_curriculum_soups),
            get_avg_time_of_each_video(course_curriculum_soups),
            get_avg_time_of_total_videos(course_curriculum_soups),
            get_no_of_avg_free_videos(course_curriculum_soups),
            get_avg_time_of_each_free_video(course_curriculum_soups),
            get_avg_time_of_total_free_videos(course_curriculum_soups),
            get_avg_review_score(instructor_soup),
            get_no_of_registered_users(instructor_soup),
        ]
    except Exception as e:
        traceback.print_exc()
        fact_instructor_value = [
            instructor_id,
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
            None,
            None,
            None,
            None,
            None,
        ]
    db.insert_fact_instructor(fact_instructor_value)


def collect_and_insert_dim_instructor(endpoint, db, instructor_id, instructor_soup):
    try:
        full_name, first_name, last_name, nick_name = get_instructor_name(instructor_soup)
        dimension_instructor_value = [
            instructor_id,
            full_name,
            first_name,
            last_name,
            nick_name,
            endpoint,
            get_image_url(instructor_soup)
        ]
    except Exception as e:
        traceback.print_exc()
        dimension_instructor_value = [
            instructor_id,
            "",
            "",
            "",
            "",
            endpoint,
            "",
        ]
    db.insert_dimension_instructor(dimension_instructor_value)


def get_course_and_cirriculum_soups(instructor_soup, db):
    course_links = instructor_soup \
            .find('h4', string=re.compile(r"คอร์สที่สอนโดย.*")) \
            .find_parent().next_sibling.next_sibling \
            .find_all('a', {'id': 'course_link'})

    result = []
    for course_link in course_links:

        href = course_link.get('href')
        course_snapshot = course_link.find('source', {'type': 'image/jpeg'}).get('srcset').split(' ')[4]
        course_soup, curriculum_soup = collect_course.collect_page_informations_and_insert_to_table(db, href, course_snapshot)
        result.append(CourseAndCurriculumSoup(course_soup, curriculum_soup))

        sleep_time = random.randint(2, 15)
        print('Sleep for {} seconds, after getting a course info'.format(sleep_time))
        time.sleep(sleep_time)

    return result


def get_image_url(instructor_soup):
    result = instructor_soup \
        .find('div', {'class': 'instructor-img'}) \
        .find('img').get('src')
    return result.split('?')[0]


def get_instructor_name(instructor_soup):
    full_name = instructor_soup \
        .find('div', {'class': 'instructor-name'}) \
        .getText().strip()
    full_name_group = re.search(r'^((?:บริษัท |อ. |ผศ. )?\S+)(?:\s+(\S+.*?))?(?:\s+\((.*)\))?$', full_name)

    if full_name_group.group() is None:
        return full_name, full_name, None, None
    else:
        return full_name, full_name_group.group(1), full_name_group.group(2), full_name_group.group(3)


def get_education_id(instructor_soup):
    short_history = instructor_soup.find('ul', {'class': 'instructor'}).get_text().strip()
    if any(word in short_history for word in ['ปริญญาเอก', 'ป.เอก', 'Phd']):
        return 'education_004'
    elif any(word in short_history for word in ['ปริญญาโท', 'ป.โท', 'Master degree']):
        return 'education_003'
    elif any(word in short_history for word in ['ปริญญาตรี', 'ป.ตรี', 'Bachelor']):
        return 'education_002'
    elif any(word in short_history for word in ['ต่ำกว่าปริญญาตรี', 'มัธยม', 'ประถม']):
        return 'education_001'
    else:
        return None


def get_gender_id(instructor_soup):
    first_name = get_instructor_name(instructor_soup)[1]
    request_payload = {
        "instances": [
            {
                "X": [ord(c) - 3585 for c in first_name],
                "seq_lengths":8
            }
        ]
    }
    result = requests.post(
        "https://www.nkuln.com/tfapi/v1/models/default:predict",
        json = request_payload,
        verify=False
    )
    predict_result = result.json()['predictions'][0]['predictions']
    if predict_result > 0.6:
        return 'gender_01'
    elif predict_result < 0.4:
        return 'gender_02'
    else:
        return None


def get_is_tutor(instructor_soup):
    short_history = instructor_soup.find('ul', {'class': 'instructor'}).get_text().strip().lower()
    if any(word in short_history for word in ['ครู', 'อาจารย์']):
        return 1
    else:
        return None


def get_is_founder(instructor_soup):
    short_history = instructor_soup.find('ul', {'class': 'instructor'}).get_text().strip().lower()
    if any(word in short_history for word in ['ผู้ก่อตั้ง', 'ผู้ร่วมก่อตั้ง', 'ceo', 'co-founder']):
        return 1
    else:
        return None


def get_is_school(instructor_soup):
    first_name = get_instructor_name(instructor_soup)[0].lower()
    if any(word in first_name for word in ['มหาวิทยาลัย', 'โรงเรียน', 'university', 'school', 'ชุมชน', 'team']):
        return 1
    else:
        return None


def get_no_of_year_experience(instructor_soup):
    short_history = instructor_soup.find('ul', {'class': 'instructor'}).get_text().strip()
    result = re.search(r"(\d+)\s*ปี", short_history)
    return None if result is None else result.group(1)


def get_no_of_background_bullets(instructor_soup):
    short_history = instructor_soup.find('ul', {'class': 'instructor'}).find_all('br')
    return len(short_history) - 1


def get_no_of_courses(course_soups):
    return len(course_soups)


def get_no_of_avg_documents(course_and_cirriculum_soup):
    result = [collect_course.get_no_of_documents(c.curriculum_soup) for c in course_and_cirriculum_soup]
    return sum(result) / len(result) if len(result) > 0 else 0


def get_no_of_avg_tests(course_and_cirriculum_soup):
    result = [collect_course.get_no_of_tests(c.curriculum_soup) for c in course_and_cirriculum_soup]
    return sum(result) / len(result) if len(result) > 0 else 0


def get_no_of_avg_chapters(course_and_cirriculum_soup):
    result = [collect_course.get_no_of_chapters(c.curriculum_soup) for c in course_and_cirriculum_soup]
    return sum(result) / len(result) if len(result) > 0 else 0


def get_no_of_avg_case_studies(course_and_cirriculum_soup):
    result = [collect_course.get_no_of_case_studies(c.curriculum_soup) for c in course_and_cirriculum_soup]
    return sum(result) / len(result) if len(result) > 0 else 0


def get_no_of_avg_videos(course_and_cirriculum_soup):
    result = [collect_course.get_no_of_videos(c.curriculum_soup) for c in course_and_cirriculum_soup]
    return sum(result) / len(result) if len(result) > 0 else 0


def get_avg_time_of_each_video(course_and_cirriculum_soup):
    result = [collect_course.get_total_time_of_videos(c.curriculum_soup) for c in course_and_cirriculum_soup]
    result2 = [collect_course.get_no_of_videos(c.curriculum_soup) for c in course_and_cirriculum_soup]
    return sum(result) / sum(result2) if sum(result2) > 0 else 0


def get_avg_time_of_total_videos(course_and_cirriculum_soup):
    result = [collect_course.get_total_time_of_videos(c.curriculum_soup) for c in course_and_cirriculum_soup]
    return sum(result) / len(result) if len(result) > 0 else 0


def get_no_of_avg_free_videos(course_and_cirriculum_soup):
    result = [collect_course.get_no_of_free_videos(c.curriculum_soup) for c in course_and_cirriculum_soup]
    return sum(result) / len(result) if len(result) > 0 else 0


def get_avg_time_of_each_free_video(course_and_cirriculum_soup):
    result = [collect_course.get_total_time_of_free_videos(c.curriculum_soup) for c in course_and_cirriculum_soup]
    result2 = [collect_course.get_no_of_free_videos(c.curriculum_soup) for c in course_and_cirriculum_soup]
    return sum(result) / sum(result2) if sum(result2) > 0 else 0


def get_avg_time_of_total_free_videos(course_and_cirriculum_soup):
    result = [collect_course.get_total_time_of_free_videos(c.curriculum_soup) for c in course_and_cirriculum_soup]
    return sum(result) / len(result) if len(result) > 0 else 0


def get_avg_review_score(instructor_soup):
    review_score_text = instructor_soup \
        .find('div', {'class': 'instructor-rating'}) \
        .find_all('p')[0] \
        .get_text()

    try:
        return float(re.search(r'([\d.]*)\s+คะแนนเฉลี่ย', review_score_text).group(1))
    except:
        return 0.0


def get_no_of_registered_users(instructor_soup):
    reviews_text = instructor_soup \
        .find('div', {'class': 'instructor-rating'}) \
        .find_all('p')[1] \
        .get_text()

    try:
        return int(re.search(r'([\d]*)\s+รีวิว', reviews_text).group(1))
    except:
        return 0


class CourseAndCurriculumSoup:

    def __init__(self, course_soup, curriculum_soup):
        self.course_soup = course_soup
        self.curriculum_soup = curriculum_soup
