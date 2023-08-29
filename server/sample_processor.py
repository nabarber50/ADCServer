import json

class SampleProcessor(object):

	def __init__(self, sample_queue, message_queue, instruction_queue, sample_size=100, debug=False):
		#super(SampleProcessor, self).__init__()
		self.running			= True
		self.paused 			= True
		self.sample_queue 		= sample_queue
		self.intruction_queue	= instruction_queue
		self.message_queue		= message_queue
		self.sample_size		= sample_size

	def run(self):
		print "starting the sample processor"
		while self.running:
			if not self.intruction_queue.empty():
				self.process_instruction(self.intruction_queue.get())
			if self.sample_queue.qsize() > self.sample_size + 1:
				# print "Sample Processor Samples: {samples}, messages: {messages}".format(samples=len(self.sample_queue), messages=len(self.message_queue))
				data = []
				for __ in range(self.sample_size):
					sample = self.sample_queue.get()
					# self.sample_buffer.task_done()
					# print sample
					#data.append("({channel},{data})".format(channel=sample[0], data=int(sample[1]) * 0.0032258064516129))
					data.append("({channel},{data},{dt})".format(channel=sample[0], data=int(sample[1]) * 0.0032258064516129, dt=sample[2]))

				data.reverse()
				data_string = json.dumps({"data": data})
				self.message_queue.put(data_string)

			else:
				pass
				#print "Not enough samples:", self.sample_buffer.qsize()
				#time.sleep(.01)

	# def start(self):
	# 	self.running = True
	# 	self.paused = False
	# 	#self.run()
	# 	Thread.start(self)

	def process_instruction(self, message):
		print "sample processor recived command:", message
		if message == "shutdown":
			self.stop()
		else:
			print "unknown instruction received by sample processor:", message

	def stop(self):
		self.running = False
