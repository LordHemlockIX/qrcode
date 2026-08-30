import matplotlib.pyplot as plt

mask_dict = {"000": lambda i,j: (i+j)%2,
			 "001": lambda i: i%2,
			 "010": lambda j: j%3,
			 "011": lambda i,j: (i+j)%3,
			 "100": lambda i,j: ((i//2) + (j//2))%2,
			 "101": lambda i,j: (i*j)%2 + (i*j)%3,
			 "110": lambda i,j: ((i*j)%2 + (i*j)%3)%2,
			 "111": lambda i,j: ((i+j)%2 + (i*j)%3)%2}
			 		 
mask = []
modules = 25

for i in range(modules):
	l = []
	for j in range(modules):
		x = mask_dict["111"](i,j)
		l.append(x)
	mask.append(l)
	
plt.imshow(mask, cmap='gray')
plt.axis("off")
plt.show()
