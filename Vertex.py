# python 2.7.12
# Vertex class

from sys import * 

class Vertex: 
	def __init__(self, newID, newPort): 
		self.id = newID; 
		self.port = newPort; 
		self.neighbours = {}; 

		# dijkstra
		self.dist= maxint; 
		self.visited = False; 
		self.predecessor = None; 

		# node failure detection
		self.lives = 5; 
		self.isDead = False; 

	def add_neighbours(self, neighbourID, linkCost):
		self.neighbours[neighbourID] = linkCost; 

	# retrieve list of neighbourID for current node 
	def get_neighbourID(self):
		return self.neighbours.keys(); 

	def get_id(self):
		return self.id; 

	def get_port(self):
		return self.port; 

	def get_linkCost(self, neighbourID):
		if neighbourID not in self.neighbours: 
			print('Invalid Key'); 
			
		return self.neighbours[neighbourID];

	def del_neighbours(self, neighbourID): 
		if neighbourID not in self.neighbours: 
			print('Invalid Key'); 
		self.neighbours[neighbourID] = maxint; 

	# for dijkstra
	def get_dist(self):
		return self.dist; 

	def get_visited(self): 
		return self.visited;

	def get_prev(self): 
		return self.predecessor;

	def set_dist(self, newDist):
		self.dist = newDist; 

	def set_prev(self, prev):
		self.predecessor = prev; 

	def set_visited(self):
		self.visited = True; 

	def reset_visited(self): 
		self.visited = False;

	def reset_dist(self): 
		self.dist = maxint;

	def reset_prev(self): 
		self.predecessor = None; 

	# for node failure dection 
	def get_lives(self): 
		return self.lives;

	def reduce_lives(self): 
		self.lives = self.lives - 1; 

	def reset_lives(self):
		self.lives = 5; 

	def set_isDead(self): 
		self.isDead = True; 

	def get_isDead(self):
		return self.isDead; 

	def __str__(self): 
		return str(self.id) + ' Neighbours: ' + str([x for x in self.neighbours]);
