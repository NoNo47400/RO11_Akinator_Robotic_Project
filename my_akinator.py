import akipy
import zmq

# Initialize akipy synchronously
aki = akipy.Akinator()

# Setup ZMQ server socket
context = zmq.Context()
socket = context.socket(zmq.REP) # REP = Reply
socket.bind("tcp://*:5555")

print("Akinator server started using synchronous akipy...")

try:
    # Start the game 
    party = aki.start_game() # english is default language

    q = party.question

    print(f"Initial question: {q}")
    print("type of initial question:", type(q))
    # First, wait for the "next_q" request from naoqi client
    msg = socket.recv_string()
    if msg == "next_q":
        print(f"Received initial request. Sending first question...")
        socket.send_string(q)
    else:
        print(f"Received unexpected first message: {msg}")
        socket.send_string("ERROR: Expected 'next_q'")
        raise SystemExit # Exit if the first message isn't right

    #while float(aki.progression) <= 100: # akipy uses progression attribute
    # Better to stop only if he found something
    while not aki.win:
        # Wait for the answer "yes", "no", "i don't know" or STOP
        answer = socket.recv_string()
        print(f"Received answer: {answer}")

        if answer == "STOP":
            print("Stop signal received. Shutting down.")
            break

        # Process the answer
        try:
            # Map answers to akipy format ('y', 'n', 'idk', 'p', 'pn')
            # Naoqi script sends 'yes', 'no', 'i don't know', we'll don't handle 'probably' or 'probably not' here
            mapped_answer = answer
            if answer == "yes":
                mapped_answer = "y"
            elif answer == "no":
                mapped_answer = "n"
            elif answer == "i don't know":
                mapped_answer = "idk"
        
            # Call answer 
            q = aki.answer(mapped_answer)
            q = q.question

            print(f"Sending next question: {q}")
            socket.send_string(q)

        except akipy.InvalidChoiceError:
            print(f"Invalid answer received: {answer}. Asking client to repeat.")
            # If the answer is invalid, send the *same* question again
            socket.send_string(aki.question)
        except Exception as e:
            print(f"An error occurred during answer processing: {e}")
            socket.send_string(f"ERROR: {e}")
            break 

    # If loop finished normally 
    if answer != "STOP":
        print("Akinator is making a guess...")
        print(f"Akinator's guess: {aki.name_proposition}")
        if aki.name_proposition:
            print(f"Game finished. Sending guess: {aki.name_proposition}")
            # Wait for an answer (any because is not used, just to sync)
            final_req = socket.recv_string()
            socket.send_string(f"FINAL:{aki.name_proposition}")
            # Wait for the final "STOP" ack from the client
            socket.recv_string()
        else:
            print("Akinator couldn't guess.")
            # Wait for an answer (any because is not used, just to sync)
            final_req = socket.recv_string()
            socket.send_string("FINAL:I could not guess.")
            socket.recv_string() # Final STOP

except Exception as e:
    print(f"An error occurred in the game loop: {e}")
finally:
    print("Closing sockets.")
    socket.close()
    context.term()