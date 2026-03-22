# src/reviewer.py

import random
import time
import json

class DecentralizedGovernanceProtocol:
    def __init__(self, agents):
        self.agents = agents
        self.proposals = []
        self.votes = {}
        self.epoch = 0
        self.voting_duration = 60  # 60 seconds

    def submit_proposal(self, agent, proposal):
        self.proposals.append({
            'agent': agent,
            'proposal': proposal,
            'votes': 0
        })
        self.votes[proposal] = []

    def vote(self, agent, proposal):
        if proposal in self.votes:
            if agent not in self.votes[proposal]:
                self.votes[proposal].append(agent)
                self.proposals[self.proposals.index(next(p for p in self.proposals if p['proposal'] == proposal))]['votes'] += 1

    def tally_votes(self):
        self.epoch += 1
        print(f'Epoch {self.epoch} vote tally:')
        for proposal in self.proposals:
            print(f'Proposal: {proposal['proposal']}, Votes: {proposal['votes']}')
        winning_proposal = max(self.proposals, key=lambda p: p['votes'])
        print(f'Winning proposal: {winning_proposal['proposal']} with {winning_proposal['votes']} votes')
        self.proposals = []
        self.votes = {}

    def run(self):
        while True:
            for agent in self.agents:
                if random.random() < 0.1:
                    proposal = f'Agent {agent} proposal {len(self.proposals) + 1}'
                    self.submit_proposal(agent, proposal)
            time.sleep(self.voting_duration)
            self.tally_votes()

agents = [f'Agent {i}' for i in range(1, 11)]
decentralized_governance = DecentralizedGovernanceProtocol(agents)
decentralized_governance.run()