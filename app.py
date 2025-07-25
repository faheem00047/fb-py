from flask import Flask, render_template, request
import requests, random, string, hashlib
from faker import Faker

app = Flask(__name__)
fake = Faker()

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def get_mail_domain():
    try:
        res = requests.get("https://api.mail.tm/domains")
        return res.json()['hydra:member'][0]['domain']
    except:
        return None

def create_mail_account():
    domain = get_mail_domain()
    if not domain:
        return None

    username = generate_random_string()
    password = fake.password()
    address = f"{username}@{domain}"
    data = {"address": address, "password": password}

    try:
        res = requests.post("https://api.mail.tm/accounts", json=data)
        if res.status_code == 201:
            return {
                "email": address,
                "password": password,
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "birthday": fake.date_of_birth(minimum_age=18, maximum_age=45)
            }
    except Exception as e:
        print(e)
    return None

def register_fake_facebook(email, password, fname, lname, birthday):
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
        'reg_instance': generate_random_string(32),
        'return_multiple_errors': True,
        'format': 'json'
    }

    sig = ''.join([f"{k}={v}" for k, v in sorted(params.items())])
    params['sig'] = hashlib.md5((sig + secret).encode()).hexdigest()

    try:
        res = requests.post('https://b-api.facebook.com/method/user.register', data=params)
        return res.json()
    except:
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        account = create_mail_account()
        if account:
            fb_response = register_fake_facebook(
                account["email"], account["password"],
                account["first_name"], account["last_name"], account["birthday"]
            )
            result = {
                "email": account["email"],
                "password": account["password"],
                "name": f"{account['first_name']} {account['last_name']}",
                "birthday": account["birthday"].strftime('%Y-%m-%d'),
                "response": fb_response
            }
        else:
            result = {"error": "Failed to create email account"}
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
