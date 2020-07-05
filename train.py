import torch
from player import Player
from agent import Agent
from game import Game
import random
import time
from pokernet import PokerNet
import torch.nn.functional as F
from collections import namedtuple
from torch.multiprocessing import Process,Queue,Manager
from threading import Thread

#agent_1 = Player("Agent_1", 100, 'sl_memory','sl_memory_1', 'rl_memory','rl_memory_1',
                 #agent_path='files/rl_network_Agent_1_16',sl_agent_path='files/sl_network_Agent_1_16',filters = 16,device = 'cuda',epsilon = 0.15)
#agent_2 = Player("Agent_2", 100, 'sl_memory','sl_memory_2', 'rl_memory','rl_memory_2',
                 #agent_path='files/rl_network_Agent_2_16',sl_agent_path='files/sl_network_Agent_2_16',filters = 16,device = 'cuda',epsilon = 0.15)



agent_1 = Agent("Agent_1", 'sl_memory','sl_memory_1', 'rl_memory','rl_memory_1',filters = 32,device = 'cuda')
agent_2 = Agent("Agent_2", 'sl_memory','sl_memory_2', 'rl_memory','rl_memory_2',filters = 32,device = 'cuda')

Transitions = namedtuple('Transition',('state', 'action', 'next_state', 'reward'))
SL_Transitions = namedtuple('SL_Transition',('state', 'action'))

agents = [agent_2,agent_1]
target_counter = 0
UPDATE_TARGET = 60
BATCH_SIZE = 256
FIRST_PASS = True
device = torch.device('cuda')
t0 = time.time()


def prepare_rl_batches(batch):
    rl_memory = []

    for doc in batch:
        state = torch.tensor(doc['state0'], device=device)
        next_state = doc['state1']

        if next_state == 'Terminal':
            next_state = None
        else:
            next_state = torch.tensor(next_state, device=device)

        action = torch.tensor([doc['action0']], device=device).unsqueeze(0)

        reward = torch.tensor([doc['reward']], device=device).float()
        transition = Transitions(state, action, next_state, reward)

        rl_memory.append(transition)

    return rl_memory


def prepare_sl_batches(batch):
    sl_memory = []

    for doc in batch:
        state = torch.tensor(doc['state'], device=device)
        action = torch.tensor([doc['action']], device=device)
        state_action = SL_Transitions(state, action)
        sl_memory.append(state_action)

    return sl_memory



def play_hand(batch_size):
    y = 0
    while (len(agent_1.rl_memory) < batch_size or len(agent_2.rl_memory) < batch_size):
        player_1 = Player('Player_1',100, agent_1)
        player_2 = Player('Player_2', 100, agent_2)
        game = Game()
        game.add(player_1)
        game.add(player_2)
        game.shuffle_players()
        game.game_start()
        stack = random.randint(10, 10)
        player_1.reset(stack*10)
        player_2.reset(stack*10)
        x = game.timer
        y += x
    agent_1.rl_memory.write_db()
    agent_1.sl_memory.write_db()
    agent_2.rl_memory.write_db()
    agent_2.sl_memory.write_db()
    print(y)

while target_counter < 120:
    play_hand(256)

    for agent in agents:
        for i in range(0,2):
            target_counter += 1

            if target_counter % UPDATE_TARGET == 0:
                for agent in agents:
                    agent.set_target_net()

            agent.optimizer_rl.zero_grad()
            agent.optimizer_sl.zero_grad()
            rl_batch = agent.rl_memory.sample(BATCH_SIZE)
            sl_batch = agent.sl_memory.sample(BATCH_SIZE)
            rl_batch = prepare_rl_batches(rl_batch)
            sl_batch = prepare_sl_batches(sl_batch)

            rl_batch = Transitions(*zip(*rl_batch))
            sl_batch = SL_Transitions(*zip(*sl_batch))

            non_final_mask = torch.tensor(tuple(map(lambda s: s is not None,
                                                    rl_batch.next_state)), dtype=torch.bool)

            non_final_next_states= torch.cat([s for s in rl_batch.next_state
                                               if s is not None])


            state_batch = torch.cat(rl_batch.state).to(device)
            action_batch  = torch.cat(rl_batch.action).to(device)
            reward_batch  = torch.cat(rl_batch.reward).unsqueeze(1).to(device)

            state_action_values = agent.model(state_batch).gather(1, action_batch)

            next_state_values = torch.zeros(BATCH_SIZE).to(device)
            next_state_values[non_final_mask] = agent.target_net(non_final_next_states).max(1)[0].detach()
            next_state_values =  next_state_values.unsqueeze(1)

            loss_rl = (reward_batch + next_state_values - state_action_values)**2
            loss_rl = loss_rl.mean()


            x = torch.cat(sl_batch.state).to(device)
            x = x.view(BATCH_SIZE, 113, 13, 4)
            y = torch.cat(sl_batch.action).to(device)
            y = y.view(BATCH_SIZE, 1)
            y_pred = agent.sl_model(x)
            loss_sl = F.nll_loss(y_pred, torch.max(y, 1)[1])

            loss_rl.backward()
            loss_sl.backward()


            print(loss_rl)

            agent.optimizer_rl.step()
            agent.optimizer_sl.step()
            del loss_rl
            del loss_sl

            agent.save_net('files/rl_network_' +agent.name +'_'+str(agent.num_filters),
                           'files/sl_network_'+agent.name+'_' +str(agent.num_filters))

t1 = time.time()
total = t1-t0
print(total)