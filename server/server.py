#!/usr/bin/python

import socket
import time
import sys
import signal
from multiprocessing import Process, Queue
from collections import deque

from adc.adc import ADC, SPI_DEVICE, SPI_PORT
from sample_processor import SampleProcessor
from message_sender import MessageSender
import threading

class Server(object):

	def __init__(self, port, address, debug=False):
		signal.signal(signal.SIGINT, self.shutdown)
		self.debug 				= debug
		self.port 				= port
		self.address 			= address
		self.clients 			= []
		self.running 			= False
		self._sample_processor 	= None
		self._message_sender	= None
		self._sample_queue 				= Queue()
		self._message_queue 			= Queue()
		self._sample_processor_commands = Queue()
		self._message_sender_commands	= Queue()

		self._adc 				= ADC(sample_buffer=self._sample_queue, spi_port=SPI_PORT, spi_device=SPI_DEVICE)
		self.socket 			= socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		# self.socket.setblocking(1)
		self.num_samples = 100
		if self.bind():
			self.running = True

	def run(self):
		while self.running:
			message = ""
			try:
				message, address = self.socket.recvfrom(1024)
			except Exception as e:
				pass
			if message:
				self.process_message(message=message.strip(), address=address[0], port=address[1])
			time.sleep(.001)

	def shutdown(self, signum=None, frame=None):
		print "SHUTTING IT DOWN"
		try:
			self._sample_processor_commands.put("shutdown")
			self._message_sender_commands.put("shutdown")
			time.sleep(1)
			# self._message_sender.shutdown()
			self._adc.shutdown()
			self.purge_queue(self._sample_queue)
			self.purge_queue(self._message_queue)
			self.purge_queue(self._sample_processor_commands)
			self.purge_queue(self._message_sender_commands)
			print self._sample_queue.qsize(), self._message_queue.qsize(), self._sample_processor_commands.qsize(), self._message_sender_commands.qsize()
			self._sample_processor.terminate()
			self._message_sender.terminate()
			print "terminated, active count is: ", threading.activeCount()
			for t in threading.enumerate():
				print "Thread still alive:", t
			self.running = False

		except Exception as e:
			print "ERROR SHITTING", e
			sys.exit(1)
		sys.exit(0)

	def purge_queue(self, queue):
		while not queue.empty():
			__ = queue.get()

	def process_message(self, message, address, port):
		if message == "shutdown":
			if self.debug:
				print "received termination instructions from address: {address} port: {port}".format(address=address, port=port)
			self.shutdown()

		if message == "register":
			if self.debug:
				print "registering client address: {address} port: {port}".format(address=address, port=port)
			self.clients.append((address, port))

		if message == "killall":
			self.broadcast_message(message="")

		if message == "stop":
			if self.debug:
				print "stopping the adc server"
			self._adc.stop()

		if message == "start":
			if self.debug:
				print "starting the adc server"
			self._adc.start()
			self._adc.sample()
			p1 = SampleProcessor(sample_queue=self._sample_queue, message_queue=self._message_queue, instruction_queue=self._sample_processor_commands)
			p2 = MessageSender(message_buffer=self._message_queue, instruction_queue=self._message_sender_commands, client_list=self.clients)
			self._sample_processor = Process(target=p1.run, args=())
			self._message_sender = Process(target=p2.run, args=())
			self._sample_processor.start()
			self._message_sender.start()
			# print "my life status is:", self._sample_processor.is_alive()
			# print "my life status is:", self._message_sender.is_alive()

		if message == "shutdown":
			if self.debug:
				print "shutting down the adc server"
			self._adc.shutdown()
			self.running = False

		if "size" in message:
			size = message.replace("size", "").strip()
			if self.debug:
				print "setting num_samples to: {size}".format(size=size)
			self.num_samples = size

		if "channels" in message:
			channels = message.replace("channels", "").strip().split(",")
			channels = [int(i) for i in channels if i]
			if self.debug:
				print "setting channels to: {channels}".format(channels=channels)
			self._adc.set_channels(channels)

		if "method" in message:
			method = message.replace("method", "").strip()
			if self.debug:
				print "setting method to: {method}".format(method=method)
			self._adc.set_method(method)
		else:
			if self.debug:
				print "received message: {message} from address: {address} port: {port}".format(message=message, address=address, port=port)

	def send(self, message, address, port):
		if self.running:
			self.socket.sendto(message, (address, port))

	def broadcast_message(self, message):
		for client in self.clients:
			self.send(message, client[0], client[1])

	def bind(self):
		bind_addr = (self.address, self.port)
		try:
			self.socket.bind(bind_addr)
		except Exception as e:
			print "failed to bind to address: {address} port:{port}\n {exception}".format(address=self.address, port=self.port, exception=e)
			return False
		return True

if __name__ == "__main__":
	debug = False
	address = "0.0.0.0"
	port = 8181
	if "--address" in sys.argv:
		address = sys.argv[sys.argv.index("--address") + 1]
	if "--port" in sys.argv:
		port = int(sys.argv[sys.argv.index("--port") + 1])
	if "--debug" in sys.argv:
		debug = True

	server = Server(address=address, port=port, debug=debug)
	server.run()


