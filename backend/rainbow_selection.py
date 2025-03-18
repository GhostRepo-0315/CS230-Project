from env_uclb import UCLB
from rainbow_replay_buffer import *
from rainbow_agent import DQN
import argparse
import random
import torch
import numpy as np

NODE_SERVERS = [
    "http://52.53.207.217:7001",
    "http://18.144.171.222:7001",
    "http://54.67.117.71:7001"
]

def seed_torch(seed):
    torch.manual_seed(seed)
    if torch.backends.cudnn.enabled:
        torch.cuda.manual_seed(seed)
        torch.backends.cudnn.benchmark = False
        torch.backends.cudnn.deterministic = True


class Runner:
    def __init__(self, args, number, seed):
        self.args = args
        self.action_list = []
        self.number = number
        self.seed = seed
        self.env = UCLB()
        print("env name:", self.env.name)
        np.random.seed(seed)
        torch.manual_seed(seed)

        self.args.state_dim = self.env.observation_space.shape[0]
        self.args.action_dim = self.env.action_space.n
        self.args.episode_limit = self.env.slot_num  # Maximum number of steps per episode
        print("state_dim={}".format(self.args.state_dim))
        print("action_dim={}".format(self.args.action_dim))
        print("episode_limit={}".format(self.args.episode_limit))

        if args.use_per and args.use_n_steps:
            self.replay_buffer = N_Steps_Prioritized_ReplayBuffer(args)
        elif args.use_per:
            self.replay_buffer = Prioritized_ReplayBuffer(args)
        elif args.use_n_steps:
            self.replay_buffer = N_Steps_ReplayBuffer(args)
        else:
            self.replay_buffer = ReplayBuffer(args)
        self.agent = DQN(args)

        self.algorithm = 'dqn'
        if args.use_double and args.use_dueling and args.use_noisy and args.use_per and args.use_n_steps:
            self.algorithm = 'rainbow_' + self.algorithm
        else:
            if args.use_double:
                self.algorithm += '_double'
            if args.use_dueling:
                self.algorithm += '_dueling'
            if args.use_noisy:
                self.algorithm += '_noisy'
            if args.use_per:
                self.algorithm += '_per'
            if args.use_n_steps:
                self.algorithm += "_n_steps"

        self.evaluate_num = 0  # Record the number of evaluations
        self.evaluate_rewards = []  # Record the rewards during the evaluating
        self.total_steps = 0  # Record the total steps during the training
        if args.use_noisy:  # If choose to use Noisy net, then the epsilon is no longer needed
            self.epsilon = 0
        else:
            self.epsilon = self.args.epsilon_init
            self.epsilon_min = self.args.epsilon_min
            self.epsilon_decay = (self.args.epsilon_init - self.args.epsilon_min) / self.args.epsilon_decay_steps

    def run(self):
        while self.total_steps < self.args.max_train_steps:
            state = self.env.reset()
            done = False
            episode_steps = 0
            while not done:
                action = self.agent.choose_action(state, epsilon=self.epsilon)
                server = NODE_SERVERS[action]
                self.action_list.append(server)
                next_state, reward, done = self.env.step(action)
                self.total_steps += 1

                if not self.args.use_noisy:
                    self.epsilon = max(self.epsilon - self.epsilon_decay, self.epsilon_min)

                terminal = done and episode_steps != self.args.episode_limit

                self.replay_buffer.store_transition(state, action, reward, next_state, terminal, done)
                state = next_state

                if self.replay_buffer.current_size >= self.args.batch_size:
                    self.agent.learn(self.replay_buffer, self.total_steps)
    
    @staticmethod
    def get_strategy():
        episode_length = 8  # Number of steps per episode
        episode_number = 1  # Number of episodes to evaluate
        steps = episode_number * episode_length  # Total step number

        parser = argparse.ArgumentParser("Hyperparameter Setting for DQN")
        parser.add_argument("--max_train_steps", type=int, default=int(steps), help="Maximum number of evaluating steps")
        parser.add_argument("--batch_size", type=int, default=256, help="Batch size")
        parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
        parser.add_argument("--gamma", type=float, default=0.99, help="Discount factor")
        parser.add_argument("--epsilon_init", type=float, default=0.5, help="Initial epsilon")
        parser.add_argument("--epsilon_min", type=float, default=0.1, help="Minimum epsilon")
        parser.add_argument("--epsilon_decay_steps", type=int, default=int(1e5), help="Epsilon decay steps")
        parser.add_argument("--use_double", type=bool, default=True, help="Use double Q-learning")
        parser.add_argument("--use_dueling", type=bool, default=True, help="Use dueling network")
        parser.add_argument("--use_noisy", type=bool, default=True, help="Use noisy network")
        parser.add_argument("--use_per", type=bool, default=True, help="Use PER")
        parser.add_argument("--use_n_steps", type=bool, default=True, help="Use n-step Q-learning")

        args = parser.parse_args()

        for k, seed in enumerate([40]):
            print("Eval index:", k, "seed", seed)
            np.random.seed(seed)
            random.seed(seed)
            seed_torch(seed)

            runner = Runner(args=args, number=1, seed=seed)
            runner.agent.net.load_state_dict(torch.load(f'rainbow_dqn_net_{runner.env.user_num}_users.pth'))
            runner.agent.target_net.load_state_dict(torch.load(f'rainbow_dqn_target_net_{runner.env.user_num}_users.pth'))
            runner.run()

            with open('action_list.txt', 'w') as file:
                file.writelines(f"{item}\n" for item in runner.action_list)


if __name__ == "__main__":
    runner = Runner()
    runner.get_strategy()
