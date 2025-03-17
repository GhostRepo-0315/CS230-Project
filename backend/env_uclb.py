import math
from idlelib.pyparse import trans

import gym
from gym import spaces, logger
import numpy as np


class UCLB(gym.Env):
    def __init__(self):
        self.name = "uclb"
        # Parameter settings
        self.last_energy = 0  # Consumed energy of last slot
        self.user_num = 1  # Number of sensors
        self.server_num = 3 # Number of servers
        self.bandwidth = 20e6  # System bandwidth (Hz)
        self.max_power = 1  # Maximum transmit power (W)
        self.delay_coff = np.random.rand(self.user_num) * 10
        self.data_size = 8

        self.chunk_size = 1  # in Mb
        self.slot_num = int(self.data_size / self.chunk_size) # Number of time slots
        self.chunk_num = np.zeros([self.user_num])
        for i in range(self.user_num):
            self.chunk_num[i] = int(math.ceil(self.data_size / self.chunk_size))
        self.remain_chunk_num = self.chunk_num
        self.noise_power_dBm = -174 + 10 * np.log10(self.bandwidth)  # Convert dBm to linear scale
        self.noise_power = 10 ** (self.noise_power_dBm / 10 - 3)  # Compute noise power
        self.noise_power = self.noise_power / 100  # High SNR
        # self.noise_power = self.noise_power * 10  # Low SNR
        self.server_load = np.zeros(self.server_num)


        self.aver_delay_list = np.zeros([self.slot_num])
        self.mad_list = np.zeros([self.slot_num])
        self.reward_list = np.zeros([self.slot_num])


        self.episode_aver_delay_list = []
        self.episode_reward_list = []
        self.episode_mad_list = []


        self.step_reward_list = []
        self.step_delay_list = []
        self.step_mad_list = []

        np.seterr(over='ignore')


        # DRL parameter settings
        self.num_actions = self.server_num ** self.user_num  # Total number of possible actions
        self.done = False
        self.action_space = spaces.Discrete(self.num_actions)

        self.obs_chunks_num_low = np.zeros(self.user_num)
        self.obs_chunks_num_high = self.remain_chunk_num

        self.obs_load_low = np.zeros(self.server_num)
        self.obs_load_high =np.ones(self.server_num) * 1e9

        obs_low = np.concatenate([self.obs_chunks_num_low, self.obs_load_low])
        obs_high = np.concatenate([self.obs_chunks_num_high, self.obs_load_high])
        self.observation_space = spaces.Box(obs_low, obs_high, dtype=np.float32)
        self.step_num = 0
        self.episode_num = 0


        # Load MIMO channel data
        self.channel_gain_data = np.load("mimo_channel_gain_data.npy")

    def decode_action(self, action):
        """
        Maps an integer action (0 ~ self.num_actions - 1) to a server selection index for each user.

        :param action: Integer action from the Discrete action space
        :return: An array of length self.user_num representing the selected server for each user (Range: 1 ~ self.server_num)
        """
        server_selection = np.zeros(self.user_num, dtype=int)

        # Decode the integer action using base conversion (multi-digit representation)
        for i in range(self.user_num):
            server_selection[i] = (action % self.server_num) + 1  # Map to range 1 ~ server_num
            action //= self.server_num  # Integer division to decode the next digit

        return server_selection

    def get_trans_rate(self):
        # Compute SINR for each user-server pair
        sinr = (self.max_power * self.channel_gain_data[self.step_num,:,:]) / self.noise_power  # Shape: (user_num, server_num)
        # Compute transmission rate using Shannon Capacity formula
        trans_rate = (self.bandwidth / self.user_num) * np.log2(1 + sinr)  # Shape: (user_num, server_num)

        return trans_rate  # Output: Transmission rate matrix for the current time slot

    def get_trans_delay(self, trans_rate, action_list):

        trans_delay = np.zeros(self.user_num)
        for i in range(self.user_num):
            server_idx = action_list[i] - 1  # Convert 1-based index to 0-based
            trans_delay[i] = self.chunk_size * 1e6  * 1e3 / trans_rate[i, server_idx]  # Delay = Data Size / Transmission Rate

        return trans_delay  # Shape: (user_num,)

    def get_load_mad(self, action_list):
        for server_idx in action_list:
            self.server_load[server_idx - 1] += self.chunk_size  # in Mb
        # Compute mean absolute deviation of the load distribution
        mad = np.mean(np.abs(self.server_load - np.mean(self.server_load)))
        return mad


    def step(self, action):
        # print("Episode index:", self.episode_num, "Step index:", self.step_num)
        action_list = self.decode_action(action)
        trans_rate = self.get_trans_rate()

        trans_delay = self.get_trans_delay(trans_rate,action_list)
        aver_trans_delay = np.mean(trans_delay)
        self.aver_delay_list[self.step_num] = aver_trans_delay
        self.step_delay_list.append(aver_trans_delay)


        mad = self.get_load_mad(action_list)  # scaled in Mb
        self.mad_list[self.step_num] = mad
        self.step_mad_list.append(mad)

        # Reward calculation
        reward = -(np.mean(self.delay_coff * trans_delay) + mad)
        self.reward_list[self.step_num] = reward
        self.step_reward_list.append(reward.item())

        # State change
        self.remain_chunk_num[self.remain_chunk_num > 0] -= 1
        state = np.concatenate([self.remain_chunk_num, self.server_load])



        # Stop condition
        if np.all(self.remain_chunk_num == 0) or self.step_num >= self.slot_num - 1:
            print("Episode index:", self.episode_num)
            self.episode_num = self.episode_num + 1
            self.done = True

            episode_aver_delay = np.sum(self.aver_delay_list) / self.slot_num
            episode_mad = np.sum(self.mad_list) / self.slot_num
            episode_reward = np.sum(self.reward_list) / self.slot_num


            print("Average total delay [msec] :", episode_aver_delay)
            print("Average total mean absolute deviation [Mb]", episode_mad)
            print("Average reward", episode_reward)


            self.episode_aver_delay_list.append(episode_aver_delay)
            self.episode_mad_list.append(episode_mad)
            self.episode_reward_list.append(episode_reward)


        self.step_num = self.step_num + 1
        return np.array(state), reward, self.done

    def reset(self):
        obs_init = (self.obs_chunks_num_low + self.obs_chunks_num_high) / 2
        load_init = (self.obs_load_low + self.obs_load_high) / 2
        # Combine the user chunks and server load initial states
        state_init = np.concatenate([obs_init, load_init])

        self.done = False
        self.step_num = 0
        self.server_load = np.zeros(self.server_num)
        for i in range(self.user_num):
            self.remain_chunk_num[i] = int(math.ceil(self.data_size / self.chunk_size))
        self.aver_delay_list = np.zeros([self.slot_num])
        self.mad_list = np.zeros([self.slot_num])
        self.reward_list = np.zeros([self.slot_num])

        self.episode_aver_delay_list = []
        self.episode_reward_list = []
        self.episode_mad_list = []


        return np.array(state_init)

