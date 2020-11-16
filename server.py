from datetime import datetime
from flask import Flask, render_template, send_from_directory, request, redirect, Markup
import os, pymongo
app = Flask(__name__)
"""
To kick off the server
set FLASK_APP=server.py
$env:FLASK_APP = "server.py"
set FLASK_ENV=development
$env:FLASK_ENV="development"

Start server
python -m  flask run
"""

client = pymongo.MongoClient("mongodb+srv://website_cv:xP3W1F4CWKDgIXcy@website-cv.k6hua.mongodb.net/Website-CV?retryWrites=true&w=majority")
db = client['Website-CV'] 
# mycol = db["Client"] 

@app.route('/')
def my_home():
    return render_template('index.html')

@app.route('/<string:html_page>')
def page(html_page="index.html"):
    return render_template(html_page)

@app.route('/submit_form', methods=['POST', 'GET'])
def submit_form():
    if request.method == "POST":
        # Store data so we can see who contacted, when they last contacted and possibly how many times they have contacted
        # Check first to see if this email has submitted before, if so update what's stored instead of adding further information. 
        data = request.form.to_dict()
        found = db.Contact.find_one({'email':data['email']}) 
        if found:
            counter = found['counter'] + 1
            db.Contact.update_one({'email':data['email']}, {'$set':{'subject':data['subject'], 'message':data['message'], 'counter':counter, 'date':datetime.now().strftime("%d/%m/%Y, %H:%M:%S") }})
        else:
            db.Contact.insert_one({'email':data['email'], 'subject':data['subject'], 'message':data['message'], 'counter':1, 'date':datetime.now().strftime("%d/%m/%Y, %H:%M:%S")})

        # TODO - add a means of emailing said person / notifying me this has happened
        return render_template('thank you.html', message=Markup('Submission successful!<br>I\'ll be in contact as soon as possible.'))
    else:
        return render_template('thank you.html', message='Something went wrong. Try again!')

@app.route('/download_cv', methods=['GET'])
def download_cv():
    if request.method == 'GET':
        return send_from_directory('static', 'Dom_di_Furia_CV.pdf')
    else:
        return 'Something went wrong. Try again!'