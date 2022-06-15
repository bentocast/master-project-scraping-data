import webbrowser


def update_instructor(db, start):
    result = db.get_all_instructors()
    for i in range(14, len(result)):
        r = result[i]
        print('-----------------------------------------------------------')
        print('Index: {}, ID: {}, Name: {}'.format(i, r['instructor_id'], r['full_name']))

        # update_gender(r, db)
        update_tutor_founder_school(r, db)


def update_gender(r, db):
    if r['gender_id'] is not None:
        return

    webbrowser.open(r['href'], autoraise=False)

    print('What is a gender? Current: {} (1 = Male, 2 = Female, 3 = LBGT, 4=No Gender)'.format(r['gender_id']))
    gender_no = int(input())

    gender_id = 'gender_0{}'.format(gender_no)
    values = [gender_id, r['instructor_id']]
    db.update_gender_id_fact_instructor(values)


def update_tutor_founder_school(r, db):
    webbrowser.open(r['href'], autoraise=False)

    values = []
    while len(values) != 3:
        print('What is (is_tutor, is_founder, is_school)?')
        print(f'current value is ({r["is_tutor"]}, {r["is_founder"]}, {r["is_school"]})')
        values = list(input())

    values.append(r['instructor_id'])
    db.update_tutor_founder_school_fact_instructor(values)

    print('What is education (1=less Bachelor, 2=Bacholor, 3=Master, 4=Phd)?')
    print(f'current value is {r["education_id"]}')
    input_2 = input()
    input_2 = None if input_2 == '' else "education_00{}".format(input_2)
    values_2 = [input_2, r['instructor_id']]
    db.update_education_fact_instructor(values_2)

    print('What is number of years experience?')
    print(f'current value is {r["no_of_year_experience"]}')
    input_3 = input()
    input_3 = None if input_3 == '' else input_3
    values_3 = [input_3, r['instructor_id']]
    db.update_no_of_year_experience(values_3)
