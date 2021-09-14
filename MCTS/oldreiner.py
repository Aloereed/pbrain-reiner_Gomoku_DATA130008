import random
import pisqpipe as pp
from collections import defaultdict
from pisqpipe import DEBUG_EVAL, DEBUG
import copy
import win32api

'''
This is the midterm AI of Alpha-Beta, and most codes here are useless.
This file is just for MCTS Agent to find moves that HAVE TO be taken, otherwise
it'll lose IMMEDIATELY, in less than 0.1s (analyze_must).
'''
pp.infotext = 'name="pbrain-reiner", author="Zheng HU(18307130208),Xiaoyi ZHU(18307130047)", version="1.0", country="China", www="https:#github.com/Aloereed"'

MAX_BOARD = 20
board = [[0 for i in range(MAX_BOARD)] for j in range(MAX_BOARD)]

OTHER=0
WIN=1
LOSE=2
FLEX4=3
flex4=4
BLOCK4=5
block4=6
FLEX3=7
flex3=8
BLOCK3=9
block3=10
FLEX2=11
flex2=12
BLOCK2=13
block2=14
FLEX1=15
flex1=16
# weight = [0,1000000,-1000000,50000,-100000,400,-100000,400,-8000,20,-50,20,-50,1,-3,1,-3]

# chess = dict() # For HASH


def brain_init():
	if pp.width < 5 or pp.height < 5:
		pp.pipeOut("ERROR size of the board")
		return
	if pp.width > MAX_BOARD or pp.height > MAX_BOARD:
		pp.pipeOut("ERROR Maximal board size is {}".format(MAX_BOARD))
		return
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
	else:
		pp.pipeOut("ERROR my move [{},{}]".format(x, y))

def brain_opponents(x, y):
	if isFree(x,y):
		board[x][y] = 2
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

def createtemplate(): # 我们这里设置判断边界为-1
	template = defaultdict(int)
	# 敌方连五
	for i in range(-1,3):
		template[(i,2,2,2,2,2)] = LOSE
		template[(2,2,2,2,2,i)] = LOSE
	# 我方连五
	for i in range(-1,3):
		template[(i,1,1,1,1,1)] = WIN
		template[(1,1,1,1,1,i)] = WIN
	# 敌方活四
	template[(0,2,2,2,2,0)] = flex4
	# 我方活四
	template[(0,1,1,1,1,0)] = FLEX4
	# 敌方活三
	template[(0,2,2,2,0,0)] = flex3
	template[(0,0,2,2,2,0)] = flex3
	template[(0,2,0,2,2,0)] = flex3
	template[(0,2,2,0,2,0)] = flex3
	# 我方活三
	template[(0,1,1,1,0,0)] = FLEX3
	template[(0,0,1,1,1,0)] = FLEX3
	template[(0,1,0,1,1,0)] = FLEX3
	template[(0,1,1,0,1,0)] = FLEX3
	# 敌方活二
	template[(0,2,2,0,0,0)] = flex2
	template[(0,0,2,2,0,0)] = flex2
	template[(0,0,0,2,2,0)] = flex2
	template[(0,2,0,0,2,0)] = flex2
	template[(0,2,0,2,0,0)] = flex2
	template[(0,0,2,0,2,0)] = flex2
	# 我方活二
	template[(0,1,1,0,0,0)] = FLEX2
	template[(0,0,1,1,0,0)] = FLEX2
	template[(0,0,0,1,1,0)] = FLEX2
	template[(0,1,0,0,1,0)] = FLEX2
	template[(0,1,0,1,0,0)] = FLEX2
	template[(0,0,1,0,1,0)] = FLEX2
	# 敌方活一
	template[(0,2,0,0,0,0)] = flex1
	template[(0,0,2,0,0,0)] = flex1
	template[(0,0,0,2,0,0)] = flex1
	template[(0,0,0,0,2,0)] = flex1
	# 我方活一
	template[(0,1,0,0,0,0)] = FLEX1
	template[(0,0,1,0,0,0)] = FLEX1
	template[(0,0,0,1,0,0)] = FLEX1
	template[(0,0,0,0,1,0)] = FLEX1

	leftmy = 0
	rightmy = 0
	leftopp = 0
	rightopp = 0
	for p1 in range(-1,3):
		for p2 in range(3):
			for p3 in range(3):
				for p4 in range(3):
					for p5 in range(3):
						for p6 in range(-1,3):
							leftmy = 0
							rightmy = 0
							leftopp = 0
							rightopp = 0
							 
							if p1 == 1: 
								leftmy += 1
							elif p1 == 2:
								leftopp += 1
							if p2 == 1: 
								leftmy += 1
								rightmy += 1
							elif p2 == 2:
								leftopp += 1
								rightopp += 1
							if p3 == 1: 
								leftmy += 1
								rightmy += 1
							elif p3 == 2:
								leftopp += 1
								rightopp += 1
							if p4 == 1: 
								leftmy += 1
								rightmy += 1
							elif p4 == 2:
								leftopp += 1
								rightopp += 1
							if p5 == 1: 
								leftmy += 1
								rightmy += 1
							elif p5 == 2:
								leftopp += 1
								rightopp += 1
							if p6 == 1: 
								rightmy += 1
							elif p6 == 2:
								rightopp += 1

							if p1 == -1:
								# 我方冲4
								if(rightopp==0 and rightmy==4):#若右边有空位是活4也没关系，因为活4权重远大于冲4，再加上冲4权重变化可以不计
									if(template[(p1,p2,p3,p4,p5,p6)]==0):
										template[(p1,p2,p3,p4,p5,p6)]=BLOCK4
								
								#敌方冲4
								if(rightopp==4 and rightmy==0):
									if(template[(p1,p2,p3,p4,p5,p6)]==0):
										template[(p1,p2,p3,p4,p5,p6)]=block4
								
								#我方眠3
								if(rightopp==0 and rightmy==3):
									if(template[(p1,p2,p3,p4,p5,p6)]==0):
										template[(p1,p2,p3,p4,p5,p6)]=BLOCK3
								
								#敌方眠3
								if(rightopp==3 and rightmy==0):
									if(template[(p1,p2,p3,p4,p5,p6)]==0):
										template[(p1,p2,p3,p4,p5,p6)]=block3
								
								#我方眠2
								if(rightopp==0 and rightmy==2):
									if(template[(p1,p2,p3,p4,p5,p6)]==0):
										template[(p1,p2,p3,p4,p5,p6)]=BLOCK2
								
								#敌方眠2
								if(rightopp==2 and rightmy==0):
									if(template[(p1,p2,p3,p4,p5,p6)]==0):
										template[(p1,p2,p3,p4,p5,p6)]=block2
									
							if p6 == -1: 
								#我方冲4
								if(leftopp==0 and leftmy==4):
									if(template[(p1,p2,p3,p4,p5,p6)]==0):
										template[(p1,p2,p3,p4,p5,p6)]=BLOCK4
								
								#敌方冲4
								if(leftopp==4 and leftmy==0):
									if(template[(p1,p2,p3,p4,p5,p6)]==0):
										template[(p1,p2,p3,p4,p5,p6)]=block4
									 
								#敌方眠3
								if(leftopp==3 and leftmy==0):
									if(template[(p1,p2,p3,p4,p5,p6)]==0):
										template[(p1,p2,p3,p4,p5,p6)]=block3
								
								#我方眠3
								if(leftopp==0 and leftmy==3):
									if(template[(p1,p2,p3,p4,p5,p6)]==0):
										template[(p1,p2,p3,p4,p5,p6)]=BLOCK3
								
								#敌方眠2
								if(leftopp==2 and leftmy==0):
									if(template[(p1,p2,p3,p4,p5,p6)]==0):
										template[(p1,p2,p3,p4,p5,p6)]=block2
								
								#我方眠2
								if(leftopp==0 and leftmy==2):
									if(template[(p1,p2,p3,p4,p5,p6)]==0):
										template[(p1,p2,p3,p4,p5,p6)]=BLOCK2
								
							# 我方冲4
							if((leftopp==0 and leftmy==4) or (rightopp==0 and rightmy==4)):
								if(template[(p1,p2,p3,p4,p5,p6)]==0):
									template[(p1,p2,p3,p4,p5,p6)]=BLOCK4
							
							# 敌方冲4
							if((leftopp==4 and leftmy==0) or (rightopp==4 and rightmy==0)):
								if(template[(p1,p2,p3,p4,p5,p6)]==0):
									template[(p1,p2,p3,p4,p5,p6)]=block4
							
							# 我方眠3
							if((leftopp==0 and leftmy==3) or (rightopp==0 and rightmy==3)):
								if(template[(p1,p2,p3,p4,p5,p6)]==0):
									template[(p1,p2,p3,p4,p5,p6)]=BLOCK3
							
							# 敌方眠3
							if((leftopp==3 and leftmy==0) or (rightopp==3 and rightmy==0)):
								if(template[(p1,p2,p3,p4,p5,p6)]==0):
									template[(p1,p2,p3,p4,p5,p6)]=block3
							
							# 我方眠2
							if((leftopp==0 and leftmy==2) or (rightopp==0 and rightmy==2)):
								if(template[(p1,p2,p3,p4,p5,p6)]==0):
									template[(p1,p2,p3,p4,p5,p6)]=BLOCK2
							
							# 敌方眠2
							if((leftopp==2 and leftmy==0) or (rightopp==2 and rightmy==0)):
								if(template[(p1,p2,p3,p4,p5,p6)]==0):
									template[(p1,p2,p3,p4,p5,p6)]=block2
	return template	

template = createtemplate()						   



class evaluate:
	def __init__(self, tmpboard):
		self.score = 0 # 分数
		self.gameresult = 0 # -1是敌方赢，0是平局/未分出胜负，1是我方赢
		self.STAT = [0]*17
		self.board = tmpboard

	def eval(self):
		weight = [0,1000000,-1000000,50000,-100000,400,-100000,400,-8000,20,-50,20,-50,1,-3,1,-3]
		stat_all = [[0 for i in range(17)] for j in range(4)]

		entendedboard = [[False for i in range(pp.width+2)] for j in range(pp.height+2)]
		for i in range(pp.width+2):
			entendedboard[0][i] = -1
			entendedboard[pp.height+1][i] = -1
		for i in range(pp.height+2):
			entendedboard[i][0] = -1
			entendedboard[i][pp.width+1] = -1
		for x in range(pp.width):
			for y in range(pp.height):
				entendedboard[x+1][y+1] = self.board[x][y]

		# 横向
		for x in range(1,pp.height+1):
			for y in range(pp.width-3):
				tu = (entendedboard[x][y],entendedboard[x][y+1],entendedboard[x][y+2],entendedboard[x][y+3],entendedboard[x][y+4],entendedboard[x][y+5])
				stat_all[0][template[tu]] += 1
		# 纵向
		for y in range(1,pp.width+1):
			for x in range(pp.height-3):
				tu = (entendedboard[x][y],entendedboard[x+1][y],entendedboard[x+2][y],entendedboard[x+3][y],entendedboard[x+4][y],entendedboard[x+5][y])
				stat_all[1][template[tu]] += 1
		# 左上至右下
		for x in range(pp.height-3):
			for y in range(pp.width-3):
				tu = (entendedboard[x][y],entendedboard[x+1][y+1],entendedboard[x+2][y+2],entendedboard[x+3][y+3],entendedboard[x+4][y+4],entendedboard[x+5][y+5])
				stat_all[2][template[tu]] += 1
		for x in range(pp.height-3):
			for y in range(5,pp.width+2):
				tu = (entendedboard[x][y],entendedboard[x+1][y-1],entendedboard[x+2][y-2],entendedboard[x+3][y-3],entendedboard[x+4][y-4],entendedboard[x+5][y-5])
				stat_all[3][template[tu]] += 1
		
		for i in range(17):
			for j in range(4):
				self.STAT[i] += stat_all[j][i]
			if self.STAT[i] != 0:
				self.score += self.STAT[i] * weight[i]

		if self.STAT[WIN] > 0:
			self.gameresult = 1
		if self.STAT[LOSE] > 0:
			self.gameresult = -1
		return 0 

def isValid(x, y):
	return x >= 0 and y >= 0 and x < pp.width and y < pp.height
		
def scorepoint(tmpboard,pos,role):
	weight = [0,1000000,-1000000,50000,-100000,400,-100000,400,-8000,20,-50,20,-50,1,-3,1,-3]
	score = 0
	before  = tmpboard[pos[0]][pos[1]]
	tmpboard[pos[0]][pos[1]] = role

	if pos[0]-5 < 0: # 触及上边界
		tu = (-1,tmpboard[0][pos[1]],tmpboard[1][pos[1]],tmpboard[2][pos[1]],tmpboard[3][pos[1]],tmpboard[4][pos[1]])
		score += weight[template[tu]]
	if pos[0]+5 >= pp.height: # 触及下边界
		tu = (tmpboard[pp.height-5][pos[1]],tmpboard[pp.height-4][pos[1]],tmpboard[pp.height-3][pos[1]],tmpboard[pp.height-2][pos[1]],tmpboard[pp.height-1][pos[1]],-1)
		score += weight[template[tu]]
	if pos[1]-5 < 0: # 触及左边界
		tu = (-1,tmpboard[pos[0]][0],tmpboard[pos[0]][1],tmpboard[pos[0]][2],tmpboard[pos[0]][3],tmpboard[pos[0]][4])
		score += weight[template[tu]]
	if pos[1]-5 >=pp.width: # 触及右边界
		tu = (tmpboard[pos[0]][pp.width-5],tmpboard[pos[0]][pp.width-4],tmpboard[pos[0]][pp.width-3],tmpboard[pos[0]][pp.width-2],tmpboard[pos[0]][pp.width-1],-1)
		score += weight[template[tu]]

	for x in range(max(0,pos[0]-5),min(pos[0],pp.height-6)):
		tu = (tmpboard[x][pos[1]],tmpboard[x+1][pos[1]],tmpboard[x+2][pos[1]],tmpboard[x+3][pos[1]],tmpboard[x+4][pos[1]],tmpboard[x+5][pos[1]])
		score += weight[template[tu]]
	for y in range(max(0,pos[1]-5),min(pos[1],pp.width-6)):
		tu = (tmpboard[pos[0]][y],tmpboard[pos[0]][y+1],tmpboard[pos[0]][y+2],tmpboard[pos[0]][y+3],tmpboard[pos[0]][y+4],tmpboard[pos[0]][y+5])
		score += weight[template[tu]]

	# 左上到右下
	flag1 = -9999 # 判断边界的flag
	flag2 = -9999
	for i in range(-5,6):
		if isValid(pos[0]+i,pos[1]+i) and flag1 == -9999:
			flag1 = i
	for i in range(5,-6,-1):
		if isValid(pos[0]+i,pos[1]+i) and flag2 == -9999:
			flag2 = i
	if flag2 - flag1 >= 3:
		if flag1 != -5:
			if flag2 - flag1 == 3:
				tu = (-1,tmpboard[pos[0]+flag1][pos[1]+flag1],tmpboard[pos[0]+flag1+1][pos[1]+flag1+1],tmpboard[pos[0]+flag1+2][pos[1]+flag1+2],tmpboard[pos[0]+flag1+3][pos[1]+flag1+3],-1)
			else:
				tu = (-1,tmpboard[pos[0]+flag1][pos[1]+flag1],tmpboard[pos[0]+flag1+1][pos[1]+flag1+1],tmpboard[pos[0]+flag1+2][pos[1]+flag1+2],tmpboard[pos[0]+flag1+3][pos[1]+flag1+3],tmpboard[pos[0]+flag1+4][pos[1]+flag1+4])
		if flag2 != 5 and flag2 - flag1 != 3:
			tu = (tmpboard[pos[0]+flag2-4][pos[1]+flag2-4],tmpboard[pos[0]+flag2-3][pos[1]+flag2-3],tmpboard[pos[0]+flag2-2][pos[1]+flag2-2],tmpboard[pos[0]+flag2-1][pos[1]+flag2-1],tmpboard[pos[0]+flag2][pos[1]+flag2],-1)
			score += weight[template[tu]]
		for i in range(flag1,flag2-4):
			tu = (tmpboard[pos[0]+i][pos[1]+i],tmpboard[pos[0]+i+1][pos[1]+i+1],tmpboard[pos[0]+i+2][pos[1]+i+2],tmpboard[pos[0]+i+3][pos[1]+i+3],tmpboard[pos[0]+i+4][pos[1]+i+4],tmpboard[pos[0]+i+5][pos[1]+i+5])
			score += weight[template[tu]]

	# 右上到左下
	flag1 = -9999 # 判断边界的flag
	flag2 = -9999
	for i in range(-5,6):
		if isValid(pos[0]+i,pos[1]-i) and flag1 == -9999:
			flag1 = i
	for i in range(5,-6,-1):
		if isValid(pos[0]+i,pos[1]-i) and flag2 == -9999:
			flag2 = i
	if flag2 - flag1 >= 3:
		if flag1 != -5:
			if flag2-flag1==3:
				tu = (-1,tmpboard[pos[0]+flag1][pos[1]-flag1],tmpboard[pos[0]+flag1+1][pos[1]-flag1-1],tmpboard[pos[0]+flag1+2][pos[1]-flag1-2],tmpboard[pos[0]+flag1+3][pos[1]-flag1-3],-1)
			else:
				tu = (-1,tmpboard[pos[0]+flag1][pos[1]-flag1],tmpboard[pos[0]+flag1+1][pos[1]-flag1-1],tmpboard[pos[0]+flag1+2][pos[1]-flag1-2],tmpboard[pos[0]+flag1+3][pos[1]-flag1-3],tmpboard[pos[0]+flag1+4][pos[1]-flag1-4])
			score += weight[template[tu]]
		if flag2 != -5 and flag2 - flag1 != 3:
			tu = (tmpboard[pos[0]+flag2-4][pos[1]-flag2+4],tmpboard[pos[0]+flag2-3][pos[1]-flag2+3],tmpboard[pos[0]+flag2-2][pos[1]-flag2+2],tmpboard[pos[0]+flag2-1][pos[1]-flag2+1],tmpboard[pos[0]+flag2][pos[1]-flag2],-1)
			score += weight[template[tu]]
		for i in range(flag1,flag2-4):
			tu = (tmpboard[pos[0]+i][pos[1]-i],tmpboard[pos[0]+i+1][pos[1]-i-1],tmpboard[pos[0]+i+2][pos[1]-i-2],tmpboard[pos[0]+i+3][pos[1]-i-3],tmpboard[pos[0]+i+4][pos[1]-i-4],tmpboard[pos[0]+i+5][pos[1]-i-5])
			score += weight[template[tu]]
	tmpboard[pos[0]][pos[1]] = before
	
	return score 

def seekpoint(tmpboard,isSurface=False):
	mark = [[False for i in range(pp.width)] for j in range(pp.height)]
	tmpevaluate = evaluate(tmpboard)
	tmpevaluate.eval()
	extend = 3 # 每个非空点附近8个方向延伸extend个深度，若不越界则标记为可走，注意这个时候标记可走的点包含了已经下的点，所以再下面要进行剔除
	for x in range(pp.height):
		for y in range(pp.width):
			if tmpboard[x][y] != 0:
				for k in range(-extend,extend+1):
					if x+k >= 0 and x+k < pp.width:
						mark[x+k][y] = True
						if y+k >= 0 and y+k < pp.height:
							mark[x+k][y+k] = True
						if y-k >= 0 and y-k < pp.height:
							mark[x+k][y-k] = True
					if y+k >= 0 and y+k < pp.height:
						mark[x][y+k] = True
	
	for x in range(pp.height):
		for y in range(pp.width):
			if tmpboard[x][y] == 0 and mark[x][y] == True:
				mark[x][y] = scorepoint(tmpboard,(x,y),1) - scorepoint(tmpboard,(x,y),0)
				# tmpboard[x][y] = 1
				# tmpevaluate = evaluate(tmpboard)
				# tmpevaluate.eval()
				# mark[x][y] = tmpevaluate.score
				# tmpboard[x][y] = 0
			else:
				mark[x][y] = float("-Inf")
	
	# random = 10
	upper = 10 if isSurface else 8 # 设置我们的分支因子，注意太小可能会剪掉有利分支
	# pool = []
	points = []
	for _ in range(upper):
		maxval = float("-Inf")
		for x in range(pp.width):
			for y in range(pp.height):
				if mark[x][y] > maxval:
					pos = (x,y)
					maxval = mark[x][y] 
		points.append((pos,maxval + tmpevaluate.score))
		mark[pos[0]][pos[1]] = float("-Inf")
	# points = pool[0:4]
	
	
	return points

def seek_kill(tmpboard,val):
	mark = [[False for i in range(pp.width)] for j in range(pp.height)]

	extend = 3 # 每个非空点附近8个方向延伸extend个深度，若不越界则标记为可走，注意这个时候标记可走的点包含了已经下的点，所以再下面要进行剔除
	for x in range(pp.height):
		for y in range(pp.width):
			if tmpboard[x][y] != 0:
				for k in range(-extend,extend+1):
					if x+k >= 0 and x+k < pp.width:
						mark[x+k][y] = True
						if y+k >= 0 and y+k < pp.height:
							mark[x+k][y+k] = True
						if y-k >= 0 and y-k < pp.height:
							mark[x+k][y-k] = True
					if y+k >= 0 and y+k < pp.height:
						mark[x][y+k] = True
	
	points = []
	for x in range(pp.height):
		for y in range(pp.width):
			if tmpboard[x][y] == 0 and mark[x][y] == True:
				mark[x][y] = scorepoint(tmpboard,(x,y),1) - scorepoint(tmpboard,(x,y),0)
				if (mark[x][y] >= val):
					points.append(((x,y),mark[x][y]))
	
	return points

def analyze_kill(tmpboard,depth,maxdepth):
	nowtime=win32api.GetTickCount()
	if nowtime-pp.start_time>pp.info_timeout_turn/3:
		return False
	if pp.info_time_left<15000 and nowtime-pp.start_time>pp.info_timeout_turn/4:
		return False
	tmpevaluate = evaluate(tmpboard)
	tmpevaluate.eval()
	weight = [0,1000000,-1000000,50000,-100000,400,-100000,400,-8000,20,-50,20,-50,1,-3,1,-3]
	if depth%2 == maxdepth%2: # 我方回合，应该是max节点
		boardcopy = copy.deepcopy(tmpboard)

		if tmpevaluate.gameresult == 1:
			return True
		if tmpevaluate.gameresult == -1 or depth < 0:
			return False

		points = seek_kill(tmpboard,5000)
		if len(points) == 0:
			return False

		for k in range(len(points)):
			x = points[k][0][0]
			y = points[k][0][1] #得到此时的落子位置
			boardcopy[x][y] = 1
			succval = analyze_kill(boardcopy,depth-1,maxdepth)
			boardcopy[x][y] = 0
			if succval:
				return (x,y)
		return False

	if depth%2 != maxdepth%2: # 敌方回合，应该是min节点
		boardcopy = copy.deepcopy(tmpboard)
		
		if tmpevaluate.gameresult == 1:
			return True
		if tmpevaluate.gameresult == -1 or depth < 0:
			return False

		for x in range(pp.width):
			for y in range(pp.height):
				if boardcopy[x][y] == 1:
					boardcopy[x][y] = 2
				elif boardcopy[x][y] == 2:
					boardcopy[x][y] = 1
		points = seek_kill(boardcopy,5000) # 我们通过对棋盘进行翻转转换成相同的操作，因为seekPoint是求我方的最佳位置

		if len(points) == 0:
			points = seekpoint(boardcopy)
			points = points[0:4]
		
		boardcopy = copy.deepcopy(tmpboard)
		for k in range(len(points)):
			x = points[k][0][0]
			y = points[k][0][1] #得到此时的落子位置
			boardcopy[x][y] = 2
			succval = analyze_kill(boardcopy,depth-1,maxdepth)
			boardcopy[x][y] = 0
			if not succval:
				return False
		return True


# def Iterative_deepening(root):
# 	bestpoint=(-1,-1)
# 	alpha=float('-Inf')
# 	beta=float('Inf')
# 	for depth in range(2,5,2):
# 		bestpoint,val = analyze(root,depth,alpha,beta,depth)
# 		nowtime=win32api.GetTickCount()
# 		if nowtime-pp.start_time>10*pp.info_timeout_turn/15:
# 			break
# 		if val<=alpha or val >= beta:
# 			alpha=float('-Inf')
# 			beta=float('Inf')
# 			if depth==5:
# 				break
# 			continue
# 		alpha=val-50
# 		beta=val+50
# 	return (bestpoint,val)

# hashfEXACT = 0
# hashfALPHA = 1
# hashfBETA  = 2

# def analyze(tmpboard,depth,alpha,beta,maxdepth): # PVS
# 	tmpevaluate = evaluate(tmpboard)
# 	tmpevaluate.eval()
# 	tupleboard = list()
# 	for i in range(pp.height):
# 		tupleboard.append(tuple(tmpboard[i]))
# 	tupleboard = tuple(tupleboard)

# 	bestpoint=(-1,-1)
# 	role = 0
# 	if depth%2 == maxdepth%2: # 我方回合，应该是max节点
# 		for k in range(maxdepth,depth-1,-1):
# 			if (tupleboard,k,hashfEXACT) in chess.keys():
# 				return chess[(tupleboard,k,hashfEXACT)]
# 			if (tupleboard,k,hashfALPHA) in chess.keys():
# 				alpha = max(alpha,chess[(tupleboard,k,hashfALPHA)][1])
# 			if alpha >= beta:
# 				return (chess[(tupleboard,k,hashfALPHA)][0],alpha)
# 		role = 1
# 		foundPV= False
# 		hashf = hashfALPHA
# 		boardcopy = copy.deepcopy(tmpboard)

# 		if tmpevaluate.gameresult != 0:
# 			return ((-1,-1),tmpevaluate.score) #返回我方赢或者敌方赢的分数
		
# 		# 杀棋
# 		# if depth==maxdepth:
# 		# 	snapback = analyze_kill(boardcopy,15,15)
# 		# 	if snapback:
# 		# 		return (snapback,float("Inf"))

# 		points = seekpoint(boardcopy)

# 		if depth == 0:
# 			chess[(tupleboard,depth,hashfEXACT)] = points[0]
# 			return points[0] # 返回最佳位置对应的分数
# 	if depth%2 != maxdepth%2: # 敌方回合，应该是min节点
# 		for k in range(maxdepth,depth-1,-1):
# 			if (tupleboard,k,hashfEXACT) in chess.keys():
# 				return chess[(tupleboard,k,hashfEXACT)]
# 			if (tupleboard,k,hashfBETA) in chess.keys():
# 				beta = min(beta,chess[(tupleboard,k,hashfBETA)][1])
# 			if alpha >= beta:
# 				return (chess[(tupleboard,k,hashfBETA)][0],beta)
# 		role = 2
# 		hashf = hashfBETA

# 		boardcopy = copy.deepcopy(tmpboard)

# 		if tmpevaluate.gameresult != 0:
# 			return ((-1,-1),tmpevaluate.score) #返回我方赢或者敌方赢的分数

# 		for x in range(pp.width):
# 			for y in range(pp.height):
# 				if boardcopy[x][y] == 1:
# 					boardcopy[x][y] = 2
# 				elif boardcopy[x][y] == 2:
# 					boardcopy[x][y] = 1
		
# 		# 杀棋
# 		# if depth==maxdepth:
# 		# 	snapback = analyze_kill(boardcopy,15,15)
# 		# 	if snapback:
# 		# 		return (snapback,float("Inf"))

# 		points = seekpoint(boardcopy) # 我们通过对棋盘进行翻转转换成相同的操作，因为seekPoint是求我方的最佳位置

# 		if depth == 0:
# 			chess[(tupleboard,depth,hashfEXACT)] = points[0]
# 			return (points[0][0],-points[0][1]) # 返回最佳位置对应的分数
# 		boardcopy = copy.deepcopy(tmpboard)	

# 	for k in range(len(points)):
# 		x = points[k][0][0]
# 		y = points[k][0][1] #得到此时的落子位置
# 		boardcopy[x][y] = role
# 		if k==0:
# 			score = -analyze(boardcopy,depth-1,-beta,-alpha,maxdepth)[1]
# 		else:
# 			score  = -analyze(boardcopy,depth-1,-alpha-1,-alpha,maxdepth)[1]
# 			if score > alpha and score < beta:
# 				score  = -analyze(boardcopy,depth-1,-beta,-alpha,maxdepth)[1]
# 		boardcopy[x][y] = 0
# 		if score > alpha:
# 			alpha = score
# 			bestpoint=(x,y)
# 		if alpha > beta:
# 			chess[(tupleboard,depth,hashfBETA)] = (bestpoint,beta)
# 			break
# 	chess[(tupleboard,depth,hashf)] = (bestpoint,alpha)
# 	return (bestpoint,alpha)

def analyze(tmpboard,depth,alpha,beta,maxdepth):
	tmpevaluate = evaluate(tmpboard)
	tmpevaluate.eval()
	tupleboard = list()
	# for i in range(pp.height):
	# 	tupleboard.append(tuple(tmpboard[i]))
	# tupleboard = tuple(tupleboard)

	bestpoint=(-1,-1)
	if depth%2 == maxdepth%2: # 我方回合，应该是max节点

		# for k in range(maxdepth,depth-1,-1):
		# 	if (tupleboard,k,hashfEXACT) in chess.keys():
		# 		return chess[(tupleboard,k,hashfEXACT)]
		# 	if (tupleboard,k,hashfALPHA) in chess.keys():
		# 		alpha = max(alpha,chess[(tupleboard,k,hashfALPHA)][1])
		# 	if alpha >= beta:
		# 		return (chess[(tupleboard,k,hashfALPHA)][0],alpha)


		# hashf = hashfALPHA
		boardcopy = copy.deepcopy(tmpboard)

		if tmpevaluate.gameresult != 0:
			return ((-1,-1),tmpevaluate.score) #返回我方赢或者敌方赢的分数
		
		# 杀棋
		if depth==maxdepth:
			snapback = analyze_kill(boardcopy,15,15)
			if snapback:
				return (snapback,float("Inf"))

		points = seekpoint(boardcopy)

		if depth == 0:
			# chess[(tupleboard,depth,hashfEXACT)] = points[0]
			return points[0] # 返回最佳位置对应的分数

		for k in range(len(points)):
			x = points[k][0][0]
			y = points[k][0][1] #得到此时的落子位置
			boardcopy[x][y] = 1
			succval = analyze(boardcopy,depth-1,alpha,beta,maxdepth)
			boardcopy[x][y] = 0
			if succval[1] > alpha:
				# hashf = hashfEXACT
				alpha = succval[1]
				bestpoint = (x,y)
			if beta <= alpha:
				# chess[(tupleboard,depth,hashfBETA)] = (bestpoint,beta)
				break
		# chess[(tupleboard,depth,hashf)] = (bestpoint,alpha)
		return (bestpoint,alpha)
	
	if depth%2 != maxdepth%2: # 敌方回合，应该是min节点
		# hashf = hashfBETA

		# for k in range(maxdepth,depth-1,-1):
		# 	if (tupleboard,k,hashfEXACT) in chess.keys():
		# 		return chess[(tupleboard,k,hashfEXACT)]
		# 	if (tupleboard,k,hashfBETA) in chess.keys():
		# 		beta = min(beta,chess[(tupleboard,k,hashfBETA)][1])
		# 	if alpha >= beta:
		# 		return (chess[(tupleboard,k,hashfBETA)][0],beta)

		boardcopy = copy.deepcopy(tmpboard)

		if tmpevaluate.gameresult != 0:
			return ((-1,-1),tmpevaluate.score) #返回我方赢或者敌方赢的分数

		for x in range(pp.width):
			for y in range(pp.height):
				if boardcopy[x][y] == 1:
					boardcopy[x][y] = 2
				elif boardcopy[x][y] == 2:
					boardcopy[x][y] = 1
		
		# 杀棋
		if depth==maxdepth:
			snapback = analyze_kill(boardcopy,15,15)
			if snapback:
				return (snapback,float("Inf"))

		points = seekpoint(boardcopy) # 我们通过对棋盘进行翻转转换成相同的操作，因为seekPoint是求我方的最佳位置

		if depth == 0:
			# chess[(tupleboard,depth,hashfEXACT)] = points[0]
			return (points[0][0],-points[0][1]) # 返回最佳位置对应的分数
		
		boardcopy = copy.deepcopy(tmpboard)
		for k in range(len(points)):
			x = points[k][0][0]
			y = points[k][0][1] #得到此时的落子位置
			boardcopy[x][y] = 2
			succval = analyze(boardcopy,depth-1,alpha,beta,maxdepth)
			boardcopy[x][y] = 0
			if succval[1] < beta:
				# hashf = hashfEXACT
				beta = succval[1]
				bestpoint = (x,y)
			if beta <= alpha:
				# chess[(tupleboard,depth,hashfALPHA)] = (bestpoint, alpha)
				break
		# chess[(tupleboard,depth,hashf)] = (bestpoint,beta)
		return (bestpoint,beta)

def seek_must(tmpboard): # 必走棋
	mark = [[False for i in range(pp.width)] for j in range(pp.height)]
	tmpevaluate = evaluate(tmpboard)
	tmpevaluate.eval()
	extend = 1 
	for x in range(pp.height):
		for y in range(pp.width):
			if tmpboard[x][y] != 0:
				for k in range(-extend,extend+1):
					if x+k >= 0 and x+k < pp.width:
						mark[x+k][y] = True
						if y+k >= 0 and y+k < pp.height:
							mark[x+k][y+k] = True
						if y-k >= 0 and y-k < pp.height:
							mark[x+k][y-k] = True
					if y+k >= 0 and y+k < pp.height:
						mark[x][y+k] = True
	
	for x in range(pp.height):
		for y in range(pp.width):
			if tmpboard[x][y] == 0 and mark[x][y] == True:
				mark[x][y] = scorepoint(tmpboard,(x,y),1) - scorepoint(tmpboard,(x,y),0)
				# tmpboard[x][y] = 1
				# myevaluate = evaluate(tmpboard)
				# myevaluate.eval()
				# tmpboard[x][y] = 0
				# tmp


			else:
				mark[x][y] = float("-Inf")
	
	upper = 1 # 设置我们的分支因子，注意太小可能会剪掉有利分支
	points = []
	for _ in range(upper):
		maxval = float("-Inf")
		for x in range(pp.width):
			for y in range(pp.height):
				if mark[x][y] > maxval:
					pos = (x,y)
					maxval = mark[x][y] 
		points.append((pos,maxval))
		mark[pos[0]][pos[1]] = float("-Inf")
	
	return points






def analyze_must(tmpboard):
	tmpevaluate = evaluate(tmpboard)
	tmpevaluate.eval()
	bestpoint=(-1,-1)


	points = seek_must(tmpboard)
	if  points[0][1]>90000:
		bestpoint=points[0][0]

	return (bestpoint,float('Inf'))

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
				# (pos,_) = Iterative_deepening([[board[x][y] for y in range(pp.height)] for x in range(pp.width)]) # For ID & PVS
				(pos,_) = analyze([[board[x][y] for y in range(pp.height)] for x in range(pp.width)],4
				,float("-Inf"),float("Inf"),4)
			x = pos[0]
			y = pos[1]
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
