from flask import Flask, render_template, redirect, session, url_for, request, jsonify
from rauth import OAuth2Service
from user import User
import sys
from simplekv.memory import DictStore
from flask_kvsession import KVSessionExtension

import requests

app = Flask(__name__)
app.config.from_object('app_config')
app.secret_key=app.config['APP_SECRET']

store = DictStore()
KVSessionExtension(store, app)

ACCESS_TOKEN_SESSION_ID = 'uber_at'
USER_SESSION_ID = 'current_user'

@app.route('/')
def index():
    if ACCESS_TOKEN_SESSION_ID in session:
        if not 'current_user' in session:
            create_user_object()
    return render_template('index.html', user=session.get('current_user', None)))

@app.route('/login')
def login():
    """
        If credentials are valid, this returns redirects the user to Uber's login page
    """
    uber_auth_url = create_uber_auth()
    return redirect(uber_auth_url)

@app.route('/logout')
def logout():
    """
        Signs a user out and clears the session data
    """
    session.clear()
    return redirect(url_for('index'))

@app.route('/products')
def get_products():
    """
        Fetches the list of products from Uber
    """
    if ACCESS_TOKEN_SESSION_ID in session:
        products_data = requests.get(
            app.config['API_URL']+'products',
            headers={
                'Authorization': 'Bearer {0}'.format(session['uber_at'])
            },
            params={
                'latitude': 37.775818,
                'longitude': -122.418028,
            }
        ).json()
        return jsonify(products_data)
    return unauthorized_view("Unauthorized View")

@app.errorhandler(401)
def unauthorized_view(error=None):
    message = {
        'status': 401,
        'message': 'Error: ' + error,
    }
    resp = jsonify(message)
    resp.status_code = 401
    return resp


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
        session[ACCESS_TOKEN_SESSION_ID] = access_token
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

def create_user_object():
    """
        Creates a new User object and stores basic information in session
    """
    user_data = requests.get(
        app.config['API_URL']+'me',
        headers={
            'Authorization': 'Bearer {0}'.format(session[ACCESS_TOKEN_SESSION_ID])
        }
    ).json()
    session['current_user'] = user_data
    print('Session size: ' + str(sys.getsizeof(session['current_user'])))

def check_authorized_session():
    """
        Returns True if access token is present
    """
    return ACCESS_TOKEN_SESSION_ID in session

if __name__ == '__main__':
    app.run()
