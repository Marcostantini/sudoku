import numpy as np
import subprocess
import json
from sudoku import *
from scipy import signal

class Sudoku:
    def __init__(self, line, n=9):
        """ line contains a Sudoku in a single line """
        self.line = line
        self.n = n

        # Build a numpy matrix as a representation for the Sudoku
        # while also counting the number of givens
        matrix = np.zeros((n, n))   
        i = 0
        j = 0
        self.givens = 0
        for number in line:
            if number != "0":
                matrix[i, j] = number
                self.givens += 1
            j += 1
            if j % n == 0:
                j = 0
                i += 1
        self.matrix = matrix

        # A 3 dimensional array acts as a map from a variable (r, c, v)
        # to a variable number from 1 to m**3
        var_map = []
        i = 0
        for r in range(n):
            row = []
            for c in range(n):
                cells = []
                for v in range(n):
                    i += 1
                    cells.append(str(i))
                row.append(cells)
            var_map.append(row)
        self.var_map = var_map

        # Number of encoding variables
        self.n_enc_vars = n**3
        # Number of definedness clauses
        self.n_def_clauses = n**2
        # Number of uniqueness clauses
        self.n_uni_clauses = int(n**3 * (n - 1)/2)

    def autocorrelation_sum(self):
        convolution = signal.convolve2d(self.matrix, self.matrix)
        return convolution.sum()

    # The following methods encode the Sudoku rules
    # using propositional formulas
    # See - Kwon, Jain, "Optimized CNF Encoding for Sudoku Puzzles"
    def cell_definedness_enc(self):
        formula = ""

        for r in range(self.n):
            for c in range(self.n):
                for v in range(self.n):
                    formula += self.var_map[r][c][v] + " "
                formula += "0\n"

        return formula

    def cell_uniqueness_enc(self):
        formula = ""

        for r in range(self.n):
            for c in range(self.n):
                for vi in range(self.n - 1):
                    for vj in range(vi + 1, self.n):
                        formula += "-" + self.var_map[r][c][vi] + " -" + self.var_map[r][c][vj] + " 0\n"

        return formula

    def row_definedness_enc(self):
        formula = ""

        for r in range(self.n):
            for v in range(self.n):
                for c in range(self.n):
                    formula += self.var_map[r][c][v] + " "
                formula += "0\n"

        return formula

    def row_uniqueness_enc(self):
        formula = ""

        for r in range(self.n):
            for v in range(self.n):
                for ci in range(self.n - 1):
                    for cj in range(ci + 1, self.n):
                        formula += "-" + self.var_map[r][ci][v] + " -" + self.var_map[r][cj][v] + " 0\n"

        return formula

    def column_definedness_enc(self):
        formula = ""

        for c in range(self.n):
            for v in range(self.n):
                for r in range(self.n):
                    formula += self.var_map[r][c][v] + " "
                formula += "0\n"

        return formula

    def column_uniqueness_enc(self):
        formula = ""

        for c in range(self.n):
            for v in range(self.n):
                for ri in range(self.n - 1):
                    for rj in range(ri + 1, self.n):
                        formula += "-" + self.var_map[ri][c][v] + " -" + self.var_map[rj][c][v] + " 0\n"

        return formula

    def block_definedness_enc(self):
        formula = ""
        off_lim = int(np.sqrt(self.n))

        for roffs in range(off_lim):
            for coffs in range(off_lim):
                for v in range(self.n):
                    for r in range(off_lim):
                        for c in range(off_lim):
                            formula += self.var_map[roffs * off_lim + r][coffs * off_lim + c][v] + " "
                    formula += "0\n"

        return formula

    def block_uniqueness_enc(self):
        formula = ""
        off_lim = int(np.sqrt(self.n))

        for roffs in range(off_lim):
            for coffs in range(off_lim):
                for v in range(self.n):
                    for ci in range(self.n - 1):
                        for cj in range(ci + 1, self.n):
                            formula += ("-" +
                                self.var_map[roffs * off_lim + ci//off_lim][coffs * off_lim + ci%off_lim][v] + " -" +
                                self.var_map[roffs * off_lim + cj//off_lim][coffs * off_lim + cj%off_lim][v] + " 0\n")

        return formula

    def assigned_enc(self):
        formula = ""

        # Scan the matrix for givens
        # Take into account indices are 0 based while
        # Sudoku givens start at 1
        for r in range(self.n):
            for c in range(self.n):
                sud_num = int(self.matrix[r, c])
                if sud_num > 0:
                    formula += self.var_map[r][c][sud_num - 1] + " 0\n"

        return formula

    def minimal_encoding(self):
        header = "c A Sudoku in minimal encoding\n"

        # Calculate total number of clauses
        n_clauses = self.n_def_clauses + 3*self.n_uni_clauses + self.givens

        header += "p cnf " + str(self.n_enc_vars) + " " + str(n_clauses) + "\n"

        return (header +
            self.cell_definedness_enc() +
            self.row_uniqueness_enc() +
            self.column_uniqueness_enc() +
            self.block_uniqueness_enc() +
            self.assigned_enc())

    def efficient_encoding(self):
        header = "c A Sudoku in efficient encoding\n"

        # Calculate total number of clauses
        n_clauses = self.n_def_clauses + 4*self.n_uni_clauses + self.givens

        header += "p cnf " + str(self.n_enc_vars) + " " + str(n_clauses) + "\n"

        return (header +
            self.cell_definedness_enc() +
            self.cell_uniqueness_enc() +
            self.row_uniqueness_enc() +
            self.column_uniqueness_enc() +
            self.block_uniqueness_enc() +
            self.assigned_enc())

    def extended_encoding(self):
        header = "c A Sudoku in extended encoding\n"

        # Calculate total number of clauses
        n_clauses = 4*self.n_def_clauses + 4*self.n_uni_clauses + self.givens

        header += "p cnf " + str(self.n_enc_vars) + " " + str(n_clauses) + "\n"

        return (header +
            self.cell_definedness_enc() +
            self.cell_uniqueness_enc() +
            self.row_definedness_enc() +
            self.row_uniqueness_enc() +
            self.column_definedness_enc() +
            self.column_uniqueness_enc() + 
            self.block_definedness_enc() +
            self.block_uniqueness_enc() + 
            self.assigned_enc())

def dump_global_densities():
    sudokus = json.load(open('49k17.json','r'))
    n_sudokus = len(sudokus)
    global_densities = []
    for i in range(n_sudokus):
        global_densities.append(globalDensity(sudokus[i]))
    json.dump(global_densities, open('global_densities.json', 'w'))

def dump_num_densities():
    sudokus = json.load(open('49k17.json','r'))
    n_sudokus = len(sudokus)
    num_densities = []
    for i in range(n_sudokus):
        num_densities.append(numDensity(sudokus[i]))
    json.dump(num_densities, open('num_densities.json', 'w'))

def dump_global_symmetries():
    sudokus = json.load(open('49k17.json','r'))
    n_sudokus = len(sudokus)
    global_symmetries = []
    for i in range(n_sudokus):
        global_symmetries.append(globalSymmetry(sudokus[i]))
    json.dump(global_symmetries, open('global_symmetries.json', 'w'))

def find_sub_list(sl,l):
    sll=len(sl)
    for ind in (i for i,e in enumerate(l) if e==sl[0]):
        if l[ind:ind+sll]==sl:
            return ind+sll

def dump_zchaff_stats():
    file = open("raw_17_clue_sudokus.txt")
    lines = [line[:-1] for line in file]
    file.close()
    max_decision_levels = []
    n_decisions = []
    conflict_literals = []
    for line in lines:
        my_sud = Sudoku(line)
        output = open("encoding.cnf", "w")
        output.write(my_sud.minimal_encoding())
        output.close()
        statistics = subprocess.check_output("zchaff encoding.cnf", shell=True, universal_newlines=True)
        stats = statistics.split()
        max_decision_levels.append(int(stats[find_sub_list(["Decision", "Level"], stats)])) 
        n_decisions.append(int(stats[find_sub_list(["of", "Decisions"], stats)]))
        conflict_literals.append(int(stats[find_sub_list(["Conflict", "Literals"], stats)]))  
    json.dump(max_decision_levels, open('zchaff_max_decision_levels.json', 'w'))
    json.dump(n_decisions, open('zchaff_n_decisions.json', 'w'))
    json.dump(conflict_literals, open('zchaff_conflict_literals.json', 'w'))

def plot_statistics(file):
    n_sudokus = 500

    global_densities = json.load(open('global_densities.json','r'))
    # global_densities = np.array(global_densities)
    # indexes = global_densities.argsort()

    # num_densities = json.load(open('num_densities.json','r'))
    # num_densities = np.array(num_densities)
    # indexes = num_densities.argsort()

    # global_symmetries = json.load(open('global_symmetries.json','r'))
    # global_symmetries = np.array(global_symmetries)
    # indexes = global_symmetries.argsort()

    # max_decision_levels = json.load(open('zchaff_max_decision_levels.json','r'))
    # n_decisions = json.load(open('zchaff_n_decisions.json','r'))
    conflict_literals = json.load(open('zchaff_conflict_literals.json','r'))


    plt.plot(global_densities, conflict_literals, 'ro')
    plt.show()

if __name__ == '__main__':

    # dump_global_densities()
    # dump_global_symmetries()
    # dump_num_densities()
    dump_zchaff_stats()
	
# BIN
    # max_decision_levels.append(int(stats[753])) 
    # n_decisions.append(int(stats[757]))
    # conflict_literals.append(int(stats[801]))  
        
    # # Read a line and create a Sudoku object
    # file = open("raw_17_clue_sudokus.txt")
    # my_sud = Sudoku(file.readline()[:-1])
    # file.close()
    
    # # Export the minimal encoding to be solved with zChaff
    # output = open("encoding.cnf", "w")
    # output.write(my_sud.minimal_encoding())
    # output.close()

    # statistics = subprocess.check_output("zchaff encoding.cnf", shell=True, universal_newlines=True)

    # print statistics.split()[753]
