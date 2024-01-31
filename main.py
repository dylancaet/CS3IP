import random

import gymnasium as gym
import pendulum_climb
import torso_climb
import pybullet as p
import time

env = gym.make('TorsoClimb-v0', render_mode='human')
ob, info = env.reset(seed=42)

state = env.reset()
done = False
truncated = False
score = 0
step = 0
pause = False

action = [0.0 for i in range(8)]
action[6] = 1.0
action[7] = 1.0

while True:
    action = env.action_space.sample()

    if not pause:
        obs, reward, done, truncated, info = env.step(action)
        score += reward
        step += 1

    # Reset on backspace
    keys = p.getKeyboardEvents()
    if 65305 in keys and keys[65305]&p.KEY_WAS_TRIGGERED:
        print(f"Score: {score}, Steps {step}")
        done = False
        truncated = False
        score = 0
        step = 0
        env.reset()
    # Pause on space
    if 32 in keys and keys[32]&p.KEY_WAS_TRIGGERED:
        pause = not pause
        print("Paused" if pause else "Unpaused")

    if done or truncated:
        pause = True
        done = False
        truncated = False
        print(f"Episode over, Score: {score}, Steps {step}")


env.close()
