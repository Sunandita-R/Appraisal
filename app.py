from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client.user_db
users = db.users

# Define the upload folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

# Ensure the uploads folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return redirect(url_for('login'))
@app.route('/personal_info')
def personal_info():
    return render_template('personal_info.html')

@app.route('/teaching_performance')
def teaching_performance():
    return render_template('academic_info.html')

@app.route('/research_work')
def research_work():
    return render_template('research_work.html')

@app.route('/extra_activities')
def extra_activities():
    return render_template('extra_activities.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users.find_one({'email': email, 'password': password})
        if user:
            session['user_id'] = str(user['_id'])
            return render_template('dashboard.html')
        else:
            return 'Invalid email or password.'
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        department_code = request.form['department_code']
        
        if users.find_one({'email': email}):
            return 'Email already registered.'
        
        user_id = users.insert_one({
            'name': name,
            'email': email,
            'password': password,
            'department_code': department_code
        }).inserted_id
        
        session['user_id'] = str(user_id)
        return render_template('dashboard.html')
    return render_template('signup.html')

@app.route('/academic_info', methods=['GET', 'POST'])
def academic_info():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        academic_info_list = []
        for i in range(len(request.form.getlist('subject_code'))):
            academic_info_list.append({
                'academic_year': request.form.getlist('academic_year')[i],
                'semester': request.form.getlist('semester')[i],
                'section': request.form.getlist('section')[i],
                'subject_code': request.form.getlist('subject_code')[i],
                'subject_name': request.form.getlist('subject_name')[i],
                'pass_percent': request.form.getlist('pass_percent')[i]
            })

        certificate = request.files['certificate']
        certificate_filename = None
        if certificate:
            certificate_filename = os.path.join(app.config['UPLOAD_FOLDER'], certificate.filename)
            certificate.save(certificate_filename)

        innovative_methods = request.form.getlist('innovative_methods')
        feedback = [{'subject_code': sc, 'feedback_percent': fp} for sc, fp in zip(request.form.getlist('feedback_subject_code'), request.form.getlist('feedback_percent'))]
        helping_students = request.form.getlist('helping_students')
        cat_duties = request.form.getlist('cat_duties')
        learning_materials = request.form.getlist('learning_materials')

        users.update_one(
            {'_id': ObjectId(session['user_id'])},
            {'$set': {
                'academic_info': academic_info_list,
                'certificate': certificate_filename,
                'innovative_methods': innovative_methods,
                'feedback': feedback,
                'helping_students': helping_students,
                'cat_duties': cat_duties,
                'learning_materials': learning_materials
            }}
        )


        return 'Academic information submitted successfully!'

    return render_template('academic_info.html')

@app.route('/personal_information', methods=['GET', 'POST'])
def personal_information():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Gather data from the form
        name = request.form['name']
        dob = request.form['dob']
        designation = request.form['designation']
        department = request.form['department']
        date_of_joining_college = request.form['date_of_joining_college']
        date_of_appointment_current = request.form['date_of_appointment_current']
        date_of_joining_department = request.form['date_of_joining_department']
        highest_qualification = request.form['highest_qualification']
        year_qualified = request.form['year_qualified']
        special_qualification = request.form['special_qualification']
        nature_of_appointment = request.form['nature_of_appointment']
        employee_id = request.form['employee_id']
        honors = request.form.getlist('honors')

        # Update the user's record in MongoDB
        users.update_one(
            {'_id': ObjectId(session['user_id'])},
            {'$set': {
                'personal_info': {
                    'name': name,
                    'dob': dob,
                    'designation': designation,
                    'department': department,
                    'date_of_joining_college': date_of_joining_college,
                    'date_of_appointment_current': date_of_appointment_current,
                    'date_of_joining_department': date_of_joining_department,
                    'highest_qualification': highest_qualification,
                    'year_qualified': year_qualified,
                    'special_qualification': special_qualification,
                    'nature_of_appointment': nature_of_appointment,
                    'employee_id': employee_id,
                    'honors': honors
                }
            }}
        )

        return 'Personal Information Updated Successfully!'

    return render_template('personal_info.html')
if __name__ == '__main__':
    app.run(debug=True)
