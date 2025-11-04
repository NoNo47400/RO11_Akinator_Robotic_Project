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
list_of_words = ["yes", "no", "i don't know", "stop"]

try:
    broker = ALBroker("myBroker", "0.0.0.0", 0, robot_ip, robot_port)
    print("ALBroker created.")
except RuntimeError:
    print("Could not connect to Naoqi. Check robot_ip and Choregraphe.")
    sys.exit(1)
except Exception as e:
    print("An unexpected error occurred while creating ALBroker: {0}".format(e))
    sys.exit(1)

print("Attempting to create proxies...") 
# Instantiate objects
speech_recog = ALProxy("ALSpeechRecognition", robot_ip, robot_port) # Not working in simulation because no microphone
tts = ALProxy("ALTextToSpeech", robot_ip, robot_port)
memory = ALProxy("ALMemory", robot_ip, robot_port)

# Configure speech recognition
speech_recog.pause(True)
speech_recog.setVocabulary(list_of_words, False) # Help reduce false positives
speech_recog.pause(False)

sr_sub_name = "AkinatorSR"
speech_recog.subscribe(sr_sub_name)

try:  
    # Send to akinator server to get the first question
    print("Sending initial 'next_q' to get first question...")
    socket.send_string("next_q")
    question = socket.recv_string()

    # Helper: last observed word to avoid repeated triggers
    last_confidence = None    
    # Confidence threshold to reduce false positives (adjust if needed)
    CONF_THRESHOLD = 0.40

    while True:
        if question.startswith("FINAL:"):
            # End of the game, akinator sent the guess
            guess = question.replace("FINAL:", "")
            print("Final guess: " + guess)
            tts.say(str("Are you thinking about " + guess))
            break

        print(question)
        tts.say(str(question))
        
        # Loop until we get a valid recognized word meeting confidence and not same as last
        while True:
            try:
                data = memory.getData("WordRecognized")  # usually [word, confidence]
                print(data)
            except Exception:
                data = []
            if len(data) >= 2:
                word = data[0]
                conf = float(data[1]) if data[1] is not None else 0.0
                if conf >= CONF_THRESHOLD and last_confidence != conf:
                    recognized = word
                    print("Recognized word: {0} with confidence {1}".format(word, conf))
                    break
            time.sleep(0.1)

        if recognized is None:
            print("No valid recognition, continuing...")
            continue

        if recognized.lower() == "stop":
            tts.say(str("You have decided to stop the game. Goodbye!"))
            print("User requested STOP.")
            break # Go to "finally" section

        # Send the answer back to the akinator server
        print("Sending answer: " + recognized.lower())
        socket.send_string(recognized.lower())
        
        # Receive the next question OR the final guess
        question = socket.recv_string() 


finally:
    # Unsubscribe and shutdown broker to clean up
    try:
        speech_recog.unsubscribe(sr_sub_name)
    except Exception:
        pass
    # Sending "STOP" to close both containers.
    print("Game over. Sending final STOP signal.")
    try:
        socket.send_string("STOP")
    except Exception:
        pass
    broker.shutdown()
    sys.exit(0)


