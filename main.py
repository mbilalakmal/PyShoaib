import time
import json
from json import JSONDecodeError
from threading import Thread
from flask import Flask
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
timetables_progress = 0  # Current timetables progress
clients = None  # Reference to all the clients connected

# Only one endpoint for everything
@sockets.route('/connect')
def connect(ws):
    global clients
    while not ws.closed:
        request_string = ws.receive()
        if request_string is None:  # message is "None" if the client has closed.
            continue
        try:
            request_json = json.loads(request_string)
            message = request_json['message']
            clients = ws.handler.server.clients.values()
            # Respond to client based on message
            if message == 'get-generating':
                response = get_generating()
            elif message == 'generate-timetables':
                response = generate_timetables()
            elif message == 'get-timetables-progress':
                response = get_timetables_progress()
            elif message == 'get-timetables':
                response = get_timetables()
            elif message == 'delete-timetables':
                response = delete_timetables()
            else:
                response = {
                    "code": 404,
                    "message": 'unknown-message-received'
                }
        except JSONDecodeError:
            response = {
                "code": 400,
                "message": "could-not-parse-json"
            }
        # Send the message to all clients connected to this webserver
        # process. (To support multiple processes or instances, an
        # extra-instance storage or messaging system would be required.)
        for client in clients:
            client.ws.send(json.dumps(response))


def get_generating():
    return {
        "code": 200,
        "message": 'attached-is-generating-status',
        "generating": generating
    }


def get_timetables_progress():
    return {
        "code": 200,
        "message": 'attached-are-timetables-progresses',
        "timetablesProgress": timetables_progress
    }


def generate_in_background(value):
    global generating
    global generated
    global timetables_progress
    # do something that takes a long time
    for i in range(4):
        time.sleep(value)
        timetables_progress += 25
        try:
            for client in clients:
                client.ws.send(json.dumps({
                    "code": 201,
                    "message": 'attached-are-timetables-progresses',
                    "timetablesProgress": timetables_progress
                }))
        except:
            print("Some error happened while sending stuff to clients")
    generating = False
    generated = True


def generate_timetables():
    global generating
    if generating:
        return {
            "code": 300,
            "message": 'generating-timetables'
        }
    if generated:
        return {
            "code": 301,
            "message": 'timetables-have-been-generated'
        }
    thread = Thread(
        target=generate_in_background,
        kwargs={
            'value': 5
        }
    )
    thread.start()
    # Succesfully started generating
    generating = True
    return {
        "code": 201,
        "message": 'started-generating-timetables'
    }


def get_timetables():
    if generating:
        return {
            "code": 302,
            "message": 'generating-timetables'
        }
    if generated:
        return {
            "code": 200,
            "message": 'attached-are-timetables',
            "timetables": [
                # CS Timetable
                [
                    # CS Lecture (Department is calculated using the coure)
                    {
                        "id": '07oOq6yVxgeM3Af0l1js',
                        "name": 'GR3',  # For ease only (GR1, C, B2)
                        "strength": 45,  # Strength for lecture
                        # Course reference - backend will implement symmetry function to ensure the referenced courses can also clash with this one
                        "courseId": 'um3MTOBhstk2h8nbruIa',
                        # Teacher reference
                        "teacherIds": ['8iJPHOKGicitf3iU1oUs'],
                        # Sections include
                        "atomicSectionIds": ["CS2018E2", "CS2018E1", "CS2018F1", "CS2018F2"],
                        "assignedSlots": [
                            {
                                "day": 0,
                                "roomId": "32sEbfyomtp6F5jprc5a",  # Room Reference
                                "time": 0
                            }
                        ]
                    }
                ]
            ]
        }
    return {
        "code": 404,
        "message": 'no-generated-timetables-found'
    }


def delete_timetables():
    global generated
    global timetables_progress
    if generating:
        # TODO: Stop generating
        return {
            "code": 304,
            "message": 'generating-timetables'
        }
    if generated:
        generated = False
        timetables_progress = 0
        return {
            "code": 203,
            "message": 'deleted-timetables'
        }
    return {
        "code": 405,
        "message": 'no-generated-timetables-found'
    }


if __name__ == '__main__':
    print("""
            This can not be run directly because the Flask development server does not
            support web sockets. Instead, use gunicorn:
            gunicorn -b 127.0.0.1:8080 -k flask_sockets.worker main:app
    """)
