import numpy as np
import os


def fill_in_table(input_matrix):
  X = input_matrix
  m, n = X.shape
  Y = np.zeros([m, n])

  for i in range(m):
    for j in range(n):
      if i == 0 and j == 0:
        Y[i, j] = X[i, j]
      elif i == 0:
        Y[i, j] = max(Y[i, j-1], X[i, j])
      elif j == 0:
        Y[i, j] = max(Y[i-1, j], X[i, j])
      else:
        Y[i, j] = max(Y[i-1, j-1] + X[i, j],
                      Y[i-1, j],
                      Y[i, j-1])
  # traceback

  index_list = []
  m, n = Y.shape

  m -= 1
  n -= 1
  while True:
      if m == 0 and n == 0:
        index_list += [[0, 0]]
        break
      elif m == 0:
        j = list(Y[0]).index(Y[0, n])
        index_list += [[0, j]]
        break
      elif n == 0:
        j = list(Y[:, 0]).index(Y[m, 0])
        index_list += [[j, 0]]
        break

      if Y[m, n] == Y[m-1, n-1] + X[m, n]:
        index_list += [[m,n]]
        m = m-1
        n = n-1
      elif Y[m, n] == Y[m-1, n]:
        m = m-1
      elif Y[m, n] == Y[m, n-1]:
        n = n-1
  return index_list[::-1]


if __name__ == '__main__':

  #Test in small area
  X = np.eye(3)
  assert fill_in_table(X) == [[0, 0], [1, 1], [2, 2]]


  #Test in small area
  X = np.array(
        [[0.8, 0.6, 0.2],
        [0.5, 0.5, 0.5],
        [0.5, 1.0, 0.3],
        [0.1, 0.7, 0.9]])
  assert fill_in_table(X) == [[0, 0], [2, 1], [3, 2]]


  #Test in small area
  X = np.array(
        [[0.5, 0.8, 0.6, 0.2],
        [0.5, 0.5, 1.0, 0.3],
        [0.5, 0.1, 0.7, 0.9]])
  assert fill_in_table(X) == [[0, 1], [1, 2], [2, 3]]


  #Test in small area
  X = np.array(
        [[0.8, 0.6, 0.2],
        [0.5, 1.0, 0.3],
        [0.1, 0.7, 0.9]])
  assert fill_in_table(X) == [[0, 0], [1, 1], [2, 2]]

  #Test in small area
  X = np.array(
        [[0.8, 0.6, 0.5, 0.2],
        [0.5, 1.0, 0.5, 0.3],
        [0.5, 0.5, 0.5, 0.5],
        [0.1, 0.7, 0.5, 0.9]])
  assert fill_in_table(X) == [[0, 0], [1, 1], [2, 2], [3, 3]]

  print('ok')

  X = []
  if not os.path.exists('bleu_MxN/5th_Bleu.nparray'):
    for i in range(2476):
      if i%5==0:
        with open('bleu_MxN/{:04d}.txt'.format(i), 'r')as f:
          X += [float(line.strip()) for line in f.readlines()]

    X = np.array(X)
    X = X.reshape([2479,2492])
    with open('bleu_MxN/5th_Bleu.nparray', 'wb') as f:
      np.save(f, X)

  with open('bleu_MxN/5th_Bleu.nparray', 'rb') as f:
    X_read = list(np.load(f))
  print(type(X))
  exit()
  if X != []:
    assert np.array_equal(X_read, X)

  X = X_read

  print('read X.')

  index_list = fill_in_table(X)
  print(index_list)
  exit()

  # maximum recursion
      # if m == 0 and n == 0:
      #   return [[0, 0]]
      # elif m == 0:
      #   j = list(Y[0]).index(Y[0, n])
      #   return [[0, j]]
      # elif n == 0:
      #   j = list(Y[:, 0]).index(Y[m, 0])
      #   return [[j, 0]]
        
      # if Y[m, n] == Y[m-1, n-1] + X[m, n]:
      #   return traceback(Y, m-1, n-1) + [[m, n]]
      
      # elif Y[m,n] == Y[m-1, n]:
      #   return traceback(Y, m-1, n)

      # elif Y[m, n] == Y[m, n-1]:
      #   return traceback(Y, m, n-1)
  