import argparse
import os

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

from MADDPG import MADDPG
from main import get_env

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('env_name', type=str, default='simple_adversary_v3', help='name of the env',
                        choices=['simple_adversary_v3', 'simple_spread_v3', 'simple_tag_v3','simple_v3'])
    parser.add_argument('folder', type=str, help='name of the folder where model is saved')
    parser.add_argument('--episode-num', type=int, default=10, help='total episode num during evaluation')
    parser.add_argument('--episode-length', type=int, default=50, help='steps per episode')

    args = parser.parse_args()

    model_dir = os.path.join('./results', args.env_name, args.folder)
    assert os.path.exists(model_dir)
    gif_dir = os.path.join(model_dir, 'gif')
    if not os.path.exists(gif_dir):
        os.makedirs(gif_dir)
    gif_num = len([file for file in os.listdir(gif_dir)])  # current number of gif

    env, dim_info = get_env(args.env_name, args.episode_length, 'rgb_array')
    maddpg = MADDPG.load(dim_info, os.path.join(model_dir, 'model.pt'))

    agent_num = env.num_agents
    # reward of each episode of each agent
    episode_rewards = {agent: np.zeros(args.episode_num) for agent in env.agents}
    for episode in range(args.episode_num):
        (states ,info)= env.reset()
        agent_reward = {agent: 0 for agent in env.agents}  # agent reward of the current episode
        frame_list = []  # used to save gif
        while env.agents :  # interact with the env for an episode
            actions = maddpg.select_action(states)
            next_states, rewards, dones, truncated,infos = env.step(actions)
            frame= env.render()
            frame_list.append(Image.fromarray(frame))
            states = next_states

            for agent_id, reward in rewards.items():  # update reward
                agent_reward[agent_id] += reward

        
        message = f'episode {episode + 1}, '
        # episode finishes, record reward
        for agent_id, reward in agent_reward.items():
            episode_rewards[agent_id][episode] = reward
            message += f'{agent_id}: {reward:>4f}; '
        print(message)
        # save gif
        frame_list[0].save(os.path.join(gif_dir, f'out{gif_num + episode + 1}.gif'),
                           save_all=True, append_images=frame_list[1:], duration=1, loop=0)
    env.close()
