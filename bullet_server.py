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
		if "command" in json_body.keys():
			command = json_body["command"]
			# body_id = json_body["id"]
			print("command: " , command)
			if command == "create":
				sphere = pybullet.loadURDF("sphere2.urdf", basePosition=[0,0,20])
				pybullet.addUserData(sphere,key="type",value="sphere")
				# pybullet.addUserData(sphere,"id",body_id)

def pybullet_report(pybullet):
	print("numBodies: " , pybullet.getNumBodies())
	for id in range(0, pybullet.getNumBodies()):
		print("id: ", id)
		userdata_type_id = pybullet.getUserDataId(id,"type")
		print("user data id: ", userdata_type_id)
		if userdata_type_id != -1:
			print("user data info: ", pybullet.getUserData(id,userdata_type_id))
		# for user_data_id in range(pybullet.getNumUserData(id)):
		# 	print("user data id: ", user_data_id)
		# 	print("user data info: ", pybullet.getUserDataInfo(id,user_data_id))

# print ("Iterating over all user data entries and printing results")
# for i in range(client.getNumUserData(plane_id)):
#   userDataId, key, bodyId, linkIndex, visualShapeIndex = client.getUserDataInfo(plane_id, i)
#   print ("Info: (%s, %s, %s, %s, %s)" % (userDataId, key, bodyId, linkIndex, visualShapeIndex))
#   print ("Value: %s" % client.getUserData(userDataId))

			# print("user data: ", pybullet.getUserData(id,user_data_id))
		# userdata_type_id = pybullet.getUserDataId(id,"type")
		# if userdata_type_id != -1:
		# 	print("type: ", pybullet.getUserData(id,userdata_type_id))
		# userdata_id_id = pybullet.getUserDataId(id,"id")
		# if userdata_id_id != -1:
		# print("id: ", pybullet.getUserData(id,userdata_id_id))
		print(pybullet.getBasePositionAndOrientation(id))

rabbit_queue = os.getenv('rabbit_queue', "foo")
connection = rabbit_setup()
bullet_setup()


while True:
	rabbit_get_queue(connection, pybullet, rabbit_queue)
	# print("simulate")
	pybullet.stepSimulation()
	pybullet_report(pybullet)
	# point=pybullet.getBasePositionAndOrientation(sphere)
	time.sleep(1)

connection.close()
pybullet.disconnect()

