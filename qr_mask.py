matrix = [[0,1,1,1,1,1],
		  [0,1,0,1,1,1],
		  [0,1,0,1,1,1],
		  [0,0,0,0,0,0],
		  [0,1,0,1,1,1],
		  [1,1,1,1,1,1]]

n1 = {}

def n1_row_count(modules: int, matrix: list, n1: dict, count: int = 1, previus: str = "nan"):
	
	for i in range(modules):
		for j in range(modules):
			if previus == "nan":
				previus = matrix[i][j]
				#print(cond, matrix[i][j], previus, count)
				continue
			elif matrix[i][j] == previus:
				count += 1
				previus = matrix[i][j]
			else:
				count = 1
				previus = matrix[i][j]
				
			#print(cond, matrix[i][j], previus, count)
			
			if count >= 5:
				
				try:
					n1[count]
				except KeyError:
					n1[count] = 0
					
				if j == modules - 1:
					n1[count] += 1
				elif matrix[i][j+1] != matrix[i][j]:
					n1[count] += 1
					
		count = 1
		previus = "nan"
		cond = "First"
		
def n1_col_count(modules: int, matrix: list, n1: dict, count: int = 1, previus: str = "nan"):

	for i in range(modules):
		for j in range(modules):
			if previus == "nan":
				previus = matrix[j][i]
				#print(cond, matrix[j][i], previus, count)
				continue
			elif matrix[j][i] == previus:
				count += 1
			else:
				count = 1
				previus = matrix[j][i]
				
			#print(cond, matrix[j][i], previus, count)
			
			if count >= 5:
				
				try:
					n1[count]
				except KeyError:
					n1[count] = 0
					
				if j == modules - 1:
					n1[count] += 1
				elif matrix[j+1][i] != matrix[j][i]:
					n1[count] += 1
					
		count = 1
		previus = "nan"
		cond = "First"
		
def n1_penalty_count(modules: int, matrix: list) -> int:
	
	n1 = {}
	
	n1_row_count(modules, matrix, n1)
	n1_col_count(modules, matrix, n1)
	
	penalty = 0
	for key, val in n1.items():
		penalty += val*(3+(key-5))
	
	return penalty

print(n1_penalty_count(6, matrix))
