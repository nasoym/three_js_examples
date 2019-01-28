import pybullet
import pybullet_data
import time
import pika
import json
import os

def bullet_setup():
	print("bullet setup")
	pybullet.connect(pybullet.DIRECT)
	pybullet.resetSimulation()
	pybullet.setAdditionalSearchPath(pybullet_data.getDataPath())
	# plane = pybullet.loadURDF("plane.urdf")
	# sphere = pybullet.loadURDF("sphere2.urdf", basePosition=[0,0,10])
	pybullet.setGravity(0,0,-9.8)
	plane = pybullet.loadURDF("plane.urdf")
	pybullet.addUserData(plane,key="type",value="plane")
	pybullet.addUserData(plane,"id","0")


def rabbit_setup():
	print("rabbit setup")
	rabbit_host = os.getenv('rabbit_host', "rabbit")
	rabbit_port = os.getenv('rabbit_port', 5672)
	rabbit_user = os.getenv('rabbit_user', "guest")
	rabbit_password = os.getenv('rabbit_password', "guest")
	credentials = pika.PlainCredentials(rabbit_user, rabbit_password)
	parameters = pika.ConnectionParameters(rabbit_host,
																		 rabbit_port,
																		 '/',
																		 credentials)
	connection = pika.BlockingConnection(parameters)
	return connection


def rabbit_get_queue(connection,pybullet, rabbit_queue):
	# print("rabbit get message")
	while True:
		message,properties,body = connection.channel().basic_get(queue=rabbit_queue, no_ack=True)
		if body is None:
			break
		print("body: " , body.decode('UTF-8'))
		json_body = json.loads(body)
		command = json_body.get("command","")
		body_id = json_body.get("id",0)
		if command == "create":
			shape = json_body.get("shape","box")
			if shape == "sphere":
				# sphere = pybullet.loadURDF("sphere2.urdf", basePosition=[0,0,20])
				sphere = pybullet.createCollisionShape(pybullet.GEOM_SPHERE,radius=1)
				pybullet.addUserData(sphere,key="type",value="sphere")
				pybullet.addUserData(sphere,"id",body_id)
				print("create sphere: ", body_id)


# colBoxId = p.createCollisionShape(p.GEOM_BOX,halfExtents=[boxHalfLength,boxHalfWidth,boxHalfHeight])
# 				colSphereId = p.createCollisionShape(p.GEOM_SPHERE,radius=sphereRadius)
# ./examples/pybullet/gym/pybullet_envs/examples/testBike.py:27:	p.changeDynamics(plane,-1, mass=20,lateralFriction=1, linearDamping=0, angularDamping=0)
#
# p.createCollisionShape(p.GEOM_PLANE)


def pybullet_report(pybullet,connection,rabbit_queue):
	print("update numBodies: " , pybullet.getNumBodies())
	for id in range(0, pybullet.getNumBodies()):
		# print("id: ", id)

		data = {}
		data["command"] = "update"
		channel = connection.channel()
		# channel.queue_declare(queue='hello')

		userdata_id = pybullet.getUserDataId(id,"id")
		# print("user data id: ", userdata_id)
		if userdata_id != -1:
			# print("user data : ", pybullet.getUserData(userdata_id).decode('UTF-8'))
			data["id"] = pybullet.getUserData(userdata_id).decode('UTF-8')
		userdata_id = pybullet.getUserDataId(id,"type")
		# print("user data id: ", userdata_id)
		if userdata_id != -1:
			# print("user data : ", pybullet.getUserData(userdata_id).decode('UTF-8'))
			data["type"] = pybullet.getUserData(userdata_id).decode('UTF-8')

		pos,rot = pybullet.getBasePositionAndOrientation(id)
		data["pos"] = pos
		data["rot"] = rot
		
		channel.basic_publish(exchange='',
											routing_key=rabbit_queue,
											body=json.dumps(data))


rabbit_command_queue = os.getenv('rabbit_queue', "commands")
rabbit_updates_queue = os.getenv('rabbit_queue', "updates")
connection = rabbit_setup()
bullet_setup()


while True:
	rabbit_get_queue(connection, pybullet, rabbit_command_queue)
	pybullet.stepSimulation()
	pybullet_report(pybullet,connection,rabbit_updates_queue)
	time.sleep(1)

connection.close()
pybullet.disconnect()

