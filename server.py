from datetime import datetime
from flask import Flask, render_template, send_from_directory, request, redirect, Markup
import csv, os
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
        # found = db.Contact.find_one({'email':data['email']}) 
        # if found:
        #     counter = found['counter'] + 1
        #     db.Contact.update_one({'email':data['email']}, {'$set':{'subject':data['subject'], 'message':data['message'], 'counter':counter, 'date':datetime.now().strftime("%d/%m/%Y, %H:%M:%S") }})
        # else:
        #     db.Contact.insert_one({'email':data['email'], 'subject':data['subject'], 'message':data['message'], 'counter':1, 'date':datetime.now().strftime("%d/%m/%Y, %H:%M:%S")})

        write_to_csv(data)
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

def write_to_csv(data):
    with open('database.csv', newline='' ,mode='a') as f:
        csv_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        csv_writer.writerow([datetime.now().strftime("%d/%m/%Y, %H:%M:%S"), data['email'],data['subject'],data['message']])
