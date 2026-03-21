import numpy as np
import networkx as nx

class MultiAgentSwarm:
    def __init__(self, num_agents, communication_radius):
        self.num_agents = num_agents
        self.communication_radius = communication_radius
        self.agents = [Agent(i) for i in range(num_agents)]
        self.graph = self.build_communication_graph()

    def build_communication_graph(self):
        G = nx.Graph()
        G.add_nodes_from(range(self.num_agents))

        for i in range(self.num_agents):
            for j in range(i+1, self.num_agents):
                if np.linalg.norm(self.agents[i].position - self.agents[j].position) <= self.communication_radius:
                    G.add_edge(i, j)

        return G

    def update_positions(self):
        for agent in self.agents:
            agent.update_position()

    def coordinate_agents(self):
        for agent in self.agents:
            neighbors = [self.agents[n] for n in self.graph.neighbors(agent.id)]
            agent.coordinate_with_neighbors(neighbors)

class Agent:
    def __init__(self, id):
        self.id = id
        self.position = np.random.rand(2)

    def update_position(self):
        self.position += np.random.rand(2) * 0.1

    def coordinate_with_neighbors(self, neighbors):
        # Implement coordination logic using information from neighboring agents
        pass
