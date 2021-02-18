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

def get_duration(start_date, end_date=None):
    duration_string = ''

    if not end_date:
        end_date = datetime.now()

    duration_time = relativedelta.relativedelta(end_date, start_date) 
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
        with open("Experience_and_Education.json") as json_file:
            data = json.load(json_file)
        
        experience = "                  <section>"
        for company in data["Experience"]:
            company_start_date = datetime.now()
            company_end_date = None
            roles = ""
            for role in company["Roles"]:
                role_start_date = datetime.strptime(role["Start Date"], "%d/%m/%Y")
                s_d = role_start_date.strftime("%b %Y")
                if role["End Date"]:
                    role_end_date = datetime.strptime(role["End Date"], "%d/%m/%Y")
                    e_d = role_end_date.strftime("%b %Y")
                else:
                    role_end_date = datetime.now()
                    e_d = "Present"

                if company_start_date > role_start_date:
                    company_start_date = role_start_date
                if not company_end_date or company_end_date < role_end_date:
                    company_end_date = role_end_date

                roles += f"""                    <div class="row">
                      <h4>{role["Role"]}</h4>
                    </div>
                    <div class="row">
                      {s_d} - {e_d} ({get_duration(role_start_date, role_end_date)})
                    </div>"""

                if role["Location"]:
                    roles += f"""                    <div class="row">
                      {role["Location"]}
                    </div>\n"""
                if role["Description"]:
                    role["Description"] = role["Description"].replace("\n", "\n<br>")
                    roles += f"""                    <div class="row">
                      <br>{role["Description"]}
                    </div>\n"""

            experience += f"""                    <div class="row">
                      <div class="column" style="white-space:normal">
                        <a href="{company["url"]}"><img src="static/assets/images/Logos/{company["Logo"]}" alt="" class="img-responsive" style="width:50px;height:50px" align="left"/></a>
                      </div>
                      <div class="column" style="white-space:normal">
                          <h4>Fidessa</h4>
                          {get_duration(company_start_date, company_end_date)}
                      </div>
                    </div>\n{roles}"""
        experience += "                  </section>"

        education = "                  <section>"
        for school in data["Education"]:
            start = datetime.strptime(school["Start Date"], "%m/%Y")
            end   = datetime.strptime(school["End Date"], "%m/%Y")
            duration   = get_duration(start, end)
            # Display date in short easy to ready form such as Jun 2009
            s_d = start.strftime("%b %Y")
            e_d = end.strftime("%b %Y")
            education += f"""                    <div class="row">
                      <div class="column" style="white-space:normal">
                        <a href="{school["url"]}"><img src="static/assets/images/Logos/{school["Logo"]}" alt="" class="img-responsive" style="width:50px;height:50px" align="left"/></a>
                      </div>
                      <div class="column" style="white-space:normal">
                          <h4>{school["School"]}</h4>
                          {duration}                       
                      </div>
                    </div>"""

            # Don't have a course in secondary school
            if school["Course"]:
                education += f"""                    <div class="row">
                      <h4>{school["Course"]}</h4>
                    </div>"""

            grades = school["Grades"].replace('\n', '\n<br>')
            education += f"""                    <div class="row">
                      {s_d} – {e_d}
                    </div>
                    <div class="row">
                      <p>{grades}</p>
                    </div>\n"""
        education += "                  </section>"

        technical_skills = ""
        for skill in data["Technical Skills"]:
            technical_skills += f"""                  <div class="row">
                    <div class="col-xs-3 col-md-2">
                      <p>{skill["Skill"]}</p>
                    </div>
                    <div class="col-xs-9 col-md-10">
                      <p>{skill["Description"]}</p>
                    </div>
                  </div>"""
        return render_template(html_page, company_duration=get_duration(datetime(2014,11,24)), role_duration=get_duration(datetime(2021,1,1)), tech_skills=technical_skills, edu=education, exp=experience)
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