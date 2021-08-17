import requests
from bs4 import BeautifulSoup
import time
from db_connection import Coursedb


def collect_page_informations_and_write(href, f, course_db, counter):
    values = collect_page_informations(href, counter)

    # insert record to database
    course_db.insert_fact_course(values)


def collect_page_informations(href, counter):
    endpoint = "https://www.skilllane.com{}".format(href)
    course_page = requests.get(endpoint)
    course_soup = BeautifulSoup(course_page.content, 'html.parser')

    no_of_instructors = get_no_of_instructors(course_soup)
    avg_review_score, no_of_registered_users = get_review_information(course_soup)

    return [
        counter,
        no_of_instructors,
        avg_review_score,
        no_of_registered_users
    ]

def get_no_of_instructors(course_soup):
    instructors = course_soup \
        .find("div", {"id": "courseDetailContent"}) \
        .findAll("div", {"class": "instructor-card"})

    if instructors[-1].find("a").getText().strip() == 'มหาวิทยาลัยธรรมศาสตร์':
        return len(instructors) - 1
    else:
        return len(instructors)


def get_review_information(course_soup):
    review_array = course_soup.h3.getText().split(' ', 1)
    try:
        review_score = float(review_array[0])
        review_users = int(review_array[1].split(' ', 1)[0][1:])
    except:
        review_score = 0.0
        review_users = 0
    return (review_score, review_users)


def main():

    counter = 1
    f = open("../result/result.txt", "w")
    course_db = Coursedb()

    # for i in range(1, 100):
    for i in range(1, 2):
        page = requests.get("https://www.skilllane.com/courses/all?page={}".format(i))
        soup = BeautifulSoup(page.content, 'html.parser')
        courses = soup.find_all('a', id='course_link')
        for course in courses:
            collect_page_informations_and_write(course['href'], f, course_db, counter)
            time.sleep(3)
            counter += 1
    f.close()


if __name__ == '__main__':
    main()


