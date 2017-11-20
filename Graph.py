# python 2.7.12 
# Graph class 

from sys import * 
from Vertex import * 

class Graph:
	def __init__(self):
		# dictionary of vertex 
		self.vertex_dict = {}; 
		self.num_vertices = 0; 

	def __iter__(self): 
		return iter(self.vertex_dict.values()); 

	# add new vertex into graph 
	# duplicate vertexID is ignored 
	def add_vertex(self, newVertexID, newVertexPort):
		if newVertexID not in self.vertex_dict: 
			self.num_vertices = self.num_vertices + 1; 
			# create new vertex, add to vertex_dict
			newVertex = Vertex(newVertexID, newVertexPort);  
			self.vertex_dict[newVertexID] = newVertex;  

	# add link between routers 
	def add_linkCost(self, srcVertexID, destVertexID, linkCost):
		# just to be safe but not really needed 
		if srcVertexID not in self.vertex_dict:
			#print ('Make ' + srcVertexID);
			self.add_vertex(srcVertexID, None); 
		if destVertexID not in self.vertex_dict: 
			#print ('Make ' + destVertexID);
			self.add_vertex(destVertexID, None); 

		# undirected graph 
		# update link cost 
		self.vertex_dict[srcVertexID].add_neighbours(destVertexID, linkCost); 
		self.vertex_dict[destVertexID].add_neighbours(srcVertexID, linkCost); 

	# remove link between routers 
	def del_linkCost(self, srcVertexID, destVertexID): 
		if srcVertexID not in self.vertex_dict:
			print ('No node ' + srcVertexID +' to del'); 
		if destVertexID not in self.vertex_dict: 
			print ('No node ' + destVertexID +' to del');

		self.vertex_dict[srcVertexID].del_neighbours(destVertexID); 
		self.vertex_dict[destVertexID].del_neighbours(srcVertexID); 

	# remove vertex from graph 
	def del_vertex(self, srcVertexID): 
		del self.vertex_dict[srcVertexID]; 

	# retrieve info about a specific vertex given its ID 
	def get_vertex(self, vertexID): 
		if vertexID in self.vertex_dict: 
			return self.vertex_dict[vertexID]; 
		else: 
			return None; 

	# retrieve all vertices in graph 
	def get_vertices(self):
		return self.vertex_dict.keys(); 

	# display graph - for debug 
	def show_graph(self):
		for itemID in self.vertex_dict.keys():
			currVertex = self.vertex_dict.get(itemID); 
			print(currVertex);
			# display cost to each neighbour
			for neighbourID in currVertex.get_neighbourID():
				print(itemID + '  -  ' + neighbourID + ' :  ' + str((currVertex.get_linkCost(neighbourID))));
			print('\n'); 