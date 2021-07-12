from datetime import datetime
from dateutil import relativedelta
from pathlib import Path
from flask import Flask, render_template, send_from_directory, request, redirect, Markup
import json, os, sys
from subprocess import Popen, PIPE
# python anywhere doesn't have pymongo on the whitelist for free accounts
#, pymongo

def read_json(json_file):
    with open(json_file, mode='r') as j_f:
        data = json.load(j_f)
    return data

def write_to_json(data):
    directory = 'responses'
    Path(directory).mkdir(parents=True, exist_ok=True)
    with open(os.path.join(directory, f'reponse.{datetime.now().strftime("%Y%m%d_%H-%M-%S")}.json'), mode='a') as f:
        json.dump(data, f)

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

nav_data = read_json(os.path.join(app.root_path, "Data", "Navigation.json"))
navigation_headers = ""
for i, nav in enumerate(nav_data):
    if os.path.isfile(os.path.join(app.root_path, 'templates', nav["Page"])):
        navigation_headers += f"""          <li><a href="{nav["Page"]}" title="{nav["Title"]}">{i+1:02d} : {nav["Title"]}</a></li>"""
    else:
        print(f"""{nav["Page"]} doesn't exist.""")

@app.route('/favicon.ico')
def favicon():
    # Saves specifying the favicon on each html page
    return send_from_directory(os.path.join(app.root_path, 'static', 'assets', 'images'), 'profile.ico')

@app.route('/')
def my_home():
    # return page()
    return render_template('index.html', nav=navigation_headers)

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
    if html_page == "works.html":
        data = read_json(os.path.join(app.root_path, "Data", "Projects.json"))
        projects = ""
        number_of_project = len(data)
        for i, project in enumerate(data):
            projects += f"""                    <div class="col-sm-4">
                      <a href="{project["url"]}" title="" class="black-image-project-hover">
                        <img src="{project["image"]}" alt="" class="img-responsive">
                      </a>
                      <div class="card-container card-container-lg">
                        <h4>{number_of_project-i:03d}/{number_of_project:03d}</h4>
                        <h3>{project["Title"]}</h3>
                        <p>{project["Description"]}</p>
                        <a href="{project["url"]}" title="" class="btn btn-default">Discover</a>
                      </div>
                    </div>\n"""
        
        return render_template(html_page, nav=navigation_headers, proj=projects)

    elif html_page == "Experience and Education.html":
        data = read_json(os.path.join(app.root_path, "Data", "Experience_and_Education.json"))
        
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
                          <h4>{company["Company"]}</h4>
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

        awards = "                  <section>"
        for award in data["Awards"]:
            award_list = "<ul>"
            for a in award["Awards"]:
                award_list += f"""<li>{a["Name"]}</li>"""
            award_list += "<ul>"
            awards += f"""<div class="column" style="white-space:normal">
                          <h4>{award["Location"]}</h4>
                          {award["Description"]}<br>
                          {award_list}
                      </div>"""

        awards += "                  </section>"

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
        return render_template(html_page, nav=navigation_headers, tech_skills=technical_skills, edu=education, awd=awards, exp=experience)
    else:
        return render_template(html_page, nav=navigation_headers)

@app.route('/submit_form', methods=['POST', 'GET'])
def submit_form():
    if request.method == "POST":
        data = request.form.to_dict()
        write_to_json(data)
        # TODO - add a means of emailing said person / notifying me this has happened
        try:
            if sys.platform == 'linux':
                process = Popen(['python', os.path.join(os.environ["HOME"], "Webpage-CV", "EmailResponses.py")], stdout=PIPE, stderr=PIPE)
                output = process.communicate()
                with open("process.out", "a") as f:
                    f.write("\n".join(output))
            else:
                Popen(['python', 'EmailResponses.py'])
        except Exception as e:
            print(e)
        return render_template('thank you.html', nav=navigation_headers, message=Markup('Submission successful!<br>I\'ll be in contact as soon as possible.'))
    else:
        return render_template('thank you.html', nav=navigation_headers, message='Something went wrong. Try again!')

@app.route('/Dom_di_Furia_CV', methods=['GET'])
def Dom_di_Furia_CV():
    if request.method == 'GET':
        return send_from_directory('static', 'Dom_di_Furia_CV.pdf')
    else:
        return 'Something went wrong. Try again!'