import json
import numpy as np

def main(filename):
    # Lendo o JSON
    with open(filename, 'r') as f:
        inDict = json.load(f)

    pontos = np.array(inDict['coords'], dtype=int)
    contorno = np.array(inDict['contour'], dtype=int)

    bloco = [4, -1, -1, -1, -1]
    n, cols = pontos.shape

    # Iniciando matrize A e vetor b
    A = np.zeros((n, n), dtype=float)
    b = np.zeros((n, 1), dtype=float)

    # print(len(pontos))
    # print(len(contorno))
    # Montando A e b
    for i in range(n):
        A[i, i] = bloco[0]
        for j in range(cols):
            loc = pontos[i, j]
            if 0 < loc < len(contorno):
                # print(loc)
                if contorno[loc, 0] == 0:
                    A[i, loc] = bloco[j + 1]
                else:
                    b[i, 0] += contorno[loc, 1]

    for i in range(n):
        if contorno[i, 0] == 1:
            A[i, :] = np.zeros(n)
            A[i, i] = 1.0
            b[i, 0] = contorno[i, 1]

    # Resolvendo o sistema linear
    x = np.linalg.solve(A, b)

    # Salvando a solução em um arquivo JSON
    data = {"temp": x.flatten().tolist()}
    with open("resultado.json", "w") as f:
        json.dump(data, f)

if __name__ == "__main__":
    main("points.json")