import json
import numpy as np
import matplotlib.pyplot as plt

def readJSON(_file):
    print(".read")
    with open(_file, "r") as f:
        data = json.load(f)
        if "coords" in data:
            ne = len(data["coords"])
            x0 = np.empty((ne, 1))
            y0 = np.empty((ne, 1))
            for i in range(ne):
                x0[i] = float(data["coords"][i][0])
                y0[i] = float(data["coords"][i][1])
        if "connect" in data:
            connect = np.array(data["connect"])
        if "forces" in data:
            forces = np.array(data["forces"])
        return ne, x0, y0, connect, forces

def outputRes(_res):
    dict_res = {"resultado": _res}
    with open("output.json", "w") as f:
        json.dump(dict_res, f)

def main(_file):
    print(".DEM")
    # read input file
    N = 600
    h = 0.00004
    ne, x0, y0, conect, F = readJSON(_file)
    ndofs = 2 * ne
    raio = 1.0
    mass = 7850.0
    kspr = 210000000000.0

    # F = np.array([
    #     [0.0, 0.0],
    #     [0.0, 0.0],
    #     [0.0, 0.0],
    #     [0.0, 0.0],
    #     [0.0, 0.0],
    #     [0.0, 0.0],
    #     [0.0, 0.0],
    #     [0.0, 0.0],
    #     [0.0, 0.0],
    #     [0.0, 0.0],
    #     [0.0, 0.0],
    #     [0.0, 0.0],
    #     [0.0, 0.0],
    #     [0.0, 0.0],
    #     [0.0, 0.0],
    #     [-1000.0, 0.0],
    #     [-1000.0, 0.0],
    #     [-1000.0, 0.0]
    # ])
    restrs = np.array([
        [1, 1],
        [1, 1],
        [1, 1],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0]
    ])
    F = F.T.reshape((ndofs, 1))
    restrs = restrs.T.reshape((ndofs, 1))
    
    print("ne:", ne)
    # ... (outros prints, se necessário)

    u = np.zeros((ndofs, 1))
    v = np.zeros((ndofs, 1))
    a = np.zeros((ndofs, 1))
    res = np.zeros(N)

    fi = np.zeros((ndofs, 1))
    a[:] = (F - fi) / mass
    for i in range(N):
        v += a * (0.5 * h)
        u += v * h
        # contato
        fi[:] = 0.0
        for j in range(ne):
            if restrs[2 * j] == 1:
                u[2 * j] = 0.0
            if restrs[2 * j + 1] == 1:
                u[2 * j + 1] = 0.0
            xj = x0[j] + u[2 * j]
            yj = y0[j] + u[2 * j + 1]
            for index in range(int(conect[j, 0])):
                k = int(conect[j, index + 1]) - 1  # Ajuste para indexação base-0
                xk = x0[k] + u[2 * k]
                yk = y0[k] + u[2 * k + 1]
                dX = xj - xk
                dY = yj - yk
                di = np.sqrt(dX**2 + dY**2)
                d2 = di - 2 * raio
                dx = d2 * dX / di
                dy = d2 * dY / di
                fi[2 * j] += kspr * dx
                fi[2 * j + 1] += kspr * dy
        a[:] = (F - fi) / mass
        v += a * (0.5 * h)
        # plot
        res[i] = u[32]  # Ajuste para indexação base-0
    outputRes(res)
    x = np.arange(1, N + 1)
    plt.plot(x, res)
    plt.show()

if __name__ == "__main__":

    main("points.json")
