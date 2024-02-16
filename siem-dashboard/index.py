from flask import *
from Aadhar_OCR import Aadhar_OCR
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import ssl, smtplib, hashlib, uuid
from werkzeug.utils import secure_filename
import os
import psycopg2
import sys
sys.path.append(f"{os.path.dirname(os.getcwd())}/elements/src")
import pandas as pd

import datetime, json

app = Flask(__name__)
app.jinja_env.auto_reload = True
app.config["TEMPLATES_AUTO_RELOAD"] = True

DATABASE_URL = "postgresql://postgres:inr_db@db.inr.intellx.in/zeus"
CONNECTION = psycopg2.connect(DATABASE_URL)

@app.route('/')
def main():
    return redirect(url_for("dashboard"))

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")
    
@app.route('/dashboard/matrix', methods=['GET', 'POST'])
def dashboard_matrix():

    return render_template("crcf.html")

@app.route('/dashboard/SIEM/ongoing')
def dashboard_siem():

    cursor = CONNECTION.cursor()

    cursor.execute('SELECT * FROM events WHERE NOT RESOLVED;')

    headings = [desc[0] for desc in cursor.description]
    data_values = list(cursor.fetchall())

    data = [{heading: value for heading, value in zip(headings, data)} for data in data_values]

    return render_template("SIEM/ongoing.html", data = data)

@app.route('/dashboard/SIEM/all')
def dashboard_siem_all():

    cursor = CONNECTION.cursor()

    cursor.execute('SELECT * FROM events;')

    headings = [desc[0] for desc in cursor.description]
    data_values = list(cursor.fetchall())

    data = [{heading: value for heading, value in zip(headings, data)} for data in data_values]

    return render_template("SIEM/all.html", data=data)

@app.route('/dashboard/SIEM/event/<id>', methods=['GET', 'POST'])
def event_view(id):

    if request.method == "POST":

        cursor = CONNECTION.cursor()

        cursor.execute('''
                INSERT INTO event_comments (
                        id,
                        user_id,
                        comment
                    )
                VALUES (
                        %s,
                        1,
                        %s
                    )
            ''', (id, request.form.get("desc")))

        CONNECTION.commit()

        return redirect(url_for('event_view', id=id))

    cursor = CONNECTION.cursor()

    cursor.execute('SELECT * FROM events WHERE id=%s;', (id,))

    headings = [desc[0] for desc in cursor.description]
    data_values = list(cursor.fetchall())

    data = [{heading: value for heading, value in zip(headings, data)} for data in data_values]

    event = data[0]

    days_passed = ((event["timestamp"] - datetime.datetime.now()).days) + 1

    event["days"] = abs(days_passed)
    event["timestamp"] = event["timestamp"].strftime('%b %d, %Y %I:%M %p')

    cursor.execute('SELECT * FROM event_comments WHERE event_id=%s;', (id,))

    headings = [desc[0] for desc in cursor.description]
    data_values = list(cursor.fetchall())

    event["comments"] = [{heading: value for heading, value in zip(headings, data)} for data in data_values]

    return render_template("SIEM/event.html", event = event)

@app.route('/dashboard/SIEM/create', methods=['GET', 'POST'])
def dashboard_siem_create():
    if request.method == "POST":

            cursor = CONNECTION.cursor()

            cursor.execute('''
                INSERT INTO events (
                        event_type,
                        description,
                        source_device,
                        man_interv
                    )
                VALUES (
                        %s,
                        %s,
                        %s,
                        True
                    )
            ''', (request.form.get("type"), request.form.get("desc"), request.form.get("name")))

            CONNECTION.commit()

            return redirect(url_for('dashboard_siem'))

    return render_template("SIEM/create.html")

@app.route('/dashboard/resolve/<id>')
def dashboard_siem_resolve(id):

    cursor = CONNECTION.cursor()

    cursor.execute('UPDATE events SET resolved = true, resolution_timestamp = %s WHERE id=%s;', (datetime.datetime.now(),id,))

    CONNECTION.commit()

    return redirect(url_for("event_view", id=id))

@app.route('/dashboard/faces')
def dashboard_facedb():
    cursor = CONNECTION.cursor()

    cursor.execute('SELECT * FROM faces;')

    headings = [desc[0] for desc in cursor.description]
    data_values = list(cursor.fetchall())

    data = [{heading: value for heading, value in zip(headings, data)} for data in data_values]


    return render_template("faces.html", data=data)

app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit upload size to 16MB

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
@app.route('/validate/id', methods=['GET', 'POST'])
def validate_id():
    if request.method == 'POST':
        file = request.files.get('id_card')
        if file and file.filename:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            aadhar_ocr = Aadhar_OCR(file_path)
            details = aadhar_ocr.extract_data()
            if details:
                return render_template('validate_id.html', details=details, valid=True)
            else:
                return render_template('validate_id.html', valid=False)
        else:
            return redirect(request.url)
    return render_template('validate_id.html')

from cam import verify_image_with_model

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Flask route for image validation
@app.route('/validate/photo', methods=['GET', 'POST'])
def validate_photo():
    if request.method == 'POST':
        file = request.files.get('image_file')
        if file and file.filename:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            # Proceed to verify the image using your model
            verification_result = verify_image_with_model(file_path)
            # Render the verification result template with the result
            return render_template('upload_image_for_verification.html', verification_result=verification_result)
        else:
            return redirect(request.url)
    return render_template('upload_image_for_verification.html')
if __name__ == '__main__':    
    app.run(debug=True)
