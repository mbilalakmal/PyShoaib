import time
from threading import Thread
from flask import Flask, request, escape, render_template
from flask_sockets import Sockets
# Local Imports
from schedule import Schedule
from resources import Resources
from parameters import Parameters

# App settings
app = Flask(__name__)
sockets = Sockets(app)

# Global Variables
generating = False  # Currently busy
generated = False  # Waiting for user to get
timetable_progress = 0  # Current timetable progress


@app.route('/generating')
def get_generating():
    return str(generating)


def generate_in_background(value):
    # do something that takes a long time
    time.sleep(value)
    timetable_progress += 25
    print(timetable_progress)
    time.sleep(value)
    timetable_progress += 25
    print(timetable_progress)
    time.sleep(value)
    timetable_progress += 25
    print(timetable_progress)
    time.sleep(value)
    timetable_progress += 25
    print(timetable_progress)
    generating = False
    generated = True


@app.route('/generate-timetable', methods=['POST'])
def generate_timetable():
    if generating:
        return {
            code: 300,
            message: 'Generating timetable...'
        }
    if generated:
        return {
            code: 301,
            message: 'Timetable has been generated and is waiting to be downloaded.'
        }
    # TODO: Get request body and pass in function
    request_json = request.get_json(silent=True)
    if request_json is None:
        return {
            code: 400,
            message: 'The mimetype does not indicate JSON (application/json).'
        }
    thread = Thread(
        target=generate_in_background,
        kwargs={
            'value': request.args.get('value', 5)
        }
    )
    thread.start()
    # Succesfully started generating
    generating = True
    return {
        code: 201,
        message: 'Started generating timetable.'
    }

# HTTP endpoint to get the final timetable
@app.route('/get-timetable')
def get_final_timetable():
    if generating:
        return {
            code: 300,
            message: 'Generating timetable...'
        }
    if generated:
        return {
            code: 200,
            message: 'Timetable attached.'
        }
    return {
        code: 404,
        message: 'Could not find a generated timetable.'
    }

# WS endpoint for getting current progress
@sockets.route('/get-timetable')
def get_timetable(ws):
    while not ws.closed:
        message = ws.receive()
        if message is None:  # message is "None" if the client has closed.
            continue
        # Send the message to all clients connected to this webserver
        # process. (To support multiple processes or instances, an
        # extra-instance storage or messaging system would be required.)
        clients = ws.handler.server.clients.values()
        for client in clients:
            client.ws.send(message + str(timetable_progress))


@app.route('/delete-timetable')
def delete_timetable():
    if generating:
        # TODO: Stop generating
        return {
            code: 300,
            message: 'Generating timetable...'
        }
    if generated:
        generated = False
        timetable_progress = 0
        return {
            code: 203,
            message: 'Deleted timetable. You can now generate a new timetable.'
        }
    return {
        code: 404,
        message: 'No timetable has been generated yet.'
    }


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # app.run(host='127.0.0.1', port=8080, debug=True)
    print("""
            This can not be run directly because the Flask development server does not
            support web sockets. Instead, use gunicorn:
            gunicorn -b 127.0.0.1:8080 -k flask_sockets.worker main:app
    """)
# [END gae_python37_app]
