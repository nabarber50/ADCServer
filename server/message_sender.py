#from threading import Thread
import socket
import time

SEND_BUFFER_SIZE = 112640

class MessageSender(object):
	def __init__(self, message_buffer, client_list, instruction_queue, debug=False):
		#super(MessageSender, self).__init__()
		self.running 		= True
		self.paused 		= False
		self.clients 		= client_list
		self.message_buffer = message_buffer
		self.intruction_queue = instruction_queue
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, SEND_BUFFER_SIZE)

	def run(self):
		while self.running:
			if not self.intruction_queue.empty():
				self.process_instruction(self.intruction_queue.get())
			if self.paused or self.message_buffer.empty():
				#time.sleep(.001)
				continue
			#print "Message Sender Messages: {messages}".format(messages=self.message_buffer.qsize())
			message = self.message_buffer.get()
			#print "message", message
			#for client in self.clients:
				# print "{data} sample in the queue, address={address}, port={port}".format(data=data, address=client[0], port=8182)
			self.socket.sendto(message, ("192.168.2.1", 8182))

	#def start(self):
	#	self.running = True
		#self.run()
		#Thread.start(self)

	def process_instruction(self, message):
		print "message sender recived command:", message
		if message == "shutdown":
			self.stop()
		else:
			print "unknown instruction received by message sender:", message
	def stop(self):
		self.running = False

	def shutdown(self):
		self.running = False
