import math
import random
import nim


class NimAI():
    def __init__(self, alpha=0.5, epsilon=0.1):
        self.q = dict()
        self.alpha = alpha
        self.epsilon = epsilon

    def update(self, old_state, action, new_state, reward):
        old = self.get_q_value(old_state, action)
        best_future = self.best_future_reward(new_state)
        self.update_q_value(old_state, action, old, reward, best_future)

    def get_q_value(self, state, action):
        return self.q.get((tuple(state), action), 0)

    def update_q_value(self, state, action, old_q, reward, future_rewards):
        self.q[(tuple(state), action)] = old_q + self.alpha * (reward + future_rewards - old_q)

    def best_future_reward(self, state):
        if not nim.Nim.available_actions(state):
            return 0
        return max([self.get_q_value(state, action) for action in nim.Nim.available_actions(state)])

    def choose_action(self, state, epsilon=True):
        if epsilon:
            if random.random() < self.epsilon:
                return random.choice(list(nim.Nim.available_actions(state)))
        
        best_action = None
        best_q = float('-inf')
        for action in nim.Nim.available_actions(state):
            q = self.get_q_value(state, action)
            if q > best_q:
                best_q = q
                best_action = action
        return best_action
    
    def predict_action(self, state):
        min_distance = int(math.pow(2, 32))
        nearest_state = None
        for state_known, action in self.q.keys():
            if state_known == state:
                return self.choose_action(state, epsilon=False)

            else:
                xor_state = state[0] ^ state[1] ^ state[2] ^ state[3] ^ state[4]
                xor_state_known = state_known[0] ^ state_known[1] ^ state_known[2] ^ state_known[3]

                distance = xor_state ^ xor_state_known
                if distance < min_distance:
                    min_distance = distance
                    nearest_state = state_known

        predict_action = self.choose_action(nearest_state, epsilon=False)

        for action in nim.Nim.available_actions(state):
            if state[action[0] - action[1]] == state[predict_action[0] - predict_action[1]]:
                return action
        
        return predict_action


def train(piles, train_episodes):
    player = NimAI()

    # Play n games
    for i in range(train_episodes):
        print(f"Playing training game {i + 1}")

        game = nim.Nim(piles)

        # Keep track of last move made by either player
        last = {
            0: {"state": None, "action": None},
            1: {"state": None, "action": None}
        }

        # Game loop
        while True:
            # Keep track of current state and action
            state = game.piles.copy()
            action = player.choose_action(game.piles)

            # Keep track of last state and action
            last[game.player]["state"] = state
            last[game.player]["action"] = action

            # Make move
            game.move(action)
            new_state = game.piles.copy()

            # When game is over, update Q values with rewards
            if game.winner is not None:
                player.update(state, action, new_state, -1)
                player.update(
                    last[game.player]["state"],
                    last[game.player]["action"],
                    new_state,
                    1
                )
                break

            # If game is continuing, no rewards yet
            elif last[game.player]["state"] is not None:
                player.update(
                    last[game.player]["state"],
                    last[game.player]["action"],
                    new_state,
                    0
                )

    print("Done training")

    # Return the trained AI
    return player
