import firebase_admin
import time
from threading import Thread
from flask import Flask, request, escape
from firebase_admin import credentials
from firebase_admin import firestore
# Local Imports
from schedule import Schedule
from resources import Resources
from parameters import Parameters

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)

# Use a service account
cred = credentials.Certificate('./serviceAccount.json')
firebase_admin.initialize_app(cred)

db = firestore.client()


@app.route('/', methods=['POST'])
def generate_timetable():
    # Background Example
    def do_work(value):
        # do something that takes a long time
        time.sleep(value)
        print("Background function completed")
    thread = Thread(target=do_work, kwargs={
                    'value': request.args.get('value', 5)})
    thread.start()
    # Firestore example
    users_ref = db.collection(u'constraints')
    docs = users_ref.stream()
    for doc in docs:
        print(u'{} => {}'.format(doc.id, doc.to_dict()))
    # Request example
    request_json = request.get_json(silent=True)
    request_args = request.args
    if request_json and 'name' in request_json:
        name = request_json['name']
    elif request_args and 'name' in request_args:
        name = request_args['name']
    else:
        name = 'World'
    return 'Hello {}!'.format(escape(name))


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python37_app]
