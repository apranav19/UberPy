from flask import Flask, render_template, redirect, session, url_for, request
from rauth import OAuth2Service
from user import User
import requests

app = Flask(__name__)
app.config.from_object('app_config')
app.secret_key=app.config['APP_SECRET']

@app.route('/')
def index():
    if 'uber_at' in session:
        return redirect(url_for('profile'))
    return render_template('index.html')

@app.route('/test_profile')
def test_profile():
    return render_template('profile.html')

@app.route('/profile')
def profile():
    if 'uber_at' in session:
        data = requests.get(
            app.config['API_URL']+'me',
            headers={
                'Authorization': 'Bearer {0}'.format(session['uber_at'])
            }
        ).json()
        current_user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            picture=data['picture']
        )
        return render_template('profile.html', user=current_user)
    return redirect(url_for('index'))

@app.route('/login')
def login():
    """
        If credentials are valid, this returns redirects the user to Uber's login page
    """
    uber_auth_url = create_uber_auth()
    return redirect(uber_auth_url)

@app.route('/callback')
def login_redirect():
    parameters = {
        'redirect_uri': app.config['REDIRECT_URI'],
        'code': request.args.get('code', None),
        'grant_type': 'authorization_code',
    }

    response = requests.post(
        app.config['UBER_ACCESS_TOKEN_URL'],
        auth=(
            app.config['CLIENT_ID'],
            app.config['CLIENT_SECRET'],
        ),
        data=parameters,
    )

    access_token = response.json().get('access_token')
    if access_token:
        session['uber_at'] = access_token
        return redirect(url_for('profile'))
    return redirect(url_for('index'))

def create_uber_auth():
    """
        Returns an OAuth2Service object that contains the required credentials
    """
    uber_obj = OAuth2Service(
        client_id=app.config['CLIENT_ID'],
        client_secret=app.config['CLIENT_SECRET'],
        name=app.config['APP_NAME'],
        authorize_url=app.config['UBER_AUTH_URL'],
        access_token_url=app.config['UBER_ACCESS_TOKEN_URL'],
        base_url=app.config['API_URL']
    )

    uber_params = {
        'response_type': 'code',
        'redirect_uri': app.config['REDIRECT_URI'],
        'scope': 'profile',
    }

    return uber_obj.get_authorize_url(**uber_params)

if __name__ == '__main__':
    app.run()
