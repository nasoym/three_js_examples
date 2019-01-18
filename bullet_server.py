import pybullet
import pybullet_data
import time
import pika
import json

pybullet.connect(pybullet.DIRECT)
pybullet.resetSimulation()
pybullet.setAdditionalSearchPath(pybullet_data.getDataPath())
# plane = pybullet.loadURDF("plane.urdf")
# sphere = pybullet.loadURDF("sphere2.urdf", basePosition=[0,0,10])
pybullet.setGravity(0,0,-9.8)

def rabbit_setup():
	rabbit_host = os.getenv('rabbit_host', "localhost")
	rabbit_port = os.getenv('rabbit_port', 5672)
	rabbit_user = os.getenv('rabbit_user', "guest")
	rabbit_queue = os.getenv('rabbit_queue', "foo")
	rabbit_password = os.getenv('rabbit_password', "guest")
	credentials = pika.PlainCredentials(rabbit_user, rabbit_password)
	parameters = pika.ConnectionParameters(rabbit_host,
																		 rabbit_port,
																		 '/',
																		 credentials)
	connection = pika.BlockingConnection(parameters)
	return connection

connection = rabbit_setup()


def rabbit_get_queue(connection,pybullet):
	message,properties,body = connection.channel.basic_get(queue=rabbit_queue, no_ack=True)
	json_body = json.loads(body)
	if "command" in json_body.keys():
		command = json_body["command"]

while True:
	rabbit_get_queue(connection, pybullet)
	pybullet.stepSimulation()
	# point=pybullet.getBasePositionAndOrientation(sphere)

	time.sleep(1)

connection.close()
pybullet.disconnect()

