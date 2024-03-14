import random

import humanoid_climb
import gymnasium as gym
import pybullet as p
import time

from stable_baselines3 import PPO, SAC

MOTION = [[10, 9, -1, -1], [10, 9, 2, -1], [10, 9, 2, 1]]
env = gym.make('HumanoidClimb-v0', render_mode='human', max_ep_steps=1600, motion_path=MOTION, state_file=None)
obs, info = env.reset()

state = env.reset()
done = False
truncated = False
score = 0
step = 0
pause = False

MODEL_PATH = ["./models/1_10_9_n_n.zip", "./models/2_10_9_2_n.zip", "./models/3_10_9_2_1.zip"]
O_ACTION = [[-1, -1, -1, -1], [1, 1, -1, -1], [1, 1, 1, -1]]
MODELS = [PPO.load(MODEL_PATH[i], env=env) for i in range(len(MODEL_PATH))]
CUR_MODEL = 0
REWARDS = [0 for i in range(len(MODELS))]
STEPS = [0 for i in range(len(MODELS))]

while True:
    # action = env.action_space.sample()

    if not pause:
        action, _state = MODELS[CUR_MODEL].predict(obs)

        for i in range(4):
            if O_ACTION[CUR_MODEL][i] != -1:
                action[17+i] = O_ACTION[CUR_MODEL][i]

        obs, reward, done, truncated, info = env.step(action)
        score += reward
        step += 1

        REWARDS[CUR_MODEL] += reward
        STEPS[CUR_MODEL] += 1

    # Reset on backspace
    keys = p.getKeyboardEvents()

    if 114 in keys and keys[114] & p.KEY_WAS_TRIGGERED:
        print(f"Score: {score}, Steps {step}")
        CUR_MODEL = 0
        REWARDS = [0 for i in range(len(MODELS))]
        STEPS = [0 for i in range(len(MODELS))]
        done = False
        truncated = False
        pause = False
        score = 0
        step = 0
        env.reset()

    # C
    # if 99 in keys and keys[99] & p.KEY_WAS_TRIGGERED:
    # 	CUR_MODEL += 1
    # 	if CUR_MODEL > len(MODELS)-1:
    # 		CUR_MODEL = 0
    # 	print(f"Current model {CUR_MODEL}")

    # Pause on space
    if 32 in keys and keys[32] & p.KEY_WAS_TRIGGERED:
        pause = not pause
        print("Paused" if pause else "Unpaused")

    if info["is_success"]:
        print(f"Finished stance {CUR_MODEL} with {REWARDS[CUR_MODEL]} reward in {STEPS[CUR_MODEL]} steps")
        CUR_MODEL += 1
        if CUR_MODEL > len(MODELS) - 1:
            CUR_MODEL = 0

    if done or truncated:
        CUR_MODEL = 0
        REWARDS = [0 for i in range(len(MODELS))]
        STEPS = [0 for i in range(len(MODELS))]
        env.reset()
        print("ENV TERMINATED\n")

env.close()
