import math
import json
import matplotlib.pyplot as plt
import numpy as np

SIZE = 9

def gen49k17Sudokus(data):
	sudokus = []
	row_len = SIZE
	for line in data:
		sudokus.append([line[i:i+row_len] for i in range(0, len(line), row_len)])
	for i,sudoku in enumerate(sudokus):
		for j,row in enumerate(sudoku):
			sudokus[i][j] = [int(k) for k in row]
	json.dump(sudokus, open('49k17.json', 'w'))

def getGivens(sudoku):
	givens = 0
	for row in sudoku:
		givens += rowGivens(row)
	return givens

def rowGivens(row):
	givens = 0
	for num in row:
		if num != 0:
			givens += 1
	return givens

def numGivens(sudoku, num):
	givens = 0
	for row in range(SIZE):
		for col in range(SIZE):
			if sudoku[row][col] == num:
				givens += 1
	return givens

def rowDensity(sudoku):
	average = getGivens(sudoku) / float(SIZE)
	density = math.sqrt(sum([pow(rowGivens(row)-average, 2) for row in sudoku]))
	return density / maxDensity(sudoku)

def colDensity(sudoku):
	average = getGivens(sudoku) / float(SIZE)
	trans_sudoku = np.asarray(sudoku).T.tolist()
	density = math.sqrt(sum([pow(rowGivens(col)-average, 2) for col in sudoku]))
	return density / maxDensity(sudoku)

def numDensity(sudoku):
	average = getGivens(sudoku) / float(SIZE)
	density = math.sqrt(sum([pow(numGivens(sudoku, num)-average, 2) for num in range(1, SIZE+1)]))
	return density / maxDensity(sudoku)

def blockDensity(sudoku):
	givens = getGivens(sudoku)
	average = givens / float(SIZE)
	sunp = np.array(sudoku)
	blocks_givens = []
	for i in [0,3,6]:
		for j in [0,3,6]:
			blocks_givens.append(getGivens(sunp[i:i+3, j:j+3]))
	density = math.sqrt(sum([pow(block_givens-average, 2) for block_givens in blocks_givens]))
	return density / maxDensity(sudoku)

def globalDensity(sudoku):
	density = (rowDensity(sudoku) + colDensity(sudoku) + blockDensity(sudoku)) / float(3)
	return density

def maxDensity(sudoku):
	givens = getGivens(sudoku)
	average = givens / float(SIZE)
	# In the square root it sums (1) the rows completely filled with givens, (2) a row partially filled, (3) the empty rows
	density = math.sqrt(pow(SIZE-average, 2) * (givens / SIZE) + pow(givens % SIZE - average, 2) + pow(average, 2) * (SIZE - math.ceil(givens / float(SIZE))))
	return float(density)

def diag1Symmetry(sudoku):
	givens = float(getGivens(sudoku))
	sunp = np.array(sudoku)
	sunpt = sunp.T
	symmetric_givens = 0
	for row in range(SIZE):
		for col in range(SIZE):
			if sunp[row][col] != 0 and sunpt[row][col] != 0:
				symmetric_givens += 1
	symmetry = symmetric_givens / givens
	return symmetry

def diag2Symmetry(sudoku):
	givens = float(getGivens(sudoku))
	sunp = np.array(sudoku)
	sunpt = np.fliplr(np.flipud(sunp)).T
	symmetric_givens = 0
	for row in range(SIZE):
		for col in range(SIZE):
			if sunp[row][col] != 0 and sunpt[row][col] != 0:
				symmetric_givens += 1
	symmetry = symmetric_givens / givens
	return symmetry

def LRSymmetry(sudoku):
	givens = float(getGivens(sudoku))
	sunp = np.array(sudoku)
	sunpt = np.fliplr(sunp)
	symmetric_givens = 0
	for row in range(SIZE):
		for col in range(SIZE):
			if sunp[row][col] != 0 and sunpt[row][col] != 0:
				symmetric_givens += 1
	symmetry = symmetric_givens / givens
	return symmetry

def UDSymmetry(sudoku):
	givens = float(getGivens(sudoku))
	sunp = np.array(sudoku)
	sunpt = np.flipud(sunp)
	symmetric_givens = 0
	for row in range(SIZE):
		for col in range(SIZE):
			if sunp[row][col] != 0 and sunpt[row][col] != 0:
				symmetric_givens += 1
	symmetry = symmetric_givens / givens
	return symmetry

def globalSymmetry(sudoku):
	return max([diag1Symmetry(sudoku),diag2Symmetry(sudoku),LRSymmetry(sudoku),UDSymmetry(sudoku)])

if __name__ == "__main__":

	# 49000 17 GIVENS SUDOKUS GENERATOR
	# filepath = 'raw_17_clue_sudokus.txt'
	# with open(filepath, 'r') as txtfile:
	# 	data = [line for line in txtfile.read().split('\n')][:-1]
	# gen49k17Sudokus(data)

	sudokus = json.load(open('49k17.json','r'))

	# calculates the density of the sudokus wrt rows
	# row_densities = []
	# for i in range(len(sudokus)):
	# 	row_densities.append(rowDensity(sudokus[i]))
	# plt.hist(row_densities)

	# calculates the density of the sudokus wrt columns
	# col_densities = []
	# for i in range(len(sudokus)):
	# 	col_densities.append(colDensity(sudokus[i]))
	# plt.hist(col_densities)

	# calculates the density of the sudokus wrt numbers
	# num_densities = []
	# for i in range(len(sudokus)):
	# 	num_densities.append(numDensity(sudokus[i]))
	# plt.hist(num_densities)

	# calculates the density of the sudokus wrt blocks
	# block_densities = []
	# for i in range(len(sudokus)):
	# 	block_densities.append(blockDensity(sudokus[i]))
	# plt.hist(block_densities)

	# calculates the density of the sudokus wrt rows, columns and blocks
	# global_densities = []
	# for i in range(len(sudokus)):
	# 	global_densities.append(globalDensity(sudokus[i]))
	# max_index = global_densities.index(max(global_densities))
	# min_index = global_densities.index(min(global_densities))
	# print np.array(sudokus[min_index])
	# print max(global_densities)
	# print min(global_densities)
	# plt.hist(global_densities)

	# calculates the symmetry of the sudokus
	global_symmetries = []
	for i in range(len(sudokus)):
		global_symmetries.append(globalSymmetry(sudokus[i]))
	max_index = global_symmetries.index(max(global_symmetries))
	min_index = global_symmetries.index(min(global_symmetries))
	print np.array(sudokus[max_index])
	print max(global_symmetries)
	print min(global_symmetries)
	plt.hist(global_symmetries)

	plt.show()