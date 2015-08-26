from flask import Flask, render_template, redirect, session, url_for, request, jsonify
from rauth import OAuth2Service
from user import User
import requests

app = Flask(__name__)
app.config.from_object('app_config')
app.secret_key=app.config['APP_SECRET']

@app.route('/')
def index():
    current_user = session.get('current_user', None)
    if 'uber_at' in session:
        if not current_user:
            current_user = create_user_object()
    return render_template('index.html', user=current_user)

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
    session.pop('current_user')
    session.pop('uber_at')
    return redirect(url_for('index'))

@app.route('/products')
def get_products():
    """
        Fetches the list of products from Uber
    """
    if 'uber_at' in session:
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
        session['uber_at'] = access_token
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
            'Authorization': 'Bearer {0}'.format(session['uber_at'])
        }
    ).json()
    session['current_user'] = user_data
    return user_data

if __name__ == '__main__':
    app.run()
