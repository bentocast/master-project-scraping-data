import pypyodbc as pyo

dbConfig = {
    'driver': 'SQL Server',
    'Server': 'LAPTOP-20VU0V92',
    'Database': '01_course',
    'username': 'LAPTOP-20VU0V92\bentocast',
    'password': 'Iwillget6packs'
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
             "course_id, no_of_instructors, avg_review_score, no_of_registered_users"
             ") VALUES (?,?,?,?)")
        self.cursor.execute(sql, values)
        self.con.commit()
        print("Insert row to database successfully")

    def insert_dim_course(self, values):

    def insert_dim_course(self, values):