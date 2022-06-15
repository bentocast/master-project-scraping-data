import pypyodbc as pyo
from src.db.database_config import db_config
import pandas as pd

class Database:

    def __init__(self):
        self.con = pyo.connect(**db_config)
        self.cursor = self.con.cursor()
        print("Connect to course database successfully")

    def __del__(self):
        self.con.close()

    def view(self):
        self.cursor.execute("SELECT * from fact_course")
        rows = self.cursor.fetchall()
        return rows

    def is_course_already_in_fact_course(self, course_id):
        self.cursor.execute("SELECT course_id from fact_course where course_id = '%s'" % course_id)
        return len(self.cursor.fetchall()) > 0

    def insert_fact_course(self, values):
        if self.is_course_already_in_fact_course(values[0]):
            print('do nothing, as this course exists in database')
        else:
            sql=("INSERT INTO fact_course("
                "course_id"
                ", course_category_id"
                ", get_certificate"
                ", no_of_instructors"
                ", no_of_documents"
                ", no_of_chapters"
                ", no_of_case_studies"
                ", no_of_tests"
                ", no_of_videos"
                ", avg_time_of_videos"
                ", total_time_of_videos"
                ", no_of_free_videos"
                ", avg_time_of_free_videos"
                ", total_time_of_free_videos"
                ", avg_review_score"
                ", no_of_registered_users"
                ") "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
            )
            self.cursor.execute(sql, values)
            self.con.commit()
            print("Insert row to fact_course successfully")

    def is_href_course_already_in_dim_course(self, href):
        self.cursor.execute("SELECT href from dimension_course where href = '%s'" % href)
        return len(self.cursor.fetchall()) > 0

    def is_course_already_in_dim_course(self, course_id):
        self.cursor.execute("SELECT course_id from dimension_course where course_id = '%s'" % course_id)
        return len(self.cursor.fetchall()) > 0

    def insert_dim_course(self, values):
        if self.is_course_already_in_dim_course(values[0]):
            print('do nothing, as this course exists in database')
        else:
            sql=("INSERT INTO dimension_course("
                 "course_id, course_name, course_href, course_description, "
                 "course_snapshot, course_index, course_short_description, course_how_to_learn"
                 ") VALUES (?,?,?,?,?,?,?,?)")
            self.cursor.execute(sql, values)
            self.con.commit()
            print("Insert row to dimension_course successfully")

    def insert_dim_course_category(self, values):
        sql=("INSERT INTO dimension_course_category("
             "course_category_id, course_category_name"
             ") VALUES (?,?)")
        self.cursor.execute(sql, values)
        self.con.commit()
        print("Insert row to dimension_course_category successfully")

    def get_category_id(self, category_name):
        self.cursor.execute("SELECT * from dimension_course_category where course_category_name = %s", category_name)
        rows = self.cursor.fetchall()
        return rows[0]['course_category_id']

    def is_course_already_in_fact_course_price(self, course_id):
        self.cursor.execute("SELECT course_id from fact_course_price where course_id = '%s'" % course_id)
        return len(self.cursor.fetchall()) > 0

    def insert_fact_course_price(self, values):
        if self.is_course_already_in_fact_course_price(values[0]):
            print('do nothing, as this course exists in fact_course_price')
        else:
            sql=("INSERT INTO fact_course_price("
                 "course_id, course_category_id, course_price, "
                 "course_promotion_price, course_percent_discount, course_no_of_registered_users"
                 ") VALUES (?,?,?,?,?,?)")
            self.cursor.execute(sql, values)
            self.con.commit()
            print("Insert row to fact_course_price successfully")

    def is_course_already_in_fact_course_instructor(self, values):
        sql = "SELECT course_id from fact_course_instructor where course_id = ? AND instructor_id = ?"
        self.cursor.execute(sql, values)
        return len(self.cursor.fetchall()) > 0

    def insert_fact_course_instructor(self, values):
        if self.is_course_already_in_fact_course_instructor(values):
            print('do nothing, as this course exists in fact_course_instructor')
        else:
            sql=("INSERT INTO fact_course_instructor("
                 "course_id, instructor_id "
                 ") VALUES (?,?)")
            self.cursor.execute(sql, values)
            self.con.commit()
            print("Insert row to fact_course_instructor successfully")

    def get_all_instructors(self):
        self.cursor.execute("SELECT * FROM fact_instructor a JOIN dimension_instructor b "
                            "ON a.instructor_id = b.instructor_id")
        return self.cursor.fetchall()

    def update_gender_id_fact_instructor(self, values):
        sql=""" UPDATE fact_instructor
                SET gender_id = ?
                WHERE instructor_id = ?
                """

        self.cursor.execute(sql, values)
        self.con.commit()
        print("Update {} to fact_instructor successfully".format(values))

    def update_tutor_founder_school_fact_instructor(self, values):
        sql=""" UPDATE fact_instructor
                SET is_tutor = ?, is_founder = ?, is_school = ?  
                WHERE instructor_id = ?
                """

        self.cursor.execute(sql, values)
        self.con.commit()
        print("Update {} to fact_instructor successfully".format(values))

    def update_education_fact_instructor(self, values):
        sql=""" UPDATE fact_instructor
                SET education_id = ?  
                WHERE instructor_id = ?
                """

        self.cursor.execute(sql, values)
        self.con.commit()
        print("Update {} to fact_instructor successfully".format(values))

    def update_no_of_year_experience(self, values):
        sql=""" UPDATE fact_instructor
                SET no_of_year_experience = ?  
                WHERE instructor_id = ?
                """

        self.cursor.execute(sql, values)
        self.con.commit()
        print("Update {} to fact_instructor successfully".format(values))

    def is_instructor_already_in_fact_instructor(self, instructor_id):
        self.cursor.execute("SELECT instructor_id from fact_instructor where instructor_id = '%s'" % instructor_id)
        return len(self.cursor.fetchall()) > 0

    def insert_fact_instructor(self, values):
        if self.is_instructor_already_in_fact_instructor(values[0]):
            print('do nothing, as this instructor exists in fact_instructor')
        else:
            sql=("INSERT INTO fact_instructor("
                    "instructor_id"
                    ", education_id"
                    ", gender_id"
                    ", is_tutor"
                    ", is_founder"
                    ", is_school"
                    ", no_of_year_experience"
                    ", no_of_background_bullets"
                    ", no_of_courses"
                    ", no_of_avg_documents"
                    ", no_of_avg_tests"
                    ", no_of_avg_chapters"
                    ", no_of_avg_case_studies"
                    ", no_of_avg_videos"
                    ", avg_time_of_each_video"
                    ", avg_time_of_total_videos"
                    ", no_of_avg_free_videos"
                    ", avg_time_of_each_free_video"
                    ", avg_time_of_total_free_videos"
                    ", avg_review_score"
                    ", no_of_registered_users"
                    ") VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)")
            self.cursor.execute(sql, values)
            self.con.commit()
            print("Insert row to fact_instructor successfully")

    def is_instructor_already_in_dimension_instructor(self, instructor_id):
        self.cursor.execute("SELECT instructor_id from dimension_instructor where instructor_id = '%s'" % instructor_id)
        return len(self.cursor.fetchall()) > 0

    def insert_dimension_instructor(self, values):
        if self.is_instructor_already_in_dimension_instructor(values[0]):
            print('do nothing, as this instructor exists in dimension_instructor')
        else:
            sql=("INSERT INTO dimension_instructor("
                 "instructor_id, full_name, first_name, last_name, nick_name, href, image"
                 ") VALUES (?,?,?,?,?,?,?)")
            self.cursor.execute(sql, values)
            self.con.commit()
            print("Insert row to dimension_instructor successfully")

    def get_all_course_packages(self):
        self.cursor.execute("SELECT course_package_href from dimension_course_package")
        rows = self.cursor.fetchall()
        return rows

    def is_course_package_already_in_dim_course_package(self, href):
        self.cursor.execute("SELECT course_package_href from dimension_course_package where course_package_href = '%s'" % href)
        return len(self.cursor.fetchall()) > 0

    def insert_dim_course_package(self, values):
        if self.is_course_package_already_in_dim_course_package(values[2]):
            print('do nothing, as this package href exists in dimension_course_package')
        else:
            sql=("INSERT INTO dimension_course_package("
                 "course_package_id, course_package_name, course_package_href"
                 ") VALUES (?,?,?)")
            self.cursor.execute(sql, values)
            self.con.commit()
            print("Insert row to dimension_course_package successfully")

    def update_dim_course_package(self, values):
        sql=""" UPDATE dimension_course_package
                SET course_package_id = ?, course_package_name = ?
                WHERE course_package_href = ?
                """

        self.cursor.execute(sql, values)
        self.con.commit()
        print("Insert row to dimension_course_package successfully")

    def is_course_package_already_in_fact_course_package(self, values):
        self.cursor.execute(""" SELECT course_id, course_package_id 
                                FROM fact_course_package 
                                where course_id = ? AND course_package_id = ?""", values)
        return len(self.cursor.fetchall()) > 0

    def insert_fact_course_package(self, values):
        if self.is_course_package_already_in_fact_course_package(values):
            print('do nothing, as this package href exists in fact_course_package')
        else:
            sql=("INSERT INTO fact_course_package("
                 "course_id, course_package_id"
                 ") VALUES (?,?)")
            self.cursor.execute(sql, values)
            self.con.commit()
            print("Insert row to fact_course_package successfully")

    def is_course_package_already_in_fact_course_package_price(self, value):
        self.cursor.execute(""" SELECT course_package_id 
                                FROM fact_course_package_price
                                where course_package_id = ? """, value)
        return len(self.cursor.fetchall()) > 0

    def insert_fact_course_package_price(self, values):
        if self.is_course_package_already_in_fact_course_package_price(values[:1]):
            print('do nothing, as this package href exists in fact_course_package_price')
        else:
            sql=("INSERT INTO fact_course_package_price("
                 "course_package_id, no_of_courses, package_price, package_promotion_price, package_percent_discount, package_no_of_registered_users"
                 ") VALUES (?,?,?,?,?,?)")
            self.cursor.execute(sql, values)
            self.con.commit()
            print("Insert row to fact_course_package_price successfully")

    def get_category_id_from_dimension_course_category(self, href):
        value = ['%{}%'.format(href)]
        self.cursor.execute(""" SELECT course_category_id 
                                FROM dimension_course_category
                                where href like ? """, value)
        result = self.cursor.fetchone()
        return None if result is None else result[0]

    def get_course_id_from_dimension_course(self, href):
        value = ['%{}'.format(href)]
        self.cursor.execute(""" SELECT course_id 
                                FROM dimension_course
                                where course_href like ? """, value)
        result = self.cursor.fetchone()
        return None if result is None else result[0]

    def update_course_category_in_fact_course(self, course_id, course_category_id):
        values = [course_category_id, course_id]
        sql=""" UPDATE fact_course
                SET course_category_id = ?
                WHERE course_id = ?
                """

        self.cursor.execute(sql, values)
        self.con.commit()
        print("Insert row to dimension_course_package successfully")

    def update_course_category_in_fact_course_price(self, course_id, course_category_id):
        values = [course_category_id, course_id]
        sql=""" UPDATE fact_course_price
                SET course_category_id = ?
                WHERE course_id = ?
                """

        self.cursor.execute(sql, values)
        self.con.commit()
        print("Insert row to dimension_course_package successfully")

    def get_course_snapshot(self):
        sql = """ SELECT course_id, course_name, course_snapshot FROM dimension_course"""
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result

    def insert_fact_course_thumbnail_aws_result(self, values):
        sql= """INSERT INTO fact_course_thumbnail_aws_result(
             course_id, detect_labels, detect_text, detect_faces
             ) VALUES (?,?,?,?) """
        self.cursor.execute(sql, values)
        self.con.commit()
        print("Insert row to fact_course_thumbnail_aws_result successfully")

    def insert_fact_course_thumbnail_gcloud_result(self, values):
        sql= """INSERT INTO fact_course_thumbnail_gcloud_result(
             course_id, result
             ) VALUES (?,?) """
        self.cursor.execute(sql, values)
        self.con.commit()
        print("Insert row to fact_course_thumbnail_gcloud_result successfully")

    def insert_fact_instructor_thumbnail_aws_result(self, values):
        sql= """INSERT INTO fact_instructor_thumbnail_aws_result(
             instructor_id, detect_labels, detect_text, detect_faces
             ) VALUES (?,?,?,?) """
        self.cursor.execute(sql, values)
        self.con.commit()
        print("Insert row to fact_instructor_thumbnail_aws_result successfully")

    def insert_fact_instructor_thumbnail_gcloud_result(self, values):
        sql= """INSERT INTO fact_instructor_thumbnail_gcloud_result(
             instructor_id, result
             ) VALUES (?,?) """
        self.cursor.execute(sql, values)
        self.con.commit()
        print("Insert row to fact_instructor_thumbnail_gcloud_result successfully")
