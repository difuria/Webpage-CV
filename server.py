from datetime import datetime
from dateutil import relativedelta
from pathlib import Path
from flask import Flask, render_template, send_from_directory, request, redirect, Markup
import json, os
# python anywhere doesn't have pymongo on the whitelist for free accounts
#, pymongo
app = Flask(__name__)
"""
Activate virtual environment
.\\venv\\Scripts\\activate

To kick off the server
set FLASK_APP=server.py
$env:FLASK_APP = "server.py"
set FLASK_ENV=development
$env:FLASK_ENV="development"

Start server
python -m  flask run
"""

# client = pymongo.MongoClient("mongodb+srv://website_cv:<password>@website-cv.k6hua.mongodb.net/Website-CV?retryWrites=true&w=majority")
# db = client['Website-CV'] 
# mycol = db["Client"] 

@app.route('/favicon.ico')
def favicon():
    # Saves specifying the favicon on each html page
    return send_from_directory(os.path.join(app.root_path, 'static', 'assets', 'images'), 'profile.ico')

@app.route('/')
def my_home():
    return render_template('index.html')

def get_duration(start_date):
    duration_string = ''
    current_date = datetime.now()
    duration_time = relativedelta.relativedelta(current_date, start_date) 
    if duration_time.years > 0:
        duration_string += f'{duration_time.years} year'
        if duration_time.years > 1:
            duration_string += 's'
        duration_string += ' '
    
    if duration_time.months > 0:
        duration_string += f'{duration_time.months} month'
        if duration_time.months > 1:
            duration_string += 's'
        duration_string += ' '
    
    if not duration_string:
        if duration_time.days < 1:
            duration_string = 'First day'
        else:
            duration_string += f'{duration_time.days} day'
            if duration_time.days > 1:
                duration_string += 's'
    
    return duration_string.strip()

@app.route('/<string:html_page>')
def page(html_page="index.html"):
    if html_page == "Experience and Education.html":
        return render_template(html_page, company_duration=get_duration(datetime(2014,11,24)), role_duration=get_duration(datetime(2021,1,1)))
    else:
        return render_template(html_page)

@app.route('/submit_form', methods=['POST', 'GET'])
def submit_form():
    if request.method == "POST":
        # Store data so we can see who contacted, when they last contacted and possibly how many times they have contacted
        # Check first to see if this email has submitted before, if so update what's stored instead of adding further information. 
        data = request.form.to_dict()
        # found = db.Contact.find_one({'email':data['email']}) 
        # if found:
        #     counter = found['counter'] + 1
        #     db.Contact.update_one({'email':data['email']}, {'$set':{'subject':data['subject'], 'message':data['message'], 'counter':counter, 'date':datetime.now().strftime("%d/%m/%Y, %H:%M:%S") }})
        # else:
        #     db.Contact.insert_one({'email':data['email'], 'subject':data['subject'], 'message':data['message'], 'counter':1, 'date':datetime.now().strftime("%d/%m/%Y, %H:%M:%S")})

        write_to_json(data)
        # TODO - add a means of emailing said person / notifying me this has happened
        return render_template('thank you.html', message=Markup('Submission successful!<br>I\'ll be in contact as soon as possible.'))
    else:
        return render_template('thank you.html', message='Something went wrong. Try again!')

@app.route('/Dom_di_Furia_CV', methods=['GET'])
def Dom_di_Furia_CV():
    if request.method == 'GET':
        return send_from_directory('static', 'Dom_di_Furia_CV.pdf')
    else:
        return 'Something went wrong. Try again!'

def write_to_json(data):
    directory = 'responses'
    Path(directory).mkdir(parents=True, exist_ok=True)
    with open(os.path.join(directory, f'reponse.{datetime.now().strftime("%Y%m%d_%H-%M-%S")}.json'), mode='a') as f:
        json.dump(data, f)
