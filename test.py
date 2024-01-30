import math
from time import sleep
import pybullet as p
import pybullet_data
import numpy as np
import os

from pendulum_climb.assets.pendulum import Pendulum

current_directory = os.getcwd()

# Can alternatively pass in p.DIRECT
client = p.connect(p.GUI)
p.setGravity(0, 0, -9.8, physicsClientId=client)
p.setAdditionalSearchPath(pybullet_data.getDataPath())

plane = p.loadURDF("plane.urdf")
# target1 = p.loadURDF(current_directory + "/torso_climb/assets/test.xml", basePosition=[0, 0, 2])
target1 = p.loadMJCF(current_directory + "/torso_climb/assets/mjcf_torso.xml")
# target1 = p.loadURDF("bicycle/bike.urdf", basePosition=[0, 0, 2])

while True:
    p.stepSimulation()
    events = p.getKeyboardEvents()
    print(events)

p.disconnect()
