
import pika
import os

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
# channel.queue_declare(queue='hello')
channel.basic_publish(exchange='',
                  routing_key='foo',
                  body='Hello W0rld!')
print(" [x] Sent 'Hello World!'")
connection.close()

