from src.course.collect_course import collect_course_data, collect_page_informations_and_insert_to_table
from src.course import process_course_screenshot
from src.instructors import process_instructor_screenshot
from src.course_category.collect_course_category import collect_course_category, collect_course_category_page
from src.instructors.collect_instructors import collect_instructor_data, get_instructor_info
from src.course_package.collect_course_package import collect_course_package_data
import time
import datetime
from src.db.database import Database
from src.instructors.update_instructors import update_instructor

if __name__ == '__main__':

    start = time.time()
    db = Database()

    # 01
    collect_course_data(db, start)

    # 02
    collect_instructor_data(db, start)

    # 03
    collect_course_package_data(db, start)

    # 04
    collect_course_category(db, start)

    # 05 Not Finish Yet
    update_instructor(db, start)

    # 06
    process_course_screenshot.screen_shot_processing(db, start)

    # 07
    process_instructor_screenshot.screen_shot_processing(db, start)

    end = time.time()
    print('All Process Time: %s' % str(datetime.timedelta(seconds=(end - start))))
