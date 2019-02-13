
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

a,b,c = channel.basic_get(queue='foo', no_ack=True)
print(" [x] a %r" % a)
print(" [x] b %r" % b)
print(" [x] c %s" % c)
print(str(c))
print(c.decode('UTF-8'))

connection.close()

