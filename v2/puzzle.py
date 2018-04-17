def create_puzzle(self, m):
    return MD5(bin(random.randint(0, 2**m-1))[2:])


def solve_puzzle(self, m, puzzle):
    for i in range(2**m):
        if MD5(bin(i)[2:]) == puzzle:
            return i
    return null
