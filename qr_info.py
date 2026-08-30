# 1. Version (for standard QR Code from 1 to 40)
# 2. N° of modules
# 3. N° if Alignment Patterns
# 4. Row, Col information position for the Alignment (pg. 91 Table E.1)
# 5. Error correction levels for each module tha can be L, M, Q, H
# 6. Total number of codewords: represent the total number of bytes available for a specific version 
# 6. Number of data codewords: represent the number of bytes for the specific oly of the data and not considering the EC and Remainder bits
# 7. Number of data bits: represent the maximum number of bits so bytes*8. It can be threfore easily calculate from step 6.
# 8. Numeric/Alphanumeric/Byte/Kanji rapresent the maximum encoding space of numbers, charaters, bytes and charactes (Japanese)
# 9. p value: number of misdecoded protection codewords
# 10. number of error correction blocks: This approach is used to make the most of EC algorithms and, by employing interleaving, to ensure greater resistance to physical effects on the QR code.
# 11. Error correction per block: (c,k,r), c = total number of codewords, k = number of data codewords, r = error correction capacity (bytes)

dict_qr_info = {}

with open("QR_CODE_DB.txt", "r") as file:
	lines = file.readlines()
file.close()

for i, line in enumerate(lines):
	l = line.split()
	if i == 0:
		dict_qr_info["cols"] = []
		for ele in l[1:]:
			dict_qr_info["cols"].append(ele)
	else:
		dict_qr_info[l[0]] = [] 
		for ele in l[1:]:
			dict_qr_info[l[0]].append(ele)

print(dict_qr_info["-1"])
