qr_mask_dict = {"000": lambda i,j: (i+j)%2,
				"001": lambda i,j: i%2,
	            "010": lambda i,j: int(not(j%3 == 0)),
		   	    "011": lambda i,j: int(not((i+j)%3 == 0)),
				"100": lambda i,j: ((i//2) + (j//3))%2,
				"101": lambda i,j: int(not((i*j)%2 + (i*j)%3 == 0)),
				"110": lambda i,j: ((i*j)%2 + (i*j)%3)%2,
				"111": lambda i,j: ((i+j)%2 + (i*j)%3)%2}
						
micro_mask_dict = {"00": lambda i,j: i%2,
				   "01": lambda i,j: ((i//2) + (j//3))%2,
				   "10": lambda i,j: ((i*j)%2 + (i*j)%3)%2,
				   "11": lambda i,j: ((i+j)%2 + (i*j)%3)%2}

# FUNCTION FOR PENALTY COUNTING IN QR CODE 
# ISO/IEC 18004:2015(E) to pg. 61 chapter 7.8.3

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
		
def n1_col_count(modules: int, matrix: list, n1: dict, count: int = 1, previus: str = "nan"):

	for i in range(modules):
		for j in range(modules):
			if previus == "nan":
				previus = matrix[j][i]
				#print(matrix[j][i], previus, count)
				continue
			elif matrix[j][i] == previus:
				count += 1
			else:
				count = 1
				previus = matrix[j][i]
				
			#print(matrix[j][i], previus, count)
			
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
		
def n1_penalty_count(modules: int, matrix: list) -> int:
	
	n1 = {}
	
	n1_row_count(modules, matrix, n1)
	n1_col_count(modules, matrix, n1)
	
	penalty = 0
	for key, val in n1.items():
		penalty += val*(3+(key-5))
	#print("N1", n1, penalty)
	return penalty

def n2_penalty_count(modules: int, matrix: list) -> int:

	count = 0
	for i in range(modules-1):
		for j in range(modules-1):
			if matrix[i][j] == matrix[i][j+1] == matrix[i+1][j+1] == matrix[i+1][j] == 1:
				count += 1
			elif matrix[i][j] == matrix[i][j+1] == matrix[i+1][j+1] == matrix[i+1][j] == 0:
				count += 1
	#print("N2", count, count*3)
	return count*3

def n3_penalty_count(modules: int, matrix: list) -> int:
	
	pattern = [0,1,0,0,0,1,0]
	
	pattern_row_pos = []
	pattern_col_pos = []
	
	# Row pattern check
	for i in range(modules):
		for j in range(modules-6):
			check = 0
			for k in range(len(pattern)):
				if pattern[k] == matrix[i][j+k]:
					check += 1
				else:
					break
			if check == 7:
				pattern_row_pos.append((i,j))
	
	count = 0			
	for row, col in pattern_row_pos:
		if col >= 7:
			#print("Sub", row, col, " | ", matrix[row][col-1], matrix[row][col-2], matrix[row][col-3], matrix[row][col-4])
			if matrix[row][col-1] == matrix[row][col-2] == matrix[row][col-3] == matrix[row][col-4] == 1:
				count += 1
		elif col + 6 <= modules - 8:
			#print("Add", row, col+4, " | ", matrix[row][col+4+1], matrix[row][col+4+2], matrix[row][col+4+3], matrix[row][col+4+4])
			if matrix[row][col+4+1] == matrix[row][col+4+2] == matrix[row][col+4+3] == matrix[row][col+4+4] == 1:
				count += 1
	
	# Col pattern check			
	for i in range(modules):
		for j in range(modules-6):
			check = 0
			for k in range(len(pattern)):
				if pattern[k] == matrix[j+k][i]:
					check += 1
				else:
					break
			if check == 7:
				pattern_col_pos.append((j,i))
	
	for row, col in pattern_col_pos:
		if row >= 7:
			#print("Sub", row, col, " | ", matrix[row-1][col], matrix[row-2][col], matrix[row-3][col], matrix[row-4][col])
			if matrix[row-1][col] == matrix[row-2][col] == matrix[row-3][col] == matrix[row-4][col] == 1:
				count += 1
		elif row + 6 <= modules - 8:
			#print("Add", row+4, col, " | ", matrix[row+4+1][col], matrix[row+4+2][col], matrix[row+4+3][col], matrix[row+4+4][col])
			if matrix[row+4+1][col] == matrix[row+4+2][col] == matrix[row+4+3][col] == matrix[row+4+4][col] == 1:
				count += 1
	#print("N3", count, count*40)
	return count*40
	
def n4_penalty_count(modules: int, matrix: list) -> int:
	
	count=0
	penalty=0
	for i in range(modules):
		for j in range(modules):
			if matrix[i][j] == 0:
				count += 1
		
	ratio = count*100/(modules**2)

	for step in range(1,11):
		if ratio >= 50 - 5*step and ratio <= 50 + 5*step:
			penalty = 10*(step-1)
			break
	#print("N4", count, ratio, penalty)	
	return penalty

def qr_micro_penalty_count(modules: int, matrix: list) -> int:
	
	penalty = 0
	sum1 = 0
	sum2 = 0
	
	for i in range(1,modules):
		if matrix[i][modules-1] == 0:
			sum1 += 1
		if matrix[modules-1][i] == 0:
			sum2 += 1
				
	if sum1 > sum2:
		penalty += sum2*16 + sum1
	elif sum1 <= sum2:
		penalty += sum1*16 + sum2
		
	return penalty

def qr_xoring(modules: int, matrix: list, mask_matrix: list, data_mask_dict: dict, mask_mode: str) -> list:
	
	matrix2 = []
	data_mask = []
	for i in range(modules):
		l = []
		l1 = []
		for j in range(modules):
			l1.append(1)
			if mask_matrix[i][j] == 0:
				l.append(1)
			else:
				x = data_mask_dict[mask_mode](i,j)
				l.append(x)
		data_mask.append(l)
		matrix2.append(l)
				
	for i in range(modules):
		for j in range(modules):
			if mask_matrix[i][j] == 0:
				matrix2[i][j] = matrix[i][j]
			else:
				matrix2[i][j] = matrix[i][j]^data_mask[i][j]^1

	return matrix2            
    
def qr_penalty_count(modules: int, matrix: list) -> int:
	
	penalty = 0
	if modules >= 21:
		penalty += n1_penalty_count(modules, matrix)
		penalty += n2_penalty_count(modules, matrix)
		penalty += n3_penalty_count(modules, matrix)
		penalty += n4_penalty_count(modules, matrix)
	elif modules < 21:
		penalty = qr_micro_penalty_count(modules, matrix2)
	
	return penalty
	
def find_best_mask(version: str, modules: int, ec_code: str, matrix: list, mask_matrix: list, add_information) -> str:
	
	penalty_dict = {}
	data_mask_dict = {}
	
	if modules >= 21:
		data_mask_dict = qr_mask_dict
	elif modules < 21:
		data_mask_dict = micro_mask_dict

	for mask_mode in data_mask_dict:
		matrix2 = qr_xoring(modules, matrix, mask_matrix, data_mask_dict, mask_mode)
		add_information(version, modules, ec_code, mask_mode, matrix2)
		penalty_dict[mask_mode] = qr_penalty_count(modules, matrix2)
	
	if modules >= 21:
		mask_mode = min(penalty_dict, key=penalty_dict.get)
	elif modules < 21:
		mask_mode = max(penalty_dict, key=penalty_dict.get)
	
	return mask_mode
