from orjson import loads

def read_json(filename):
    
    with open(filename, "r") as file:
        return loads(file.text())

def get_student_data():
    return read_json("students.json")

def get_test_data():
    return read_json("tests.json")

login_data = {
    "students": get_student_data(),
    "tests": get_test_data()
}
