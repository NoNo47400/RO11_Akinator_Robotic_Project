from naoqi import ALProxy, ALModule, ALBroker
import sys
import time
import zmq 

# --- Setup ZMQ Client ---
context = zmq.Context()
print("Connecting to Akinator server...")
socket = context.socket(zmq.REQ) # REQ = Request
socket.connect("tcp://akinator_server:5555")

# --- Naoqi Setup ---
robot_ip = "192.168.2.121" # Real robot IP
robot_port = 9559
list_of_words = ["yes", "no", "i don't know"] # We'll only handle these three answers

try:
    broker = ALBroker("myBroker", "0.0.0.0", 0, robot_ip, robot_port)
    print("ALBroker created.")
except RuntimeError:
    print("Could not connect to Naoqi. Check robot_ip and Choregraphe.")
    sys.exit(1)

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

print("Attempting to create proxies...") 
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
    # Send to akinator server to get the first question
    print("Sending initial 'next_q' to get first question...")
    socket.send_string("next_q")
    question = socket.recv_string()

    while True:
        if question.startswith("FINAL:"):
            # End of the game, akinator sent the guess
            guess = question.replace("FINAL:", "")
            print("Final guess: " + guess)
            tts.say(str("Are you thinking about " + guess))
            break

        print(question)
        tts.say(str(question))
        
        # Wait for speech input
        while not obj_recognition.new_value:
            time.sleep(0.1)
        obj_recognition.new_value = False
        
        if obj_recognition.value.lower() == "stop":
            print("User requested STOP.")
            break # Go to "finally" section

        # Send the answer back to the akinator server
        print("Sending answer: " + obj_recognition.value.lower())
        socket.send_string(obj_recognition.value.lower())
        
        # Receive the next question OR the final guess
        question = socket.recv_string() 


finally:
    # Sending "STOP" to close both containers.
    print("Game over. Sending final STOP signal.")
    socket.send_string("STOP") 
    broker.shutdown()
    sys.exit(0)


