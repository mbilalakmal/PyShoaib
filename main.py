# import firebase_admin
import time
from threading import Thread
from flask import Flask, request, escape, render_template
from flask_sockets import Sockets
# from firebase_admin import credentials
# from firebase_admin import firestore
# Local Imports
from schedule import Schedule
from resources import Resources
from parameters import Parameters

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)
sockets = Sockets(app)

# Use a service account
# firebase_admin.initialize_app()

# db = firestore.client()

# Websockets
@sockets.route('/chat')
def chat_socket(ws):
    while not ws.closed:
        message = ws.receive()
        if message is None:  # message is "None" if the client has closed.
            continue
        # Send the message to all clients connected to this webserver
        # process. (To support multiple processes or instances, an
        # extra-instance storage or messaging system would be required.)
        clients = ws.handler.server.clients.values()
        for client in clients:
            client.ws.send(message)


# @app.route('/', methods=['POST'])
# def generate_timetable():
#     # Background Example
#     def do_work(value):
#         # do something that takes a long time
#         time.sleep(value)
#         print("Background function completed")
#     thread = Thread(target=do_work, kwargs={
#                     'value': request.args.get('value', 5)})
#     thread.start()
#     # Firestore example
#     users_ref = db.collection(u'constraints')
#     docs = users_ref.stream()
#     for i in range(50):
#         print(i)
#     # for doc in docs:
#     #     print(u'{} => {}'.format(doc.id, doc.to_dict()))
#     # Request example
#     request_json = request.get_json(silent=True)
#     request_args = request.args
#     if request_json and 'name' in request_json:
#         name = request_json['name']
#     elif request_args and 'name' in request_args:
#         name = request_args['name']
#     else:
#         name = 'World'
#     return 'Hello {}!'.format(escape(name))

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # app.run(host='127.0.0.1', port=8080, debug=True)
    print("""
            This can not be run directly because the Flask development server does not
            support web sockets. Instead, use gunicorn:
            gunicorn -b 127.0.0.1:8080 -k flask_sockets.worker main:app
            Ensure that you have exported the credentials for Firebase:
            export GOOGLE_APPLICATION_CREDENTIALS=./serviceAccount.json
    """)
# [END gae_python37_app]
