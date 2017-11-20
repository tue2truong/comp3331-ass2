# python 2.7.12 
# IMPORTANT : Please use Ctrl + Z to stop a program from running

from sys import * 
from socket import * 
import os 
import pickle 
import time 
import heapq
from threading import *
from Graph import *
from Vertex import * 

class Lsr: 

	# define 
	NODE_ID = 0; 
	DATA = 1;
	SEQ_NUM = 2; 

	UPDATE_INTERVAL = 1; 
	ROUTE_UPDATE_INTERVAL = 30; 

	UNREACHABLE = maxint;

	def __init__(self, argv): 
		# input 
		self.nodeID = str(argv[1]);
		self.nodePort = int(argv[2]); 
		self.config = str(argv[3]); 
		self.seqNum = 0; 
		self.aliveQueue = [];
		self.deadQueue  = []; 
		self.lastSeqNumRecv = {};

		# set up UDP socket 
		self.ip_addr = '127.0.0.1';
		routerSocket = socket(AF_INET, SOCK_DGRAM); 
		routerSocket.bind(('', self.nodePort)); 

		# create graph 
		# node curr view of the topology 
		self.routerMap = Graph(); 
		self.routerMap.add_vertex(self.nodeID, self.nodePort);  
		
		# process config file 
		# update router map 
		# create link state packet 
		self.curr_lsp = self.create_packet();

		# Link state advertisement 
		thread_broadcast = Thread(target=self.broadcast_lsp, args=(routerSocket, self.curr_lsp,));
		thread_forward = Thread(target=self.forward_lsp, args=(routerSocket,));

		# Dijkstra algorithm 
		# compute shortest path to all nodes
		thread_dijkstra = Thread(target=self.program_output, args=());

		# Checl alive thread - making sure all neighbours are alive 
		thread_check_alive = Thread(target=self.check_alive, args=()); 

		# starting all threads
		thread_broadcast.start();
		thread_forward.start(); 
		thread_dijkstra.start(); 

		# wait 6 second before the checking_alive thread run 
		# so that when the program doest not start simultaneously 
		# node does not think that its neighbour is dead 
		time.sleep(6); 
		thread_check_alive.start();

		# for debug only  
		#thread_show_map = Thread(target=self.show_map, args=()); 
		#thread_show_map.start(); 
		
	# process config files, update router map,
	# create first link state packet  
	def create_packet(self):
		with open(self.config, "r") as myFile: 
			content = myFile.read().splitlines();

		#create link state packet - lsp
		# packet contains nodeID and its data (linkCost to neighbours)
		lsp = [self.nodeID]; 
		lsp_data = {}; 

		for entry in content[1:]:
			# update router map 
			neighbourID, dist, neighbourPort = entry.split(); 
			self.routerMap.add_vertex(neighbourID, neighbourPort);
			self.routerMap.add_linkCost(self.nodeID, neighbourID, dist);

			# update lsp data
			lsp_data.update({neighbourID : float(dist)}); 

		lsp.append(lsp_data); 
		lsp.append(self.seqNum); 
		return lsp; 


	# receive link state packet from neighbours
	# update current router map 
	# forward to neighbours - naive flood 
	def forward_lsp(self, routerSocket): 
		while True: 
			packed_lsp, neighbourAddr = routerSocket.recvfrom(1024); 
			lsp = pickle.loads(packed_lsp); 

			srcNodeID = lsp[self.NODE_ID]; 
			srcNode = self.routerMap.get_vertex(srcNodeID); 
			costDict = lsp[self.DATA];

			srcSeqNumber = lsp[self.SEQ_NUM]; 

			# update last seq number receive 
			if srcNodeID not in self.lastSeqNumRecv: 
				new_entry = {srcNodeID : -1}; 
				self.lastSeqNumRecv.update(new_entry);  
				 
			currNode = self.routerMap.get_vertex(self.nodeID); 
			if srcNodeID in currNode.get_neighbourID() and srcNodeID not in self.aliveQueue: 
				self.aliveQueue.append(srcNodeID);   

			# update router map based on LSP
			for key, value in costDict.iteritems():
				# if the node is dead 
				if costDict[key] >= self.UNREACHABLE:
					self.routerMap.get_vertex(key).set_isDead();
				# update routermap 
				self.routerMap.add_linkCost(srcNodeID, key, value); 

			# forward packet to neighbours
			for neighbourID in currNode.get_neighbourID(): 
				if self.lastSeqNumRecv[srcNodeID] == srcSeqNumber: 
					break;  
				neighbourNode = self.routerMap.get_vertex(neighbourID);
				neighbourPort = int(neighbourNode.get_port()); 
 
				if neighbourPort == neighbourAddr[1]: 
					continue; 
				routerSocket.sendto(pickle.dumps(lsp), (self.ip_addr, neighbourPort)); 

			# update last seq receives from srcNode 
			if self.lastSeqNumRecv[srcNodeID] != srcSeqNumber: 
				self.lastSeqNumRecv[srcNodeID] = srcSeqNumber; 

	
	# constantly broacast link state packet to neighbours
	def broadcast_lsp(self, routerSocket, packetToSend):
		while True: 
			time.sleep(self.UPDATE_INTERVAL);
			currNode = self.routerMap.get_vertex(self.nodeID); 
			for neighbourID in currNode.get_neighbourID(): 
				neighbourNode = self.routerMap.get_vertex(neighbourID); 
				neighbourPort = int(neighbourNode.get_port());  
				routerSocket.sendto(pickle.dumps(packetToSend), (self.ip_addr, neighbourPort));  


	# constantly check aliveQueue every 1 second 
	def check_alive(self): 
		while True: 
			time.sleep(1); 
		 
			# detect node failures in neighbours 
			currNode = self.routerMap.get_vertex(self.nodeID);
			for neighbourID in currNode.get_neighbourID():
				neighbour = self.routerMap.get_vertex(neighbourID); 
				if neighbourID not in self.aliveQueue: 
					neighbour.reduce_lives(); 
				else: 
					neighbour.reset_lives(); 

				# detect neighbour is dead 
				if neighbour.get_lives() == 0: 
					print('Node ' + neighbour.get_id() + ' dead'); 
					self.deadQueue.append(neighbour);
					neighbour.set_isDead();  

			# clear aliveQueue  
			del self.aliveQueue[:]; 

			# remove dead node
			# update to new router map  
			self.remove_dead(); 


	# remove dead node in dead queue 
	def remove_dead(self): 
		currNode = self.routerMap.get_vertex(self.nodeID); 
		currPacketData = self.curr_lsp[self.DATA]; 

		for deadNode in self.deadQueue: 
			# update link state packet 
			if currPacketData.has_key(deadNode.get_id()):
				currPacketData[deadNode.get_id()] = maxint;
				self.seqNum = self.seqNum + 1; 
				self.curr_lsp[self.SEQ_NUM] = self.seqNum;   

			# update router map  
			for neighbourID in deadNode.get_neighbourID(): 
				self.routerMap.del_linkCost(deadNode.get_id(), neighbourID);  

		del self.deadQueue[:];

	
	def show_map(self): 
		while True: 

			time.sleep(30); 
			self.routerMap.show_graph(); 
			print('LSP  ' + str(self.curr_lsp)); 

		
	# Dijkstra algorithm 
	def dijkstra(self, startID):
		print ('Performing Dijkstra...'); 
		startNode = self.routerMap.get_vertex(startID); 

		startNode.set_dist(0); 

		unvisitedQueue = [(v.get_dist(), v) for v in self.routerMap if not v.get_isDead()]; 
		heapq.heapify(unvisitedQueue); 

		while len(unvisitedQueue):
			currEntry = heapq.heappop(unvisitedQueue); 
			currVertex = currEntry[1]; 
			currVertex.set_visited(); 

			# inspect all the neighbours of currVertex 
			# update its cost 
			for nextVertexID in currVertex.get_neighbourID():
				nextVertex = self.routerMap.get_vertex(nextVertexID);  
				if(nextVertex.get_visited()): 
					continue; 

				newDistance = float(currVertex.get_dist()) + float(currVertex.get_linkCost(nextVertexID)); 
				if(newDistance < nextVertex.get_dist()): 
					nextVertex.set_dist(newDistance); 
					nextVertex.set_prev(currVertex); 

			# rebuild heapq 
			while len(unvisitedQueue): 
				heapq.heappop(unvisitedQueue); 
			# place all vertices that is not visited back and not dead to queue 
			unvisitedQueue = [(v.get_dist(), v) for v in self.routerMap if not v.get_visited() and not v.get_isDead()]; 
			heapq.heapify(unvisitedQueue);  


	# construct the shortest path to all other nodes 
	def shortestPath(self, currVertex, path): 
		if currVertex.get_prev(): 
			path.append(currVertex.get_prev().get_id()); 
			self.shortestPath(currVertex.get_prev(), path); 
		return; 


	# display program output to stdout 
	def program_output(self): 
		while True: 
			time.sleep(self.ROUTE_UPDATE_INTERVAL);
			
			# re-initialise variables for dijkstra 
			for neighbour in self.routerMap: 
				neighbour.reset_visited(); 
				neighbour.reset_dist();
				neighbour.reset_prev(); 
			
			# performing dijkstra 
			self.dijkstra(self.nodeID); 
			 
			# display shortest path to output 
			for neighbour in self.routerMap: 
				neighbourID = neighbour.get_id(); 
				if neighbourID == self.nodeID: 
					continue;
				if neighbour.get_isDead() == True: 
					continue; 
				path=[neighbourID];
				self.shortestPath(neighbour, path);
				print ('least-cost path to node %s : %s and the cost is %s' %(neighbourID ,path[::-1] , neighbour.get_dist())); 
			print('\n'); 


# main code execution 
def main(argv):
	Lsr(argv);

main(argv); 
