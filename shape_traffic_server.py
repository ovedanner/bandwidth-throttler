'''
Simple server that can receive requests to limit the bandwidth
between the host machine and other machines.
'''
import zmq
import psutil
import getpass
import argparse
from subprocess import PIPE

# Parse the arguments.
parser = argparse.ArgumentParser()
parser.add_argument("--port", help = "The local port on which the server listens", required = True)
args = parser.parse_args()

context = zmq.Context();
socket = context.socket(zmq.REP)
socket.bind("tcp://*:" + args.port)
user = getpass.getuser()

while True:
	message = socket.recv()
	print("Received request: %s" % message)
	
	message_parts = message.split(" ")
	if (len(message_parts) > 0):
		command = message_parts[0]

		# Set the incoming and outgoing bandwidth value for one
		# or more IP addresses.
		if (command == "set"):
			for i in range(1, len(message_parts)):
				ip, bandwidth = message_parts[i].split(":")
				print("Setting " + ip + " to " + bandwidth)
				p = psutil.Popen(["/usr/bin/shape_traffic", "set", ip, bandwidth], stdout=PIPE)
				print(p.communicate()[0])

		# Limit the traffic on the interface as a whole.
		if (command == "set-all"):
			bandwidth = message_parts[1]
			print("Setting interface to: " + bandwidth)
			p = psutil.Popen(["/usr/bin/shape_traffic", "set-all", bandwidth], stdout=PIPE)
			print(p.communicate()[0])

		# Remove all bandwidth throttles
		if (command == "reset"):
			print("Resetting all bandwidth rules")
			p = psutil.Popen(["/usr/bin/shape_traffic", "reset"], stdout=PIPE)
			print(p.communicate()[0])
				

	# Send reply back to client
	socket.send("Executed request: %s" % message)

