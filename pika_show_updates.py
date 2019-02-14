import pika
import os
import time
import json


# json.encoder.FLOAT_REPR = lambda o: format(o, '.2f')
json.encoder.FLOAT_REPR = lambda f: ("%.2f" % f)

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
  for data in json_body:
    if data["type"] == "box":
      # pos = data["pos"]
      print("id:%s pos:[%.2f,%.2f,%.2f] rot:[%.2f,%.2f,%.2f,%.2f]" % (data["id"],data["pos"][0],data["pos"][1],data["pos"][2],data["rot"][0],data["rot"][1],data["rot"][2],data["rot"][3]))
      # print(pos)
      # print(json.dumps(data))

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue
channel.queue_bind(exchange='updates',queue=queue_name)
channel.basic_consume(callback,
											queue=queue_name,
											no_ack=True)

channel.start_consuming()
connection.close()

