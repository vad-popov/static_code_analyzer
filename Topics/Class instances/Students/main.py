class Student:

    def __init__(self, name, last_name, birth_year):
        self.name = name
        self.last_name = last_name
        self.birth_year = birth_year
        # calculate the student_id here
        self.student_id = name[:1] + last_name + birth_year

    def show_id(self):
        print(self.student_id)

first_student = Student(input(), input(), input())
first_student.show_id()