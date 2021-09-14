

import pisqpipe as pp
from collections import defaultdict
from pisqpipe import DEBUG_EVAL, DEBUG
import copy
import time
from random import choice, shuffle
from math import log, sqrt
import win32api
from oldreiner import analyze_must

pp.infotext = 'name="pbrain-MCTS", author="Zheng HU(18307130208),Xiaoyi ZHU(18307130047)", version="1.0", country="China", www="https:#github.com/Aloereed"'

MAX_BOARD = 20
board = [[0 for i in range(MAX_BOARD)] for j in range(MAX_BOARD)]

direction = [(1,0),(0,1),(1,1),(1,-1)]
class Board():
	"""
	board for game
	"""

	def __init__(self):
		self.width = 20
		self.height = 20
		self.boardcopy=0			 #  board copy
		self.candidate =0 # available moves
		self.neighbours = set()
		self.win = 0
	
	def update(self, player, pos):
		global direction
		# update candidate and neighbours to be taken
		self.boardcopy[pos[0]][pos[1]] = player
		self.candidate.remove(pos)
		for i in range(max(0,pos[0]-2),min(pp.width,pos[0]+3)):
			for j in range(max(0,pos[1]-2),min(pp.width,pos[1]+3)):
				if (i,j) not in self.neighbours and (i,j) in self.candidate:
					self.neighbours.add((i,j))
		if (pos[0],pos[1]) in self.neighbours:
			self.neighbours.remove((pos[0],pos[1]))
		# Check winner
		for i in range(4):
			for k in range(-4,1):
				flag = True
				for j in range(5): 
					x = pos[0] + (k+j) * direction[i][0]
					y = pos[1] + (k+j) * direction[i][1]
					if x<0 or y<0 or x >= self.height or y>= self.width or self.boardcopy[x][y] != player:
						flag = False
						break
				if flag == True:
					self.win = player
					return 

#  Time have been used this turn
def GetTime():
	return win32api.GetTickCount() - pp.start_time
#  Time limit for this turn
def StopTime():
	return pp.info_timeout_turn if (pp.info_timeout_turn < pp.info_time_left / 7) else pp.info_time_left / 7

class MCTS:
	def __init__(self, board, max_actions=1000):
		self.board = board
		self.max_actions = max_actions

		self.player = 1 
		self.C = 1.96
		self.sims = {} # Simulations of (player, move)
		self.wins = {} # Wins of (player, move)
		self.K = 10000 
		self.max_depth = 1

	def GetMove(self):
		if len(self.board.candidate) == 1:
			return self.board.candidate[0]
 
		self.sims = {}	  
		self.wins = {}	  
		self.sims_rave = {} # {move:simulated times}
		self.wins_rave = {}  # {move:{player: win times}}
		simulations = 0

		while GetTime() + 50 < StopTime():
			counter = 100
			while counter:
				board_copy = copy.deepcopy(self.board) 
				self.Simulate(board_copy, self.player)
				simulations += 1
				counter-=1

		pos = self.SelectPos()
		return pos

	def Simulate(self, board, player):
		sims = self.sims
		wins = self.wins
		sims_rave = self.sims_rave
		wins_rave = self.wins_rave
		candidate = board.candidate
		neighbours = board.neighbours

		reached = set()
		winner = -1
		expand = True
		# Simulation
		for t in range(1, self.max_actions + 1):
			# Choose max UCB
			if all(sims.get((player, pos)) for pos in neighbours):
				_, pos = max(((1-sqrt(self.K/(3 * sims_rave[cand] + self.K))) * wins[(player, cand)] / sims[(player, cand)] + sqrt(self.K/(3 * sims_rave[cand] + self.K)) * wins_rave[cand][player] / sims_rave[cand] + sqrt(self.C * log(sims_rave[cand]) / sims[(player, cand)]), cand) for cand in neighbours)
			else:
				if len(neighbours):
					pos = choice(list(neighbours))
				else:
					peripherals = []
					for pos in candidate:
						if not sims.get((player, pos)):
							peripherals.append(pos)
					pos = choice(peripherals)

			board.update(player, pos)

			# Expand children
			if expand and (player, pos) not in sims:
				expand = False
				sims[(player, pos)] = 0
				wins[(player, pos)] = 0
				if pos not in sims_rave:
					sims_rave[pos] = 0
				if pos in wins_rave:
					wins_rave[pos][player] = 0
				else:
					wins_rave[pos] = {player: 0}
				if t > self.max_depth:
					self.max_depth = t

			reached.add((player, pos))

			full = not len(candidate)
			winner = board.win
			if full or (winner!=0):
				break

			player = 3-player

		# Back-propagation
		for player, pos in reached:
			if (player, pos) in sims:
				sims[(player, pos)] += 1
				if player == winner:
					wins[(player, pos)] += 1
			if pos in sims_rave:
				sims_rave[pos] += 1
				if winner in wins_rave[pos]:
					wins_rave[pos][winner] += 1

	def SelectPos(self):
		neighbours = self.board.neighbours
		_, pos = max(
			(self.wins.get((self.player, pos), 0) /
			 self.sims.get((self.player, pos), 1),
			 pos)
			for pos in neighbours)
		return pos 


ourboard = Board()


def brain_init():
	global ai,ourboard
	if pp.width < 5 or pp.height < 5:
		pp.pipeOut("ERROR size of the board")
		return
	if pp.width > MAX_BOARD or pp.height > MAX_BOARD:
		pp.pipeOut("ERROR Maximal board size is {}".format(MAX_BOARD))
		return
	ourboard.boardcopy=[[0  for i in range(pp.height)] for j in range(pp.width)]
	ourboard.candidate = [(i,j)  for i in range(pp.height) for j in range(pp.width)] 
	ai = MCTS(ourboard)
	pp.pipeOut("OK")

def brain_restart():
	for x in range(pp.width):
		for y in range(pp.height):
			board[x][y] = 0
	pp.pipeOut("OK")

def isFree(x, y):
	return x >= 0 and y >= 0 and x < pp.width and y < pp.height and board[x][y] == 0

def brain_my(x, y):
	if isFree(x,y):
		board[x][y] = 1
		ourboard.update(1, (x,y))
	else:
		pp.pipeOut("ERROR my move [{},{}]".format(x, y))

def brain_opponents(x, y):
	if isFree(x,y):
		board[x][y] = 2
		ourboard.update(2, (x,y))
	else:
		pp.pipeOut("ERROR opponents's move [{},{}]".format(x, y))

def brain_block(x, y):
	if isFree(x,y):
		board[x][y] = 3
	else:
		pp.pipeOut("ERROR winning move [{},{}]".format(x, y))

def brain_takeback(x, y):
	if x >= 0 and y >= 0 and x < pp.width and y < pp.height and board[x][y] != 0:
		board[x][y] = 0
		return 0
	return 2

def brain_turn():

	if pp.terminateAI:
		return
	i = 0
	flag = 0
	for k in range(pp.width):
		for j in range(pp.height):
			if not isFree(k,j):
				flag = 1
	while True:
		if flag == 0:
			x = pp.width//2
			y = pp.height//2
		if flag==1:
			(pos,_) = analyze_must([[board[x][y] for y in range(pp.height)] for x in range(pp.width)])
			if pos==(-1,-1):
				pos = ai.GetMove()
				x = pos[0]
				y = pos[1]
			else:
				x,y=pos
		i += 1
		if pp.terminateAI:
			return
		if isFree(x,y):
			break
	if i > 1:
		pp.pipeOut("DEBUG {} coordinates didn't hit an empty field".format(i))
	pp.do_mymove(x, y)
	#board[x][y]=1


def brain_end():
	pass

def brain_about():
	pp.pipeOut(pp.infotext)

if DEBUG_EVAL:
	import win32gui
	def brain_eval(x, y):
		# TODO check if it works as expected
		wnd = win32gui.GetForegroundWindow()
		dc = win32gui.GetDC(wnd)
		rc = win32gui.GetClientRect(wnd)
		c = str(board[x][y])
		win32gui.ExtTextOut(dc, rc[2]-15, 3, 0, None, c, ())
		win32gui.ReleaseDC(wnd, dc)

######################################################################
# A possible way how to debug brains.
# To test it, just "uncomment" it (delete enclosing """)
######################################################################

# # define a file for logging ...
# DEBUG_LOGFILE = "Y:\\pbrain-pyrandom.log"
# # ...and clear it initially
# with open(DEBUG_LOGFILE,"w") as f:
# 	pass

# # define a function for writing messages to the file
# def logDebug(msg):
# 	with open(DEBUG_LOGFILE,"a") as f:
# 		f.write(msg+"\n")
# 		f.flush()

# # define a function to get exception traceback
# def logTraceBack():
# 	import traceback
# 	with open(DEBUG_LOGFILE,"a") as f:
# 		traceback.print_exc(file=f)
# 		f.flush()
# 	raise
"""
# use logDebug wherever
# use try-except (with logTraceBack in except branch) to get exception info
# an example of problematic function
def brain_turn():
	logDebug("some message 1")
	try:
		logDebug("some message 2")
		1. / 0. # some code raising an exception
		logDebug("some message 3") # not logged, as it is after error
	except:
		logTraceBack()
"""
######################################################################

# "overwrites" functions in pisqpipe module
pp.brain_init = brain_init
pp.brain_restart = brain_restart
pp.brain_my = brain_my
pp.brain_opponents = brain_opponents
pp.brain_block = brain_block
pp.brain_takeback = brain_takeback
pp.brain_turn = brain_turn
pp.brain_end = brain_end
pp.brain_about = brain_about
if DEBUG_EVAL:
	pp.brain_eval = brain_eval

def main():
	pp.main()

if __name__ == "__main__":
	main()
