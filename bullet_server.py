import pybullet
import pybullet_data
import time
import pika
import json
import os
import copy

sleep_time=0.1

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
  channel = connection.channel()
  channel.queue_declare(queue="commands")
  channel.exchange_declare(
      exchange="updates",
      exchange_type="fanout"
      )
  return (connection,channel)

def getBodyId(pybullet,body_id):
  for id in range(0, pybullet.getNumBodies()):
    body_unique_id = pybullet.getBodyUniqueId(id)
    userdata_id = pybullet.getUserDataId(body_unique_id,"id")
    if userdata_id != -1:
      if pybullet.getUserData(userdata_id).decode('UTF-8') == body_id:
        return body_unique_id
  return -1

def rabbit_get_queue(channel,pybullet, rabbit_queue):
  global sleep_time
  # print("rabbit get message")
  while True:
    message,properties,body = channel.basic_get(queue="commands", no_ack=True)
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
      if shape == "box":
        size = json_body.get("size",[1,1,1])
        box_geom = pybullet.createCollisionShape(pybullet.GEOM_BOX,halfExtents=[size[0]*0.5,size[1]*0.5,size[2]*0.5])
        # box = pybullet.createMultiBody(baseMass=mass,baseCollisionShapeIndex=box_geom,-1,basePosition=basePosition,baseOrientation=baseOrientation)
        box = pybullet.createMultiBody(baseMass=mass,baseCollisionShapeIndex=box_geom,basePosition=basePosition,baseOrientation=baseOrientation)
        pybullet.addUserData(box,key="type",value="box")
        pybullet.addUserData(box,"id",body_id)
        pybullet.addUserData(box,"size",str(size))
        print("create box: ", body_id)
      elif shape == "plane":
        size = json_body.get("size",[1,1,1])
        plane_geom = pybullet.createCollisionShape(pybullet.GEOM_PLANE)
        plane = pybullet.createMultiBody(mass,plane_geom,-1,basePosition,baseOrientation)
        pybullet.addUserData(plane,key="type",value="plane")
        pybullet.addUserData(plane,"id",body_id)
        pybullet.addUserData(plane,"size",str(size))
        print("create plane: ", body_id)
      # elif shape == "sphere":
      #   radius = json_body.get("size",[1,1,1])
      #   sphere_geom = pybullet.createCollisionShape(pybullet.GEOM_SPHERE,radius=radius)
      #   sphere = pybullet.createMultiBody(mass,sphere_geom,-1,basePosition,baseOrientation)
      #   pybullet.addUserData(sphere,key="type",value="sphere")
      #   pybullet.addUserData(sphere,"id",body_id)
      #   pybullet.addUserData(sphere,"size",str([radius]))
      #   print("create sphere: ", body_id)
    elif command == "remove":
      found_id = getBodyId(pybullet,body_id)
      if found_id == -1:
        print("body id not found: ",body_id)
      else:
        print("remove: ",body_id," - ",found_id," - ",type(found_id))
        # body_unique_id = pybullet.getBodyUniqueId(found_id)
        # # collision_ids = pybullet.getCollisionShapeData(body_unique_id,-1)
        # # for collision_id in collision_ids:
        # #   print("remove collision: ",collision_id[0])
        # #   pybullet.removeCollisionShape(collision_id[0])
        # print("remove: ",body_id," - ",body_unique_id," - ",type(body_unique_id))
        # pybullet.removeBody(body_unique_id)
        pybullet.removeBody(found_id)
    elif command == "set":
      key = json_body.get("key","")
      value = json_body.get("value","")
      if key == "gravity":
        pybullet.setGravity(value[0],value[1],value[2])
      elif key == "sleep_time":
        sleep_time = value;
    # elif command == "quit":

# In [3]: pybullet.removeBody
#                         removeAllUserDebugItems() removeConstraint()
#                         removeBody()              removeUserData()
#                         removeCollisionShape()    removeUserDebugItem()
 
# ./examples/pybullet/gym/pybullet_envs/examples/testBike.py:27:  p.changeDynamics(plane,-1, mass=20,lateralFriction=1, linearDamping=0, angularDamping=0)

def pybullet_get_body_data(pybullet,body_unique_id):
  data = {}
  data["command"] = "update"

  # for user_data_index in range(1, pybullet.getNumUserData(body_unique_id)+1):
  #   # print("userdata info: ", user_data_index, " - ", pybullet.getUserDataInfo(body_unique_id,user_data_index))
  #   userDataInfo = pybullet.getUserDataInfo(body_unique_id,user_data_index)
  #   # print("userdata data: ", pybullet.getUserData(userDataInfo[0]).decode('UTF-8'))
  #   # data[userDataInfo[1].decode('UTF-8')] = pybullet.getUserData(userDataInfo[0]).decode('UTF-8')
  #   # data[copy.copy(userDataInfo[1].decode('UTF-8'))] = "a"
  #   data["u"] = "a"

  userdata_id = pybullet.getUserDataId(body_unique_id,"id")
  if userdata_id != -1:
    data["id"] = pybullet.getUserData(userdata_id).decode('UTF-8')

  userdata_id = pybullet.getUserDataId(body_unique_id,"type")
  if userdata_id != -1:
    data["type"] = pybullet.getUserData(userdata_id).decode('UTF-8')

  userdata_id = pybullet.getUserDataId(body_unique_id,"size")
  if userdata_id != -1:
    data["size"] = json.loads(pybullet.getUserData(userdata_id).decode('UTF-8'))

  pos,rot = pybullet.getBasePositionAndOrientation(body_unique_id)
  data["pos"] = pos
  data["rot"] = rot
  return data

def pybullet_report(pybullet,channel,rabbit_queue):
  body_data = []
  for id in range(0, pybullet.getNumBodies()):
    body_unique_id = pybullet.getBodyUniqueId(id)
    body_data.append(pybullet_get_body_data(pybullet,body_unique_id))

  channel.basic_publish(exchange='updates',
                    routing_key='',
                    body=json.dumps(body_data))


rabbit_command_queue = os.getenv('rabbit_queue', "commands")
rabbit_updates_queue = os.getenv('rabbit_queue', "updates")
connection,channel = rabbit_setup()
bullet_setup()

while True:
  rabbit_get_queue(channel, pybullet, rabbit_command_queue)
  pybullet.stepSimulation()
  pybullet_report(pybullet,channel,rabbit_updates_queue)
  time.sleep(sleep_time)

print("closing")
connection.close()
pybullet.disconnect()

