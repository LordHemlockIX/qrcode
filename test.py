from qr_encoding import check_numeric, check_alphanumeric, check_byte, check_kanji

#data = "こんばんは"
data = "Hello_MyNameis009911"

modes = []
exclusive_modes = {}

for c in data:
	if check_numeric(c):
		modes.append('N')
	elif check_alphanumeric(c):
		modes.append('A')
	elif check_byte(c):
		modes.append('B')
	elif check_kanji(c):
		modes.append('K')
	else:
		mode.append(None)

start = 0
end = None
for i in range(len(modes)-1):
	if modes[i] != modes[i+1] or i == len(modes)-3:
		end = i+1
		m = modes[start:end]
		if len(set(m)) == 1:
			try:
				exclusive_modes[m[0]].append([start, end])
			except KeyError:
				exclusive_modes[m[0]] = []
				exclusive_modes[m[0]].append([start, end])
			start = i+1
			end = None
			
print(exclusive_modes)

highest_mode = None

if 'K' in list(exclusive_modes.keys()):
	highest_mode = 'K'
elif 'B' in list(exclusive_modes.keys()):
	highest_mode = 'B'
elif 'A' in list(exclusive_modes.keys()):
	highest_mode = 'A'

print(highest_mode)



"""if len(set(modes)) == 1:
	final_modes = list(set(modes))
	print(f"Exclusive mode used: {final_modes[0]}")
else:
	print(modes)"""
