from flask import Flask, render_template, request
import random, string, hashlib
from faker import Faker
import requests

app = Flask(__name__)
fake = Faker()

def generate_random_email():
    name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"{name}@signinid.com"

def generate_password():
    return fake.password()

def register_facebook(email, password, fname, lname, birthday):
    api_key = '882a8490361da98702bf97a021ddc14d'
    secret = '62f8ce9f74b12f84c123cc23437a4a32'
    gender = random.choice(['M', 'F'])

    params = {
        'api_key': api_key,
        'attempt_login': True,
        'birthday': birthday.strftime('%Y-%m-%d'),
        'client_country_code': 'EN',
        'fb_api_caller_class': 'com.facebook.registration.protocol.RegisterAccountMethod',
        'fb_api_req_friendly_name': 'registerAccount',
        'firstname': fname,
        'lastname': lname,
        'email': email,
        'password': password,
        'gender': gender,
        'locale': 'en_US',
        'method': 'user.register',
        'reg_instance': ''.join(random.choices(string.ascii_letters + string.digits, k=32)),
        'return_multiple_errors': True,
        'format': 'json'
    }

    sig = ''.join([f"{k}={v}" for k, v in sorted(params.items())])
    params['sig'] = hashlib.md5((sig + secret).encode()).hexdigest()

    try:
        res = requests.post("https://b-api.facebook.com/method/user.register", data=params)
        return res.json()
    except Exception as e:
        return {"error": str(e)}

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        email = generate_random_email()
        password = generate_password()
        fname = fake.first_name()
        lname = fake.last_name()
        birthday = fake.date_of_birth(minimum_age=18, maximum_age=40)

        fb_response = register_facebook(email, password, fname, lname, birthday)

        result = {
            "email": email,
            "password": password,
            "name": f"{fname} {lname}",
            "birthday": birthday.strftime('%Y-%m-%d'),
            "response": fb_response
        }
    return ("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
