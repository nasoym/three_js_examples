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
  # plane = pybullet.loadURDF("plane.urdf")
  # pybullet.addUserData(plane,key="type",value="plane")
  # pybullet.addUserData(plane,"id","0")


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

def getBodyId(pybullet,body_id):
  for id in range(0, pybullet.getNumBodies()):
    userdata_id = pybullet.getUserDataId(id,"id")
    if userdata_id != -1:
      if pybullet.getUserData(userdata_id).decode('UTF-8') == body_id:
        return id
  return -1

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
      basePosition = json_body.get("pos",[0,0,10])
      baseOrientation = json_body.get("rot",[0,0,0,1])
      mass = json_body.get("mass",1)
      if shape == "sphere":
        radius = json_body.get("radius",1)
        sphere_geom = pybullet.createCollisionShape(pybullet.GEOM_SPHERE,radius=radius)
        sphere = pybullet.createMultiBody(mass,sphere_geom,-1,basePosition,baseOrientation)
        pybullet.addUserData(sphere,key="type",value="sphere")
        pybullet.addUserData(sphere,"id",body_id)
        pybullet.addUserData(sphere,"size",str([radius]))
        print("create sphere: ", body_id)
      elif shape == "box":
        size = json_body.get("radius",[1,1,1])
        box_geom = pybullet.createCollisionShape(pybullet.GEOM_BOX,halfExtents=size)
        box = pybullet.createMultiBody(mass,box_geom,-1,basePosition,baseOrientation)
        pybullet.addUserData(box,key="type",value="box")
        pybullet.addUserData(box,"id",body_id)
        pybullet.addUserData(box,"size",str(size))
        print("create box: ", body_id)
      elif shape == "plane":
        plane_geom = pybullet.createCollisionShape(pybullet.GEOM_PLANE)
        plane = pybullet.createMultiBody(mass,plane_geom,-1,basePosition,baseOrientation)
        pybullet.addUserData(plane,key="type",value="plane")
        pybullet.addUserData(plane,"id",body_id)
        pybullet.addUserData(plane,"size",str([0]))
        print("create plane: ", body_id)
    elif command == "remove":
      found_id = getBodyId(pybullet,body_id)
      if found_id == -1:
        print("body id not found: ",body_id)
      else:
        collision_ids = pybullet.getCollisionShapeData(found_id,-1)
        for collision_id in collision_ids:
          print("remove collision: ",collision_id[0])
          pybullet.removeCollisionShape(collision_id[0])
        print("remove: ",body_id," - ",found_id)
        pybullet.removeBody(found_id)

# In [3]: pybullet.removeBody
#                         removeAllUserDebugItems() removeConstraint()
#                         removeBody()              removeUserData()
#                         removeCollisionShape()    removeUserDebugItem()
 
# ./examples/pybullet/gym/pybullet_envs/examples/testBike.py:27:  p.changeDynamics(plane,-1, mass=20,lateralFriction=1, linearDamping=0, angularDamping=0)


def pybullet_report(pybullet,connection,rabbit_queue):
  # print("update numBodies: " , pybullet.getNumBodies())
  for id in range(0, pybullet.getNumBodies()):
    # print("id: ", id)

    data = {}
    data["command"] = "update"
    channel = connection.channel()
    # channel.queue_declare(queue='hello')

    userdata_id = pybullet.getUserDataId(id,"id")
    if userdata_id != -1:
      data["id"] = pybullet.getUserData(userdata_id).decode('UTF-8')

    userdata_id = pybullet.getUserDataId(id,"type")
    if userdata_id != -1:
      data["type"] = pybullet.getUserData(userdata_id).decode('UTF-8')

    userdata_id = pybullet.getUserDataId(id,"size")
    if userdata_id != -1:
      data["size"] = json.loads(pybullet.getUserData(userdata_id).decode('UTF-8'))

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
  time.sleep(0.1)

connection.close()
pybullet.disconnect()

