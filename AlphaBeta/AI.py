import pisqpipe as pp
import random
import win32api
import copy


WIN = 7
FLEX4 = 6
BLOCK4 = 5
FLEX3 = 4
BLOCK3 = 3
FLEX2 = 2
BLOCK2 = 1
MaxSize = 20		#  Max Board Size
branch = 20	   #  Max Branch Factor
Offen = 1.2 # Offensive factor
PVSSize = 1 << 20   #  PVS Transposition Table Size
MaxDepth = 20	   #  Max Search Depth
MinDepth = 2			#  Min Search Depth


#  Hash Table
hashfEXACT = 0
hashfALPHA = 1
hashfBETA = 2
valUNKNOWN = -20000
hashSize = 1 << 22  #  Hash Table Size


class Hash:
	def __init__(self):
		self.key=0
		self.depth=0
		self.hashf=0
		self.val=0

def QueryHash(depth, alpha, beta):
	hashEmt = hashTable[zobristKey & (hashSize - 1)]
	if hashEmt != 0:
		if hashEmt.key == zobristKey:
			if hashEmt.depth >= depth:
				if hashEmt.hashf == hashfEXACT:
					return hashEmt.val
				elif hashEmt.hashf == hashfALPHA and hashEmt.val <= alpha:
					return hashEmt.val
				elif hashEmt.hashf == hashfBETA and hashEmt.val >= beta:
					return hashEmt.val
	return valUNKNOWN


def WriteHash(depth, val, hashf):
	hashEmt = Hash()
	hashEmt.key = zobristKey
	hashEmt.val = val
	hashEmt.hashf = hashf
	hashEmt.depth = depth
	hashTable[zobristKey & (hashSize - 1)] = hashEmt

#  Roles of Points in Chessboard
White=0 # To perform a quick bit operation
Black=1
Empty=2
Outside=3


#  Directions
dx = [ 1, 0, 1, 1 ]
dy = [ 0, 1, 1, -1 ]

# Point for Analysis
class Point:
	def __init__(self):
		self.p=[0,0]
		self.val=0

#  Point in the Board
class Unit:
	def __init__(self):
		self.role=0			
		self.pattern=[[0 for i in range(4)] for j in range(2)]	# Pattern data for both sides
		self.neighbors=0

# Principal Variation
class PV:
	def __init__(self):
		self.key=0
		self.best=[0,0]

# Path
class Path:
	def __init__(self):
		self.n=0
		self.moves=[[0,0] for i in range(MaxDepth)]

# Possible moves
class Moves:
	def __init__(self):
		self.stage=0
		self.n=0
		self.index=0
		self.first=False
		self.hashMove=[0,0]
		self.moves=[[0,0] for i in range(64)]

# Other global variables
step = 0								#  Total step number
zobristKey = 0						  #  Current zobristKey


boardcopy=[[Unit()  for i in range(MaxSize+8)] for j in range(MaxSize+8)]			 #  A board copy
moved=[[0,0] for i in range((MaxSize * MaxSize))]	  #  Moves having been taken

cand=[Point() for i in range(400)]							 #  Candidates
my = Black							 #  Role of AI
opp = White							 #  Role of the opponent
rootMove=[Point() for i in range(64)]					  #  Possible moves the root can take
rootCount=0						   #  the used number of above


# For initializing evaluate function
def EvaluateHelper(len, dist, count, block):
	# count: my continuous units
	# len: my continuous units and empty units
	# block: boundary points
	# dist: the longest distance of my units in X-dim
	if len >= 5 and count > 1:
		if count == 5:
			return WIN
		if len > 5 and dist < 5 and block == 0:
			if count==2:
				return FLEX2
			if count==3:
				return FLEX3
			if count==4:
				return FLEX4
		else:
			if count==2:
				return BLOCK2
			if count==3:
				return BLOCK3
			if count==4:
				return BLOCK4
	return 0

# For initializing templates
def CreateTemplate():
	template=[[[[0 for k in range(3)]  for k in range(6)]  for i in range(6)] for j in range(10)]	
	for i in range(10):
		for j in range(6):
			for k in range(6):
				for l in range(3):
					template[i][j][k][l] = EvaluateHelper(i, j, k, l)
	return template
	
#  Help judge path type
def ShortPath(path):
	avai = 0
	block = 0
	len = 1
	dist = 1
	count = 1
	my = path[4]
	for k in range(5,9):
		if path[k] == my:
			if avai + count > 4: # 5-in-row for my and empty
				break
			count+=1
			len+=1
			dist = avai + count
		elif path[k] == Empty:
			len+=1
			avai+=1
		else:
			if path[k - 1] == my:
				block+=1
			break
	avai = dist - count	#  Calculate EMPTYs
	for k in range(3,-1,-1):
		if path[k] == my:
			if avai + count > 4:
				break
			count+=1
			len+=1
			dist = avai + count
		elif path[k] == Empty:
			len+=1
			avai+=1
		else:
			if path[k + 1] == my:
				block+=1
			break
	return template[len][dist][count][block]

#  Judge the path type of key
def PathType(role, key):
	path_left=[0]*9
	path_right=[0]*9
	
	for i in range(9): # Center is my
		if i == 4:
			path_left[i] = role
			path_right[i] = role
		else:
			path_left[i] = key & 3 # Every 2 bit represents a role
			path_right[8 - i] = key & 3
			key >>= 2

	#  2 directions
	p1 = ShortPath(path_left)
	p2 = ShortPath(path_right)
	
	#  Judge if FLEX3
	if p1 == BLOCK3 and p2 == BLOCK3:
		for i in range(9):
			if path_left[i] == Empty:
				path_left[i] = role # Empty->My => FLEX4 then FLEX3
				
				five = 0 
				for k in range(9):
					if path_left[k] == Empty:
						count = 0
						j = k - 1
						while j >= 0 and path_left[j] == role: 
							count+=1
							j-=1
						j = k + 1
						while j <= 8 and path_left[j] == role:
							count+=1
							j+=1
						if count >= 4:
							five+=1

				path_left[i] = Empty
				if five >= 2: 
					return FLEX3
		return BLOCK3
	#  Judge if FLEX4
	elif p1 == BLOCK4 and p2 == BLOCK4:
		five = 0
		for i in range(9):
			if path_left[i] == Empty:
				count = 0
				j = i - 1
				while j >= 0 and path_left[j] == role: 
					count+=1
					j-=1
				j = i + 1
				while j <= 8 and path_left[j] == role:
					count+=1
					j+=1
				if count >= 4:
					five+=1
		if five >= 2:
			return FLEX4
		return BLOCK4

	else:
		return p1 if p1 > p2 else p2

# Help create pattern table, note that key might be up to 1<<16
def createPatternTable():
	patternTable=[[0  for i in range(2)] for j in range(65536)]
	for key in range(65536):
		patternTable[key][0] = PathType(0, key) # mypattern
		patternTable[key][1] = PathType(1, key) 
	return patternTable 

# Help get and create the value table for tuple of types
def GetTupleValue(a, b, c, d):
	type = [ 0 ] * 8
	type[a]+=1
	type[b]+=1
	type[c]+=1
	type[d]+=1

	if type[WIN] > 0:
		return 5000
	if type[FLEX4] > 0  or type[BLOCK4] > 1:
		return 1200
	if type[BLOCK4] > 0 and type[FLEX3] > 0:
		return 1000
	if type[FLEX3] > 1:
		return 200

	val = [ 0, 2, 5, 5, 12, 12 ]
	score = 0
	for i in range(1,BLOCK4+1):
		score += val[i] * type[i]

	return score


def createTupleValue(): 
	tupleVal=[[[[0 for m in range(8)]  for k in range(8)]  for i in range(8)] for j in range(8)]	
	for i in range(8):
		for j in range(8):
			for k in range(8):
				for l in range(8):
					tupleVal[i][j][k][l] = GetTupleValue(i, j, k, l)
	return tupleVal

# For initializing zobrist table
def InitZobrist():
	zobrist= [[[0 for k in range(MaxSize + 4)]  for i in range(MaxSize + 4)] for j in range(2)]	
	for i in range(MaxSize + 4):
		for j in range(MaxSize + 4):
			zobrist[0][i][j] = random.getrandbits(64)
			zobrist[1][i][j] = random.getrandbits(64)
	return zobrist


def InitAll(_size):
	global template,patternTable,tupleVal,zobrist
	global size,b_start,b_end,boardcopy
	template = CreateTemplate()
	patternTable = createPatternTable()
	tupleVal = createTupleValue()
	zobrist = InitZobrist()

	size = _size
	b_start = 4
	b_end = size + 4
	for i in range(MaxSize + 8):
		for j in range(MaxSize + 8):
			if i < 4  or i >= size + 4  or j < 4  or j >= size + 4:
				boardcopy[i][j].role = Outside
			else:
				boardcopy[i][j].role = Empty

def GetKey(x, y, i):
	stepX = dx[i]
	stepY = dy[i]
	key = (boardcopy[x - stepX * 4][y - stepY * 4].role) ^ (boardcopy[x - stepX * 3][y - stepY * 3].role << 2) ^ (boardcopy[x - stepX * 2][y - stepY * 2].role << 4) ^ (boardcopy[x - stepX * 1][y - stepY * 1].role << 6) ^ (boardcopy[x + stepX * 1][y + stepY * 1].role << 8) ^ (boardcopy[x + stepX * 2][y + stepY * 2].role << 10) ^ (boardcopy[x + stepX * 3][y + stepY * 3].role << 12) ^ (boardcopy[x + stepX * 4][y + stepY * 4].role << 14)
	return key

#  Make move for analysis and match
def MakeMove(next):
	global my,zobristKey,opp,step,boardcopy,moved
	x = next[0]
	y = next[1]

	boardcopy[x][y].role = my
	zobristKey ^= zobrist[my][x][y]
	my ^= 1
	opp ^= 1
	moved[step] = [x,y]
	step+=1
	
	
	for i in range(4):
		for j in range(-4,5):
			a = x + j * dx[i]
			b = y + j * dy[i]
			if IsOutside(a,b):
				key = GetKey(a, b, i)
				boardcopy[a][b].pattern[0][i] = patternTable[key][0]
				boardcopy[a][b].pattern[1][i] = patternTable[key][1]
	
	# extend = 2
	for i in range(x - 2,x + 3):
		boardcopy[i][y - 2].neighbors+=1
		boardcopy[i][y - 1].neighbors+=1
		boardcopy[i][y].neighbors+=1
		boardcopy[i][y + 1].neighbors+=1
		boardcopy[i][y + 2].neighbors+=1

#  Delete moves for analysis
def DelMove():
	global my,opp,zobristKey,step,boardcopy
	step-=1
	x = moved[step][0]
	y = moved[step][1]

	my ^= 1
	opp ^= 1
	zobristKey ^= zobrist[my][x][y]
	boardcopy[x][y].role = Empty
	

	for i in range(4):
		for j in range(-4,5):
			a = x + j * dx[i]
			b = y + j * dy[i]
			if IsOutside(a,b):
				key = GetKey(a, b, i)
				boardcopy[a][b].pattern[0][i] = patternTable[key][0]
				boardcopy[a][b].pattern[1][i] = patternTable[key][1]
	# extend = 2
	for i in range(x - 2,x + 3):
		boardcopy[i][y - 2].neighbors-=1
		boardcopy[i][y - 1].neighbors-=1
		boardcopy[i][y].neighbors-=1
		boardcopy[i][y + 1].neighbors-=1
		boardcopy[i][y + 2].neighbors-=1


#  For initialize and restart
def ReStart():
	global hashTable,PVSTable,step
	hashTable=[0 for k in range(hashSize)]				   #  hash table 
	PVSTable=[0 for k in range(PVSSize)]						#  PVS table
	while step:
		DelMove()

# Make move for match
def PutChess(next):
	next[0] += 4
	next[1] += 4
	MakeMove(next)

#  Check the location if outside
def IsOutside(x, y):
	return boardcopy[x][y].role != Outside
#  Check 5-in-row
def IsWin():
	c = boardcopy[moved[step - 1][0]][moved[step - 1][1]]
	return c.pattern[opp][0] == WIN or c.pattern[opp][1] == WIN or c.pattern[opp][2] == WIN or c.pattern[opp][3] == WIN




searchDepth = 0			#  Search Depth
bestPoint = Point()		# The solution for current board
stopThink = False			# If stop continuing thinking



#  Time have been used this turn
def GetTime():
	return win32api.GetTickCount() - pp.start_time
#  Time limit for this turn
def StopTime():
	return pp.info_timeout_turn if (pp.info_timeout_turn < pp.info_time_left / 7) else pp.info_time_left / 7




#  Solve for current board
def Solve():
	best = IterDeep()[:]
	best[0] -= 4
	best[1] -= 4
	return best

#  Iteration Deepening
def IterDeep():
	global searchDepth,stopThink,IsLose,bestPoint
	bestMove=[0,0]
	#  Basic step rules of Gomoku
	if step == 0:
		bestMove[0] = size // 2 + 4
		bestMove[1] = size // 2 + 4
		return bestMove
	if step == 1  or  step == 2:
		x = moved[0][0] + random.randint(0,step * 2 ) - step
		y = moved[0][1] + random.randint(0,step * 2 ) - step
		while not IsOutside(x, y)  or  boardcopy[x][y].role != Empty:
			x = moved[0][0] + random.randint(0,step * 2)  - step
			y = moved[0][1] + random.randint(0,step * 2) - step
		bestMove[0] = x
		bestMove[1] = y
		return bestMove
	# ID
	stopThink = False
	bestPoint.val = 0
	IsLose=[[False  for i in range(MaxSize+4)] for j in range(MaxSize+4)]
	for i in range(MinDepth,MaxDepth+1,2):
		if stopThink:
			break
		searchDepth = i
		bestPoint= RootSearch(searchDepth, -10001, 10000)
		if stopThink  or  (searchDepth >= 10 and GetTime() >= 1000 and GetTime() * 12 > StopTime()):
			break
	bestMove = bestPoint.p[:]
	return bestMove



#  Search for best for root
def RootSearch(depth, alpha, beta):
	global rootCount,IsLose,rootMove
	global stopThink
	best = Point()
	best.p=rootMove[0].p[:]
	best.val=rootMove[0].val

	if depth == MinDepth:
		moves=[[0,0] for i in range(64)]
		rootCount = GetMoves(moves)
		if rootCount == 1:
			stopThink = True
			best.p = moves[0][:]
			best.val = 0
			return best

		for i in range(rootCount):
			rootMove[i].p = moves[i][:]
	else:
		for i in range(1,rootCount):
			if rootMove[i].val > rootMove[0].val:
				rootMove[0],rootMove[i]=rootMove[i],rootMove[0]
	val=0
	updateBest=False
	for i in range(rootCount):
		#  Search for POSSIBLE-WIN
		p = rootMove[i].p[:]
		if not IsLose[p[0]][p[1]]:
			MakeMove(p)
			for _ in range(1):
				if i > 0 and alpha + 1 < beta:
					val = -Analyze(depth - 1, -alpha - 1, -alpha)
					if val <= alpha  or  val >= beta:
						break
				val = -Analyze(depth - 1, -beta, -alpha)
			DelMove()

			rootMove[i].val = val

			if stopThink:
				break

			if val == -10000:
				IsLose[p[0]][p[1]] = True


			if val > alpha:
				alpha = val
				best.p = p[:]
				best.val = val
				updateBest = True

				# MUST-WIN
				if val == 10000:
					stopThink = True
					return best
	return best if updateBest else rootMove[0]

#  Seek points for move
def SeekPoint(myMoves):
	# Using PVS table
	if myMoves.stage==0:
		myMoves.stage = 1
		pv = PVSTable[zobristKey % PVSSize]
		if pv != 0 and pv.key == zobristKey:
			myMoves.hashMove = pv.best
			return pv.best
	# Generate all possible moves
	if myMoves.stage==1:
		myMoves.stage = 2
		myMoves.n = GetMoves(myMoves.moves)
		myMoves.index = 0
		if myMoves.first == False:
			for i in range(myMoves.n):
				if myMoves.moves[i][0] == myMoves.hashMove[0] and myMoves.moves[i][1] == myMoves.hashMove[1]:
					for j in range(i + 1 ,myMoves.n ):
						myMoves.moves[j - 1] = myMoves.moves[j]
					myMoves.n-=1
					break
	# Return all possible moves
	if myMoves.stage==2:
		if myMoves.index < myMoves.n:
			myMoves.index+=1
			return myMoves.moves[myMoves.index - 1]
	return [ -1, -1 ]

#  Write to PVS table
def WritePVS(best):
	global PVSTable
	pv = PV()
	pv.key = zobristKey
	pv.best = best[:]
	PVSTable[zobristKey % PVSSize] = pv

# Alpha-Beta Pruning using PVS
counter = 1000
def Analyze(depth, alpha, beta):
	global stopThink
	global counter
	counter-=1
	if counter <= 0:
		counter = 1000
		if GetTime() + 50 >= StopTime():
			stopThink = True
			return alpha
	# The other WIN
	if IsWin():
		return -10000
	#  Leaves
	if depth <= 0:
		return evaluate()

	#  Hash operations
	val = QueryHash(depth, alpha, beta)
	if val != valUNKNOWN:
		return val

	myMoves=Moves()
	myMoves.stage = 0
	myMoves.first = True
	p = SeekPoint(myMoves)
	best = Point()
	best.p=p[:]
	best.val=-10000
	hashf = hashfALPHA
	while p[0] != -1:
		MakeMove(p)
		for _ in range(1):
			if (not myMoves.first) and (alpha + 1 < beta):
				val = -Analyze(depth - 1, -alpha - 1, -alpha)
				if val <= alpha  or  val >= beta:
					break
			val = -Analyze(depth - 1, -beta, -alpha)
		DelMove()

		if stopThink:
			 return best.val

		if val >= beta:
			WriteHash(depth, val, hashfBETA)
			WritePVS(p)
			return val
		if val > best.val:
			best.val = val
			best.p = p[:]
			if val > alpha:
				hashf = hashfEXACT
				alpha = val
		p = SeekPoint(myMoves)
		myMoves.first = False

	WriteHash(depth, best.val, hashf)
	WritePVS(best.p)

	return best.val

#  Experienced Pruning
def PruneMoves(move, cand, candCount):
	# ABOVE FLEX4
	if cand[0].val >= 2400:                
		move[0] = cand[0].p[:]
		return 1
	moveCount = 0
	# THE OTHER FLEX3
	if cand[0].val == 1200:          
		# THE OTHER MIGHT FLEX4 or BLOCK4
		for i in range( candCount ):
			if cand[i].val == 1200:
				move[moveCount] = cand[i].p[:]
				moveCount+=1
			else:
				break

		flag = False
		for i in range(moveCount,candCount):
			p = boardcopy[cand[i].p[0]][cand[i].p[1]]
			for k in range(4):
				if p.pattern[my][k] == BLOCK4 or p.pattern[opp][k] == BLOCK4:
					flag = True
					break
			if flag == True:
				move[moveCount] = cand[i].p[:]
				moveCount+=1
				if moveCount >= branch:
					break
				
	return moveCount

#  Get possible moves
def GetMoves(move):
	global cand
	candCount = 0                # Count for candidates
	moveCount = 0                # Count for moves after sorting

	for i in range(b_start,b_end):
		for j in range(b_start,b_end):
			if boardcopy[i][j].neighbors and boardcopy[i][j].role == Empty:
				val = scorePoint(boardcopy[i][j])
				if val > 0:
					cand[candCount].p[0] = i
					cand[candCount].p[1] = j
					cand[candCount].val = val
					candCount+=1
	
	cand[0:candCount]=sorted(cand[0:candCount],key=lambda x:x.val,reverse=True)
	# Prune
	moveCount = PruneMoves(move, cand, candCount)
	# CANNOT Prune then use branch factor
	if moveCount == 0:
		for i in range(candCount):
			move[i] = cand[i].p[:]
			moveCount+=1
			if moveCount >= branch:
				break

	return moveCount

#  Evaluate function
def evaluate():
	eval= [ 0, 2, 12, 18, 96, 144, 800, 1200 ]
	myType = [ 0 ]   * 8            # My number of types
	oppType = [ 0 ]   * 8            # Opp number of types
	_BLOCK4 = 0				# Help judge if FLEX4 of my

	for i in range(b_start,b_end):
		for j in range(b_start,b_end):
			if boardcopy[i][j].neighbors and boardcopy[i][j].role == Empty:
				_BLOCK4 = myType[BLOCK4]
				for k in range(4):
					myType[boardcopy[i][j].pattern[my][k]]+=1
					oppType[boardcopy[i][j].pattern[opp][k]]+=1
				# FLEX4
				if myType[BLOCK4] - _BLOCK4 >= 2:
					myType[BLOCK4] -= 2
					myType[FLEX4] += 1

	# NOW my turn
	# MUST-WIN of my
	if myType[WIN] >= 1: 
		return 10000
	if (oppType[WIN] == 0 and myType[FLEX4] >= 1) :
		return 10000
	# MUST-WIN of opp
	if (oppType[WIN] >= 2) :
		return -10000

	global Offen
	# For other probabilities
	myScore = 0
	oppScore = 0
	for i in range(8):
		myScore += myType[i] * eval[i]
		oppScore += oppType[i] * eval[i]
	# 
	return myScore*Offen - oppScore

#  Score a Move Point
def scorePoint(c):
	score=[0]*2
	score[my] = tupleVal[c.pattern[my][0]][c.pattern[my][1]][c.pattern[my][2]][c.pattern[my][3]]
	score[opp] = tupleVal[c.pattern[opp][0]][c.pattern[opp][1]][c.pattern[opp][2]][c.pattern[opp][3]]

	#  ABOVE 2 FLEX3
	if score[my] >= 200  or  score[opp] >= 200:
		return score[my] * 2 if score[my] >= score[opp] else score[opp]
	#	Otherwise
	else:
		return score[my] * 2 + score[opp]
