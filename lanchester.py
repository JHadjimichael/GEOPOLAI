class lanchester_battle:
    def __init__(self) -> None:
        pass

    def run_battle(self, A, alpha, B, beta):
        A_Army = A
        B_Army = B

        while A_Army >= 1 and B_Army >= 1:
            dA = -beta * B_Army
            dB = -alpha * A_Army
            #print(dA, dB)
            A_Army = A_Army+dA
            B_Army = B_Army+dB
            #print(A_Army, B_Army)

        if A_Army <= 1 and B_Army <= 1:
            return "Tie"
        elif A_Army <= 1:
            return "B", B_Army
        elif B_Army <= 1:
            return "A", A_Army
