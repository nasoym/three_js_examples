
import pika
import os
import time
import thread

rabbit_host = os.getenv('rabbit_host', "localhost")
rabbit_port = os.getenv('rabbit_port', 5672)
rabbit_user = os.getenv('rabbit_user', "guest")
rabbit_password = os.getenv('rabbit_password', "guest")

credentials = pika.PlainCredentials(rabbit_user, rabbit_password)
parameters = pika.ConnectionParameters(rabbit_host,
                                   rabbit_port,
                                   '/',
                                   credentials)
connection = pika.BlockingConnection(parameters)


channel = connection.channel()

def callback(ch, method, properties, body):
  print(" [x] Received %r" % body)


# print(' [*] Waiting for messages. To exit press CTRL+C')

def threaded_rmq():
	channel.basic_consume(callback,
												queue='foo',
												no_ack=True)
	channel.start_consuming()


# threadRMQ = Thread(target=threaded_rmq)
# threadRMQ.start()
thread.start_new_thread(threaded_rmq)
	
time.sleep(60 * 3)
connection.close()

