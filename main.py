import time
import json
from json import JSONDecodeError
from multiprocessing.dummy import Process
from flask import Flask
from flask_sockets import Sockets
# Local Imports
from resources_parser import extract_resources
from genetic_algorithm import GeneticAlgorithm
from parameters import Parameters

# App settings
app = Flask(__name__)
sockets = Sockets(app)

# Global Variables
generating = False  # Currently busy
generated = False  # Waiting for user to get
timetables = None  # Generated timetables
timetables_progresses = 0  # Current timetables progress
clients = None  # Reference to all the clients connected
thread = None  # Track generation

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
                response = generate_timetables(
                    extract_resources(request_json['timetableRequest'])
                )
            elif message == 'get-timetables-progress':
                response = get_timetables_progresses()
            elif message == 'cancel-generation':
                response = cancel_generation()
            elif message == 'get-timetables':
                response = get_timetables()
            elif message == 'delete-timetables':
                response = delete_timetables()
            elif message == 'prevent-timeout':
                continue
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
        broadcast_to_clients(response)


# Send the message to all clients connected to this webserver
# process. (To support multiple processes or instances, an
# extra-instance storage or messaging system would be required.)
def broadcast_to_clients(response):
    global clients
    try:
        for client in clients:
            client.ws.send(json.dumps(response))
    except TypeError:
        print('Type Error: ' + json.dumps(response))
    except:
        print("Some error happened while sending stuff to clients")


def get_generating():
    return {
        "code": 200,
        "message": 'attached-is-generating-status',
        "generating": generating
    }


def get_timetables_progresses():
    return {
        "code": 200,
        "message": 'attached-are-timetables-progresses',
        "timetablesProgresses": timetables_progresses
    }


def generate_in_background(resources):
    global generating
    global generated
    global timetables
    global timetables_progresses
    ga = GeneticAlgorithm(resources, Parameters())
    time.sleep(0)
    ga._initialize()
    while(
        ga.optimum_reached is False and
        ga.generation < ga.parameters.maximum_generations
    ):
        ga._reproduce()
        time.sleep(0)
        timetables_progresses = ga.best_fitness
        broadcast_to_clients({
            "code": 201,
            "message": 'attached-are-timetables-progresses',
            "timetablesProgresses": timetables_progresses
        })
        ga.generation += 1
    timetables = ga.best_schedule.to_dict()
    if ga.optimum_reached:
        generated = True
        broadcast_to_clients({
            "code": 200,
            "message": 'attached-are-timetables',
            "timetables": timetables
        })
    else:
        generated = False
        broadcast_to_clients({
            "code": 500,
            "message": 'max-generations-reached',
            "timetables": timetables
        })
    generating = False


def generate_timetables(resources):
    global thread
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
    # Starting generating
    generating = True
    timetables_progresses = 0
    thread = Process(
        target=generate_in_background,
        kwargs={
            'resources': resources
        }
    )
    thread.start()
    return {
        "code": 201,
        "message": 'started-generating-timetables'
    }


def get_timetables():
    global timetables
    if generating:
        return {
            "code": 302,
            "message": 'generating-timetables'
        }
    if generated:
        return {
            "code": 201,
            "message": 'attached-are-timetables',
            "timetables": timetables
        }
    return {
        "code": 404,
        "message": 'no-generated-timetables-found'
    }


def cancel_generation():
    if (thread and thread.is_alive()):
        try:
            thread.terminate()
            return {
                "code": 200,
                "message": 'canceled-timetables-generation'
            }
        except:
            return {
                "code": 400,
                "message": 'could-not-cancel-generation'
            }
    else:
        return {
            "code": 401,
            "message": 'could-not-cancel-generation'
        }


def delete_timetables():
    global generated
    global timetables_progresses
    if generating:
        # TODO: Stop generating
        return {
            "code": 304,
            "message": 'generating-timetables'
        }
    if generated:
        generated = False
        timetables_progresses = 0
        timetables = None
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
            gunicorn -b 127.0.0.1:8080 -k flask_sockets.worker -t 2147483647 main:app
    """)
