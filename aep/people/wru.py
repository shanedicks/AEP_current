from .models import *
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

WRU_PROGRAMS = {
    "ADULT BASIC EDUCATION": "1",
    "ACCELERATING OPPORTUNITY": "2",
    "FAMILY LITERACY": "3",
    "WORKPLACE LITERACY": "4",
    "CORRECTIONAL EDUCATION PROGRAM": "5",
    "EL PROGRAM (ESL)": "6",
    "EL CIVICS": "7",
    "ADULT SECONDARY EDUCATION": "8",
    "PROGRAM FOR THE HOMELESS": "9",
    "COMMUNITY CORRECTIONS PROGRAM": "10",
    "OTHER INSTITUTIONAL PROGRAMS": "11",
    "DISTANCE EDUCATION": "12",
    "WORK-BASED PROJECT LEARNER": "13",
    "COMMUNITY EDUCATION": "14",
    "LA Career Pathways": "15",
    "Integrated English Literacy and Civics Education": "16",
    "Correctional (225)": "17",
    "Correctional (NON 225-Local funds)": "18",
    "Intake Only / Informational Services": "19",
    "Needs To Be Updated": "20"
}

def state_webdriver():
    driver = webdriver.Firefox()
    driver.maximize_window()
    driver.get("https://workreadyu.lctcs.edu")
    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_element_located((By.NAME, "btnLogin")))
    provider = driver.find_element(by='id', value='Provider')
    Select(provider).select_by_visible_text("DELGADO COMMUNITY COLLEGE")
    driver.find_element(By.ID, "loginPassword").send_keys(settings.LCTCS_PASS)
    driver.find_element(By.ID, "loginLogin").send_keys("greenbean")
    submit = driver.find_element(By.NAME, "btnLogin")
    submit.click()
    submit.click()
    return driver


def get_program(student_id):
    try:
        student = Student.objects.get(WRU_ID=student_id)
        try:
            tests = student.tests
            program_from_test = {
                "Tabe": "CCR",
                "Clas_E": "ELL"
            }
            if tests.last_test_type in program_from_test:
                return program_from_test[tests.last_test_type]
            else:
                try:
                    program = student.classes.latest('pk').section.program
                    return program
                except ObjectDoesNotExist:
                    return "No Tests or Classes"
        except ObjectDoesNotExist:
            return "TestHistory not found"
    except ObjectDoesNotExist:
        return "Student not found"

def wru_program_needs_updating(csv_filename):
    with open(csv_filename, "rt", newline="") as review, open("student_programs.csv", "w", newline="") as output:
        reader = csv.reader(review)
        out = csv.writer(output)

        for row in reader:
            record = row
            if row[0] == "StudentId":
                record.append("Program")
            else:
                record.append(get_program(row[0]))
            out.writerow(record)

def get_required_fields(student_id, program):
    wioa = WIOA.objects.get(student__WRU_ID=student_id)
    if len(wioa.student.ec_phone) != 12:
        ec_phone = 5045555555
    else:
        ec_phone = wioa.student.ec_phone.replace("-", "")
        ec_phone = ec_phone.replace(" ", "")
        try:
            ec_phone = int(ec_phone)
        except ValueError:
            ec_phone = 5045555555

    if wioa.referred_by == '':
        referred_by = 15
    else:
        referred_by = wioa.referred_by
    required = {
        '1': {
            'input': {
                "Emergency.FirstName": ec_name(wioa.student.emergency_contact)[0],
                "Emergency.LastName": ec_name(wioa.student.emergency_contact)[1],
                'Emergency.Telephone1': ec_phone
            },
            'select': {
                'Address.City': wioa.student.city,
                'Emergency.RelationshipId': ec_relation(wioa.student.ec_relation)
            },
        'cities': [wioa.student.city, wioa.student.other_city]
        },
        '4': {
            'input': {},
            'select': {'StudentWIOADetail.PrimaryGoal': wioa.student.primary_goal}
        },
        '6': {
            'input': {},
            'select': {'StudentWIOADetail.ReferredBy': referred_by}
        },
        '7': {
            'input': {},
            'select': {'Program.ProgramTypeId': WRU_PROGRAMS[program]}
        }
    }
    if required['1']['input']['Emergency.FirstName'] == '':
        required['1']['input']['Emergency.FirstName'] = 'NA'
    if required['1']['input']['Emergency.LastName'] == '':
        required['1']['input']['Emergency.LastName'] = 'NA'
    if wioa.student.city not in [c[0] for c in Student.CITY_CHOICES]:
        required['1']['select']["Address.City"] = "Other"
        required['1']['input']["Address.OtherCity"] = wioa.student.other_city
    if wioa.student.city == "Metairie":
        required['1']['select']["Address.City"] = "Other"
        required['1']['input']["Address.OtherCity"] = wioa.student.city
    emp_status = employment_status(wioa.current_employment_status)
    if emp_status in ["1_EM", "11_EMR"]:
        employer = wioa.employer if wioa.employer != '' else 'not provided'
        occupation = wioa.occupation if wioa.occupation != '' else 'not provided'
        required['3'] = {
            'input': {
                'EnrollPStat.EmploymentLocation': employer,
                'EnrollPStat.Occupation': occupation
            },
            'select': {}
        }
    return required

def complete_step(driver, step, step_dict):
    wait = WebDriverWait(driver, 10)
    if step != "1":
        driver.find_element(By.XPATH, "//body").send_keys(Keys.CONTROL + Keys.HOME)
        wait.until(EC.element_to_be_clickable((By.ID, step)))
        driver.find_element(By.ID, step).click()
    for name, value in step_dict['select'].items():
        field = driver.find_element(By.NAME, name)
        Select(field).select_by_value(str(value))
    for name, value in step_dict['input'].items():
        field = driver.find_element(By.NAME, name)
        if name == "Emergency.Telephone1":
            field.send_keys(Keys.CONTROL + 'a')
            field.send_keys(Keys.BACKSPACE)
            field.send_keys(value)
        else:
            field.send_keys(value)


def update_wru_program(student_id, driver, program):
    wait = WebDriverWait(driver, 60)
    sid = driver.find_element(By.ID, "StudentId")
    sid.clear()
    sid.send_keys(student_id)
    driver.find_element(By.ID, 'btnFilter').click()
    required = get_required_fields(student_id, program)
    modal_loader = (By.XPATH, "//div[contains(@class, 'modal loader')]")
    wait.until(EC.invisibility_of_element_located(modal_loader))
    edit_link = (By.XPATH, "//a[contains(@href, 'EditWithWIOA')]")
    wait.until(EC.element_to_be_clickable(edit_link))
    driver.find_element(By.XPATH, "//a[contains(@href, 'EditWithWIOA')]").click()
    wait.until(EC.title_is("LCTCS | Student Edit Form"))
    for step, step_dict in required.items():
        complete_step(driver, step, step_dict)
    driver.find_element(By.ID, "btnSave").click()
    validation_errors = driver.find_element(By.ID, "lblValidationMessages")
    return validation_errors.text

def process_program_updates(input_filepath):
    with open(input_filepath, 'rt', newline="") as file, open("not_finished.csv", 'w', newline="") as out:
        reader = csv.reader(file)
        writer = csv.writer(out)

        driver = state_webdriver()
        driver.get("https://workreadyu.lctcs.edu/Student/Index1")
        status = driver.find_element(By.ID, "Status")
        Select(status).select_by_visible_text('All')
        for row in reader:
            if row[0] == "WRU ID":
                row.append("Errors")
                writer.writerow(row)
                continue
            wait = WebDriverWait(driver, 60)
            wait.until(EC.title_is("LCTCS | Index1"))
            wait.until(EC.element_to_be_clickable((By.ID, "StudentId")))
            student_id, program = row[0], row[4]
            validation_errors = update_wru_program(student_id, driver, program)
            if validation_errors != '':
                row.append(validation_errors)
                writer.writerow(row)
                driver.back()
            else:
                print(f"Completed updating student {student_id}")
