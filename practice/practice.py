#!/usr/bin/env python
# coding: utf-8

# In[4]:


#different size and shape

#1D Array
import numpy  as np 

a = np.array([1,2,3,4,5])
print("1D array: ",a)
print("Array Shape:",np.shape(a))
print("Array size: ",np.size(a))
print("Array Dimension: ",np.ndim(a))

# 1D array:  [1 2 3 4 5]
# Array Shape: (5,)
# Array size:  5
# Array Dimension:  1

#2D array


a=np.array([[1,2,3],[2,5,4]])
print("2D array: ",a)
print("Array Shape:",np.shape(a))
print("Array size: ",np.size(a))
print("Array Dimension: ",np.ndim(a))


# 2D array:  [[1 2 3]
#  [2 5 4]]
# Array Shape: (2, 3)
# Array size:  6
# Array Dimension:  2
# [[[1 2 3]
#   [2 5 4]]]

#3D array

a=np.array([[[1,2,3],[1,2,2]],[[5,9,6,],[7,5,3]]])
print("3D array: ",a)
print("Array Shape:",np.shape(a))
print("Array size: ",np.size(a))
print("Array Dimension: ",np.ndim(a))

# 3D array:  [[[1 2 3]
#   [1 2 2]]

#  [[5 9 6]
#   [7 5 3]]]
# Array Shape: (2, 2, 3)
# Array size:  12
# Array Dimension:  3


# In[30]:


#basic math in numpy
#addition
import numpy as np
a=np.array([1,2,9,8])
b=np.array([2,6,5,4])

print("Addition:",a+b)

# Addition: [ 3  8 14 12]

#subtraction

a=np.array([[1,5,6],[9,8,9]])
b=np.array([[1,2,3],[5,5,7]])
print("Subtraction: ",a-b)

# Subtraction:  [[0 3 3]
#  [4 3 2]]


#Average

a=np.array([[1,5,6],[9,8,9]])
b=np.array([[1,2,3],[5,5,7]])
print("Average : ",np.mean([a,b]))

# Average :  5.083333333333333



#maximum 

arr = np.array([1,2,6,8,41,3])
print("Maximum : ",np.max(arr))
print("Minimum : ",np.min(arr))
print("Std: ",np.std(arr))

# Maximum :  41
# Minimum :  1
# Std:  13.993053832368243


# In[18]:


#Slicing 

import numpy as np
a=np.array([[1,8,7],
            [9,5,3]])
print("Single element row and col")
print(a[0,1])

# Single element row and col
# 8

print("Single Row")
print(a[0])
print(a[-1])

# Single Row
# [1 8 7]
# [9 5 3]

print("Single column")
print(a[:,-1])

# Single column
# [7 3]

print("Slicing Element")
print(a[0:2])      
print(a[0:2, 1:3]) 

# Slicing Element
# [[1 8 7]
#  [9 5 3]]
# [[8 7]
#  [5 3]]


# In[25]:


import numpy as np
a=np.arange(1,21)
print("Array: ",a)

# Array:  [ 1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20]
even = a[a % 2 == 0]
print("Even :",even)
# Even : [ 2  4  6  8 10 12 14 16 18 20]

odd = a[a % 2 != 0]
print("Odd: ",odd)
# Odd:  [ 1  3  5  7  9 11 13 15 17 19]


# In[29]:


a = np.array([12, 3, 45, 7, 89, 23, 4, 56])
b = a[a>20]
print("A greater than 20:",b)

# A greater than 20: [45 89 23 56]


# In[35]:


a = np.array([[10,20,30,40],
              [50,60,70,80],
              [90,100,110,120]])
print("Row 1 and 2 , col 1 and 2 :",a[1:3,1:3])


# Row 1 and 2 , col 1 and 2 : [[ 60  70]
#  [100 110]]


# In[ ]:




