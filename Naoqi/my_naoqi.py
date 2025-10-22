from naoqi import ALProxy, ALModule, ALBroker
import sys
import time
import zmq 

# --- Setup ZMQ Client ---
context = zmq.Context()
print("Connecting to Akinator server...")
socket = context.socket(zmq.REQ) # REQ = Request
socket.connect("tcp://akinator_server:5555")

#robot_ip = "host.docker.internal"  # Only for simulation
robot_ip = "192.168.2.121" # Real robot IP
robot_port = 9559
list_of_words = ["yes", "no", "i don't know"]

# Create a broker to handle modules and events
broker = ALBroker("myBroker", "0.0.0.0", 0, robot_ip, robot_port)
print("ALBroker created. Waiting a bit...")
time.sleep(2) # Wait for everything to settle (SpeechRecognition etc...)
print("Attempting to create proxies...") 

class SpeechRecognitionModule(ALModule):
    def __init__(self, name):
        ALModule.__init__(self, name)
        self.memory = ALProxy("ALMemory", robot_ip, robot_port)
        self.new_value = False
        self.value = ""

    def onWordRecognized(self, keyValue):
        word = keyValue[0]
        confidence = keyValue[1]
        print("Recognized word: {0} with confidence {1}".format(word, confidence))
        self.new_value = True
        self.value = word

# Instantiate objects
speech_recog = ALProxy("ALSpeechRecognition", robot_ip, robot_port) # Not working in simulation because no microphone
tts = ALProxy("ALTextToSpeech", robot_ip, robot_port)
memory = ALProxy("ALMemory", robot_ip, robot_port)
obj_recognition = SpeechRecognitionModule("SpeechRecognitionModule")

# Configure speech recognition
speech_recog.pause(True)
speech_recog.setVocabulary(list_of_words, False) # Help reduce false positives
speech_recog.pause(False)

# Subscribe once before the loop
speech_recog.subscribe("SpeechRecognitionModule")
memory.subscribeToEvent("WordRecognized", "SpeechRecognitionModule", "onWordRecognized")

try:  
    while True:
        # Request the next question from the Py3 server
        socket.send_string("next_q")
        
        # Get the question
        question = socket.recv_string()

        if question.startswith("FINAL:"):
            # Game is over
            guess = question.replace("FINAL:", "")
            print("Final guess: " + guess)
            tts.say("Are you thinking about " + guess)
            break

        print(question)
        tts.say(question)
        
        # Wait for speech input
        while not obj_recognition.new_value:
            time.sleep(0.1)
        obj_recognition.new_value = False
        
        # Send the answer back to the Py3 server
        print("Sending answer: " + obj_recognition.value.lower())
        socket.send_string(obj_recognition.value.lower())
        
        # Receive the confirmation (the next question) in the next loop
        _ = socket.recv_string() # This will be the next question, but we'll grab it at the top of the loop


finally:
    socket.send_string("STOP") # Tell the server to shut down
    broker.shutdown()
    sys.exit(0)