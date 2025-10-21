import akinator
import zmq

context = zmq.Context()
socket = context.socket(zmq.REP) # REP = Reply
socket.bind("tcp://*:5555")

aki = akinator.Akinator()
aki.start_game()

try:
    while not aki.finished:
        # Send the current question
        socket.send_string(aki.question)

        # Wait for the answer (e.g., "yes", "no")
        answer = socket.recv_string()

        if answer == "STOP":
            break

        q = aki.answer(answer)

    # Send the final guess and wait for final ack
    socket.send_string(f"FINAL:{aki.name_proposition}")
    socket.recv_string()  # Wait for final ack
finally:
    socket.close()
    context.term()