import signal
import socket
import sys
import threading


class Client(threading.Thread):
	def __init__(self, port, address, debug=False):
		super(Client, self).__init__()
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.server_port = port
		self.server_address = address
		self.running = True

	def run(self):
		while self.running:
			message, address = self.socket.recvfrom(1024)
			self.process_message(message=message.strip(), address=address[0], port=address[1])

	def send(self, message):
		if self.running:
			self.socket.sendto(message, (self.server_address, self.server_port))

	def signal_handler(self, signal, frame):
		print('You pressed Ctrl C!')
		self.send("shutdown")
		self.running = False

	def process_message(self, message, address, port):
		if message == "":
			print "received termination server: {address} port: {port}".format(address=address, port=port)
			self.running = False
		else:
			print "received message: {message} from address: {address} port: {port}".format(message=message, address=address, port=port)

if __name__ == "__main__":
	debug = False
	port = 8181
	address = "0.0.0.0"
	message = "sup"

	if "--message" in sys.argv:
		message = sys.argv[sys.argv.index("--message") + 1]
	if "--address" in sys.argv:
		address = sys.argv[sys.argv.index("--address") + 1]
	if "--port" in sys.argv:
		port = int(sys.argv[sys.argv.index("--port") + 1])
	if "--debug" in sys.argv:
		debug = True

	client = Client(address=address, port=port)
	client.start()
	signal.signal(signal.SIGINT, client.signal_handler)

	while client.running:
		message = raw_input("enter message to send: ")
		client.send(message)
