import pypyodbc as pyo

dbConfig = {
    'driver': 'SQL Server',
    'Server': 'LAPTOP-20VU0V92',
    'Database': '01_course',
    'username': 'LAPTOP-20VU0V92\bentocast',
    'password': 'Iwillget6packs',
}

class Coursedb:

    def __init__(self):
        self.con = pyo.connect(**dbConfig)
        self.cursor = self.con.cursor()
        print("Connect to database course successfully")

    def __del__(self):
        self.con.close()

    def view(self):
        self.cursor.execute("SELECT * from fact_course")
        rows = self.cursor.fetchall()
        return rows

    def insert_fact_course(self, values):
        sql=("INSERT INTO fact_course("
            "course_id"
            ", course_category_id"
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
             ") VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)")
        self.cursor.execute(sql, values)
        self.con.commit()
        print("Insert row to fact_course successfully")

    def insert_dim_course(self, values):
        sql=("INSERT INTO dim_course("
             "course_id, course_name, course_href"
             ") VALUES (?,?,?)")
        self.cursor.execute(sql, values)
        self.con.commit()
        print("Insert row to dim_course successfully")

    def insert_dim_course_category(self, values):
        sql=("INSERT INTO dim_course_category("
             "course_category_id, course_category_name"
             ") VALUES (?,?)")
        self.cursor.execute(sql, values)
        self.con.commit()
        print("Insert row to dim_course_category successfully")

    def get_category_id(self, category_name):
        self.cursor.execute("SELECT * from dim_course_category where course_category_name = %s", category_name)
        rows = self.cursor.fetchall()
        return rows[0]['course_category_id']