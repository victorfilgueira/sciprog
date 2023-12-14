#Métodos das Diferenças Finitas
import numpy as np

L = 10
n = 6

dx = L/(n-1)

restr1 = [1, 300]
restr2 = [1, 400]

A = np.zeros(shape=(n,n))
b = np.zeros(shape=(n,1))

for i in range(n-2):
    A[i+1, i] = -1
    A[i+1, i+1] = 2.2
    A[i+1, i+2] = -1
    b[i+1] = 40
    
if (restr1[0]==1):
    A[0,0] = 1
    b[0] = restr1[1]
    
if (restr2[0]==1):
    A[n-1,n-1] = 1
    b[n-1] = restr2[1]
    
T = np.linalg.solve(A, b)

print(A)
print(b)
print(T)