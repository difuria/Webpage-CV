import glob, json, os, smtplib, sys

# Currently have as a seperate script so this can also execute on a cron to pick up any times where this may have just failed because of being unable to connect to gmail

file_format = "*.json"
log_file = ""

def Log(msg):
    print(msg)

    with open(log_file, "a") as f:
        f.write(f"{msg}\n")    

gmail_info = {}
if sys.platform == 'linux':
    # The production system is linux, whereas the test system in windows
    ARCHIVE_DIR = os.path.expanduser("~/Archive")
    credentials = os.path.expanduser("~/credentials.json")
    RESPONSE_DIR = os.path.expanduser("~/responses/")
    log_file = os.path.expanduser("~/log")
else:
    ARCHIVE_DIR = "ARCHIVE"
    credentials = os.path.join(os.getcwd(), "credentials.json")
    RESPONSE_DIR = os.path.join(os.getcwd(), "responses") 
    log_file = "log"
files = glob.glob(os.path.join(RESPONSE_DIR, file_format))

print(os.getcwd(), glob.glob("*"))
if not os.path.exists(credentials):
    Log(f"Unable to find credentials file {credentials}")
    exit(1)
else:
    print("HERE", os.getcwd(), credentials)
    try:
        with open(credentials, "r") as f:
            gmail_info = json.load(f)
    except Exception as e:
        print(e)
        exit()

    print(gmail_info)

if not gmail_info:
    Log("Gmail Info Not Found")
    exit(1)
elif not ("username" in gmail_info and gmail_info["username"] and "password" in gmail_info and gmail_info["password"]):
    Log("Credentials not as expected")
    exit(1)

sent_from = gmail_info["username"]
sent_to = gmail_info["sent to"]
try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(gmail_info["username"], gmail_info["password"])
    for file in files:
        with open(file, "r") as f:
            data = json.load(f)
        if "email" not in data:
            Log(f"Unable to find email address in {file}")
            continue
        email_text = f"""From: {sent_from}
To: {sent_to}
Subject: {data["subject"]}

Message Sent From: {data["email"]}
{data["message"]}"""
        server.sendmail(sent_from, sent_to, email_text)
        # If we've notified of the addition of the file then remove it 
        #os.remove(file)
        if sys.platform == "linux":
            os.makedirs(os.path.expanduser("~/Archive"), exist_ok=True)
            os.rename(os.path.join(RESPONSE_DIR, file), os.path.join(ARCHIVE_DIR, os.path.basename(file)))    
    server.close()
    Log("Complete")
except Exception as e:
    Log(f'Something went wrong...\n{e}')