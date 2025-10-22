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
robot_ip = "host.docker.internal"
robot_port = 9559
valid_answers = ["yes", "no", "i don't know"] # We'll only handle these three answers

terminal_mode = False

try:
    broker = ALBroker("myBroker", "0.0.0.0", 0, robot_ip, robot_port)
    print("ALBroker created.")
except RuntimeError:
    print("Could not connect to Naoqi. Check robot_ip and Choregraphe.")
    sys.exit(1)

print("Attempting to create proxies...") 

try:
    tts = ALProxy("ALTextToSpeech", robot_ip, robot_port)
    print("ALTextToSpeech proxy created.")
except Exception as e:
    print("Could not create ALTextToSpeech proxy: {0}".format(e))
    print("Go in only terminal mode.")
    terminal_mode = True


def get_shell_input():
    """
    Gets validated input from the shell (using raw_input for Python 2.7).
    """
    while True:
        # Use raw_input() for Python 2.7
        answer = raw_input("Enter your answer (yes/no/i don't know): ").strip().lower() # You need to attach to the container's shell to input (please see readme)
        if answer in valid_answers:
            return answer
        else:
            print("Invalid input. Please enter 'yes', 'no', or 'i don't know'.")

try:
    # Send to akinator server to get the first question
    print("Sending initial 'next_q' to get first question...")
    socket.send_string("next_q")
    question = socket.recv_string()

    while True: # Start the main game loop
        if question.startswith("FINAL:"):
            # End of the game, akinator sent the guess
            guess = question.replace("FINAL:", "")
            final_line = "Are you thinking about " + guess
            print("Final guess: " + guess)
            if not terminal_mode:
                tts.say(str(final_line)) # Don't work in simulation don't know why
                pass
            break # Go to "finally" section

        # Ask question and get answer 
        print(question)
        if not terminal_mode:
            tts.say(str(question))
            pass
        
        # Wait for shell input
        answer = get_shell_input()
        
        if answer == "STOP":
            print("User requested STOP.")
            break # Go to "finally" section

        # Send answer and receive next question 
        print("Sending answer: " + answer)
        socket.send_string(answer)
        
        # Receive the next question OR the final guess
        question = socket.recv_string()

finally:
    # Sending "STOP" to close both containers.
    print("Game over. Sending final STOP signal.")
    socket.send_string("STOP") 
    broker.shutdown()
    sys.exit(0)