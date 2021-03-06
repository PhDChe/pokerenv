from pokerenv.common import PlayerState, PlayerAction


class Player:
    def __init__(self, identifier, agent, name, penalty):
        self.agent = agent
        self.state = PlayerState.ACTIVE
        self.has_acted = False
        self.identifier = identifier
        self.name = name
        self.stack = 0
        self.cards = []
        self.position = 0
        self.all_in = False
        self.bet_this_street = 0
        self.money_in_pot = 0
        self.history = []
        self.hand_rank = 0
        self.pending_penalty = 0
        self.winnings = 0
        self.penalty = penalty

    def __lt__(self, other):
        return self.identifier < other.identifier

    def __gt__(self, other):
        return self.identifier > other.identifier

    def step(self, observation, valid_actions, episode_over=False):
        if self.has_acted:
            previous_reward = self.pending_penalty + self.winnings
            self.pending_penalty = 0
        else:
            previous_reward = None
            self.has_acted = True
        return self.agent.step(observation, valid_actions, previous_reward, episode_over)

    def fold(self):
        self.state = PlayerState.FOLDED
        self.history.append({'action': PlayerAction.FOLD, 'value': 0})

    def check(self):
        self.history.append({'action': PlayerAction.CHECK, 'value': 0})

    def call(self, amount):
        amount = amount - self.bet_this_street
        if amount >= self.stack:
            call_size = self.stack
            self.stack = 0
            self.all_in = True
            self.bet_this_street += call_size
            self.money_in_pot += call_size
            self.history.append({'action': PlayerAction.CALL, 'value': call_size})
            return call_size
        else:
            self.stack -= amount
            self.bet_this_street += amount
            self.money_in_pot += amount
            self.history.append({'action': PlayerAction.CALL, 'value': amount})
            return amount

    def bet(self, amount):
        if amount == self.stack:
            self.all_in = True
        amount = amount - self.bet_this_street
        self.stack -= amount
        self.bet_this_street += amount
        self.money_in_pot += amount
        self.history.append({'action': PlayerAction.BET, 'value': amount})
        return amount

    def punish_invalid_action(self):
        self.pending_penalty += self.penalty

    def finish_street(self):
        self.bet_this_street = 0

    def calculate_hand_rank(self, evaluator, community_cards):
        self.hand_rank = evaluator.evaluate(self.cards, community_cards)

    def reset(self):
        self.state = PlayerState.ACTIVE
        self.has_acted = False
        self.all_in = False
        self.bet_this_street = 0
        self.money_in_pot = 0
        self.cards = []
        self.history = []
        self.hand_rank = 0
        self.pending_penalty = 0
        self.winnings = 0
