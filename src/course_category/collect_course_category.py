import datetime
import random
import time

import requests
from bs4 import BeautifulSoup


def collect_course_category(db, start):

    main_page = requests.get("https://www.skilllane.com")
    soup = BeautifulSoup(main_page.content, 'html.parser')

    sleep_time = random.randint(10, 120)
    print('Sleep for {} seconds'.format(sleep_time))
    time.sleep(sleep_time)

    #  menu-sidebar-item
    category_a_tags = soup.find('div', {'class': 'menu-sidebar-item'}).find_all('a')
    category_hrefs = [x.get('href') for x in category_a_tags]
    for i in range(0, len(category_hrefs)):
        href = category_hrefs[i]
        is_next = True
        page_no = 1

        while is_next:

            category_soup = collect_course_category_page(db, href, page_no)

            page_no += 1
            next_button = category_soup.find('a', {'rel': 'next'})
            is_next = next_button is not None

            end = time.time()
            print('Finish Course Category: %s, Page: %s, Current Process Time: %s' % (href, page_no, str(datetime.timedelta(seconds=(end - start)))))
            sleep_time = random.randint(10, 30)
            print('Sleep for {} seconds'.format(sleep_time))
            time.sleep(sleep_time)


def collect_course_category_page(db, category_href, page_no):
    endpoint = "https://www.skilllane.com/{}?page={}".format(category_href, page_no)
    print('collect data from endpoint: {}'.format(endpoint))
    category_page = requests.get(endpoint, timeout=120)
    category_soup = BeautifulSoup(category_page.content, 'html.parser')

    all_course_a = category_soup \
        .find_all('div', {'class': 'feature-course-container'})[-1] \
        .find_all('a', {'id': 'course_link'})

    all_course_href = [x.get('href') for x in all_course_a]

    course_category_id = db.get_category_id_from_dimension_course_category(category_href)
    for course_href in all_course_href:

        course_id = db.get_course_id_from_dimension_course(course_href)
        if course_id is not None:
            print(f'Update Category: {course_category_id} for course_id: {course_id} in fact_course')
            db.update_course_category_in_fact_course(course_id, course_category_id)
            print(f'Update Category: {course_category_id} for course_id: {course_id} in fact_course_price')
            db.update_course_category_in_fact_course_price(course_id, course_category_id)
        else:
            print('No course id found')

    return category_soup






