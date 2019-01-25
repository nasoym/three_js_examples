
import pika
import os
import time

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
  # print(" [x] Received %r" % body)
  print(body.decode('UTF-8'))


# print(' [*] Waiting for messages. To exit press CTRL+C')

channel.basic_consume(callback,
											queue='updates',
											no_ack=True)
channel.start_consuming()

	
connection.close()

