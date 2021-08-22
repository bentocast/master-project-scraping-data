import collect_01_course
from db_connection import Coursedb

if __name__ == '__main__':
    collect_01_course.collect_data_01_course()
    # collect_01_course.collect_page_informations_and_insert_to_table('/courses/Stock-Investment-by-AndrewStotz', Coursedb())