import pika
import os
import time
import json

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
  json_body = json.loads(body.decode('UTF-8'))
  print(json_body[0]["id"])
  # print(body.decode('UTF-8'))

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue
channel.queue_bind(exchange='updates',queue=queue_name)
channel.basic_consume(callback,
											queue=queue_name,
											no_ack=True)

channel.start_consuming()
	
connection.close()

