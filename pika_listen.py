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
  # print(json_body)
  # print(json_body[0]["id"])
  # print(body.decode('UTF-8'))
  all_bodies_below = True
  all_bodies_above = True
  for data in json_body:
    # print("- ", i)
    # data = json_body[i]
    if data["type"] == "box":
      # print("- ", data["pos"][2]  )
      if data["pos"][2] < 3:
        all_bodies_below &= True
      else:
        all_bodies_below &= False
      if data["pos"][2] > 7:
        all_bodies_above &= True
      else:
        all_bodies_above &= False

  if all_bodies_below:
    print("all_bodies_below:", all_bodies_below)
    channel.basic_publish(exchange='',
                      routing_key='commands',
                      body='{"command":"set","key":"gravity","value":[0,0,90]}')
  if all_bodies_above:
    print("all_bodies_above:", all_bodies_above)
    channel.basic_publish(exchange='',
                      routing_key='commands',
                      body='{"command":"set","key":"gravity","value":[0,0,-90]}')


result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue
channel.queue_bind(exchange='updates',queue=queue_name)
channel.basic_consume(callback,
											queue=queue_name,
											no_ack=True)

channel.start_consuming()
	
connection.close()

