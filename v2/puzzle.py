from hashlib import md5
import random

# RESEND_CODE = 2
# CREATE_CODE = 3

def create_puzzle(m):
	res = md5(bin(random.randint(2**(m-1)-1, 2**m-1))[2:])
	return str(res.hexdigest())


def solve_puzzle(m, puzzle):
	for i in range(2**m):
		if str(md5(bin(i)[2:]).hexdigest()) == puzzle:
			return i
	return None

# def puzzle_level(type):
# 	if type == "resend":
# 		return RESEND_CODE
# 	elif type == "create":
# 		return CREATE_CODE
# 	else:
# 		return 1