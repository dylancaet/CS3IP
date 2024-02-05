import numpy as np
import pybullet as p
import os
import math


# Reference https://www.gymlibrary.dev/environments/mujoco/humanoid/
class Torso:
    def __init__(self, client, pos):
        f_name = os.path.join(os.path.dirname(__file__), 'mjcf_torso.xml')

        self.client = client
        self.id = p.loadMJCF(mjcfFileName=f_name,
                             flags=p.URDF_USE_SELF_COLLISION_EXCLUDE_ALL_PARENTS)
        self.motors = []
        self.motor_names = []
        self.motor_power = []
        self.ordered_joints = []
        self.ordered_joint_indices = []

        # https://github.com/bulletphysics/bullet3/blob/master/examples/pybullet/tensorflow/humanoid_running.py#L35
        self.human = self.id[0]
        self.ordered_joints = []
        self.ordered_joint_indices = []

        self.RIGHT_HAND = -1
        self.LEFT_HAND = -1
        self.rhand_cid = -1
        self.lhand_cid = -1

        p.resetBasePositionAndOrientation(bodyUniqueId=self.id[0], posObj=pos, ornObj=[0.0, 0.0, 0.0, 1.0],
                                          physicsClientId=client)

        jdict = {}
        for j in range(p.getNumJoints(self.human, physicsClientId=client)):
            info = p.getJointInfo(self.human, j, physicsClientId=client)
            link_name = info[12].decode("ascii")
            if link_name == "left_hand": self.LEFT_HAND = j
            if link_name == "right_hand": self.RIGHT_HAND = j
            self.ordered_joint_indices.append(j)

            if info[2] != p.JOINT_REVOLUTE: continue
            jname = info[1].decode("ascii")
            jdict[jname] = j
            lower, upper = (info[8], info[9])
            self.ordered_joints.append((j, lower, upper))

            p.setJointMotorControl2(self.human, j, controlMode=p.VELOCITY_CONTROL, force=0, physicsClientId=client)

        self.motor_names = ["right_shoulder1", "right_shoulder2", "right_elbow"]
        self.motor_power = [75, 75, 75]
        self.motor_names += ["left_shoulder1", "left_shoulder2", "left_elbow"]
        self.motor_power += [75, 75, 75]
        self.motors = [jdict[n] for n in self.motor_names]

    def get_ids(self):
        return self.id, self.client

    def apply_action(self, actions):
        body_actions = actions[0:6]
        grasp_actions = actions[6:8]

        forces = [0.] * len(self.motors)
        for m in range(len(self.motors)):
            limit = 15
            ac = np.clip(body_actions[m], -limit, limit)
            forces[m] = self.motor_power[m] * ac * 0.082
        p.setJointMotorControlArray(self.human, self.motors, controlMode=p.TORQUE_CONTROL, forces=forces)

        # Left hand value
        if grasp_actions[0] > 0.5:
            self.attach(self.LEFT_HAND, target=2)
        else:
            self.detach(self.LEFT_HAND)

        # Right hand value
        if grasp_actions[1] > 0.5:
            self.attach(self.RIGHT_HAND)
        else:
            self.detach(self.RIGHT_HAND)


    # TODO
    def force_attach(self, limb_link, target_id, force=-1):
        if limb_link == self.LEFT_HAND and self.lhand_cid != -1: self.detach(self.LEFT_HAND)
        if limb_link == self.RIGHT_HAND and self.rhand_cid != -1: self.detach(self.RIGHT_HAND)

        constraint = p.createConstraint(parentBodyUniqueId=self.human,
                                        parentLinkIndex=limb_link,
                                        childBodyUniqueId=target_id,
                                        childLinkIndex=-1,
                                        jointType=p.JOINT_FIXED,
                                        jointAxis=[0, 0, 0],
                                        parentFramePosition=[0, 0, 0],
                                        childFramePosition=[0, 0, 0],
                                        physicsClientId=self.client)
        p.changeConstraint(userConstraintUniqueId=constraint, maxForce=force, physicsClientId=self.client)

        if limb_link == self.LEFT_HAND:
            self.lhand_cid = constraint
        else:
            self.rhand_cid = constraint

    # Attach to the closest target
    # !!! CURRENTLY TESTING CONSTRAINT ON LEFT HAND!!!!
    def attach(self, limb_link, target=None):
        # If already attached return
        if limb_link == self.LEFT_HAND and self.lhand_cid != -1: return
        if limb_link == self.RIGHT_HAND and self.rhand_cid != -1: return

        body_count = p.getNumBodies(physicsClientId=self.client)
        limb_pos = p.getLinkState(bodyUniqueId=self.human, linkIndex=limb_link, physicsClientId=self.client)[0]

        for body_id in range(body_count):
            body_info = p.getBodyInfo(body_id, physicsClientId=self.client)
            body_name = body_info[0].decode("utf-8")

            if body_name == "target":
                target_pos, _ = p.getBasePositionAndOrientation(bodyUniqueId=body_id, physicsClientId=self.client)
                dist = np.linalg.norm(np.array(limb_pos)-np.array(target_pos))
                if dist < 0.06:
                    self.force_attach(limb_link=limb_link, target_id=body_id, force=200)
                    break

    def detach(self, limb_link):
        if limb_link == self.LEFT_HAND and self.lhand_cid != -1:
            p.removeConstraint(userConstraintUniqueId=self.lhand_cid, physicsClientId=self.client)
            self.lhand_cid = -1
        elif limb_link == self.RIGHT_HAND and self.rhand_cid != -1:
            p.removeConstraint(userConstraintUniqueId=self.rhand_cid, physicsClientId=self.client)
            self.rhand_cid = -1

    def get_observation(self):
        pass

