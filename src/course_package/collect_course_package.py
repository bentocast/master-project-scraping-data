import datetime
import time
import random
import re
import requests
from bs4 import BeautifulSoup

def collect_course_package_data(db, start):

    href = [x[0] for x in db.get_all_course_packages()]

    for i in range(0, len(href)):
        current = time.time()
        print('Start Course Package %s, Current Process Time: %s' % (i, str(datetime.timedelta(seconds=(current - start)))))
        collect_course_package_from_href(href[i], db)
        sleep_time = random.randint(2, 20)
        print('Sleep for {} seconds, after getting a course package info'.format(sleep_time))
        time.sleep(sleep_time)


def collect_course_package_from_href(endpoint, db):

    course_package_page = requests.get(endpoint)
    course_package_soup = BeautifulSoup(course_package_page.content, 'html.parser')

    course_package_name = get_course_package_name(course_package_soup)
    if course_package_name is None:
        return

    collect_and_update_dim_course_package(db, endpoint, course_package_name)

    collect_and_update_fact_course_package(db, endpoint, course_package_soup)
    collect_and_update_fact_course_package_price(db, endpoint, course_package_soup)


def collect_and_update_dim_course_package(db, endpoint, course_package_name):
    dim_course_package_values = [
        get_course_package_id(endpoint),
        course_package_name,
        endpoint
    ]
    db.update_dim_course_package(dim_course_package_values)


def get_list_of_course_ids(course_package_soup):
    return [
        x.get('id')
        for x in course_package_soup.find_all('div', {'class': 'course-video-item'})
    ]


def collect_and_update_fact_course_package(db, endpoint, course_package_soup):

    list_of_course_id = get_list_of_course_ids(course_package_soup)
    for course_id in list_of_course_id:
        fact_course_package_values = [
            "course_{}".format(course_id),
            get_course_package_id(endpoint)
        ]
        db.insert_fact_course_package(fact_course_package_values)


def collect_and_update_fact_course_package_price(db, endpoint, course_package_soup):

    list_of_course_id = get_list_of_course_ids(course_package_soup)
    dim_course_package_values = [
        get_course_package_id(endpoint),
        get_no_of_course(list_of_course_id),
        get_package_price(course_package_soup),
        get_package_promotion_price(course_package_soup),
        get_package_percent_discount(course_package_soup),
        get_package_no_of_registered_users(course_package_soup),
    ]
    db.insert_fact_course_package_price(dim_course_package_values)

def get_course_package_name(course_package_soup):
    result = course_package_soup.find('div', {'class': 'course-name-title'})
    if result is None:
        return None
    else:
        return result.get_text().strip()


def get_course_package_id(endpoint):
    suffix = endpoint.replace('https://www.skilllane.com/course_bundles/', '')
    return "course_package_{}".format(suffix)


def get_no_of_course(list_of_course_id):
    return len(list_of_course_id)


def get_package_promotion_price(course_package_soup):
    result = course_package_soup \
                .find('div', {'class': 'discount-price'})
    if result is None:
        return 0
    else:
        result2 = re.search(r'([\d.,]+) บาท', result.get_text().strip())
        return 0 if result2.group() is None else float(result2.group(1).replace(',', ''))


def get_package_price(course_package_soup):
    result = course_package_soup \
                .find('div', {'class': 'discount-price'}) \
                .find('span')

    if result is None:
        return 0
    else:
        result2 = re.search(r'([\d.,]+) บาท', result.get_text().strip())
        return 0 if result2.group() is None else float(result2.group(1).replace(',', ''))


def get_package_percent_discount(course_package_soup):
    current = get_package_promotion_price(course_package_soup)
    full = get_package_price(course_package_soup)
    return (full - current) / full if full != 0 else 0


def get_package_no_of_registered_users(course_package_soup):
    None