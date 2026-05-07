#!/usr/bin/env python
# coding: utf-8

# In[1]:


pip install pandas


# **Pandas** : Pandas ak python ni libraries che. Pandas data handal karva mate use thay che jeva k koi students na marks hoy to ema thi apde missing values ne remove kari sakhavi
#              and duplicates values ne remove kari sakhavi. atle k data clean karva mate pandas use thay che. large data handle kari sakhavi. pandas ak excel jevi che pn excel ma
#              small data handle thay and pandas ma large data handle thay. excel ma manually karvu pade jem k koi user ne manually video suggest karva impossible che and apde 
#              pandas ma ak var model banavi atle automatic video suggest kare model automatic past behevior na through vidoe suggest kare ek example apu k apde koi cricket no
#              joyo hoy to model bija sports na related video suggest kare. aa kam excel sheet kartu nathi. pandas ma 2 main structure che 1 sereies and 2 dataframe. Series ma 
#              single column hoy.

# **DataFrame** : DataFrame ak Table formate ma hoy che. Structure 2D ma hoy che multiple columns and row hoy che . DataFrame ak multiple columns no group hoy che. atle data ne 
#                 analysis kari sakhavi. jem k koi student na data ne handle karva che to data mathi top student find kari sakhiye , avgrage value find kari sakhavi. Ai/ML model
#                 use karti pela data ne clean karva pade. missing value ne handel karvu pade and model ne format ma handle karvu pade .
#                 row data -> DataFrame -> clean data -> ML model use kare.

# In[9]:


import pandas as pd
data = {
    "name" : ["A","B","C"],
    "Marks" : [20,15,30]
}


df=pd.DataFrame(data)
print(df)

#   name  Marks
# 0    A     20
# 1    B     15
# 2    C     30

A=df.head()
print("Student data:",A)

# Student data:   name  Marks
# 0    A     20
# 1    B     15
# 2    C     30


#particular colums Select
df["Marks"]
# 0    20
# 1    15
# 2    30
# Name: Marks, dtype: int64




#Filter 
b = df[df["Marks"] >15]
print(b)
#   name  Marks
# 0    A     20
# 2    C     30


# **CSV file** : csv file data store karva mate simple formate che. jem database mysql ma data store thay am csv file ma data store kare che. jem k koi online shopping 
#                amazon ma csv file data store thay che atle easy joy sake k kaya product ni best selling che am. and csv file ne easy read and write kari sakhavi in pandas ma.
#                
#               

# In[17]:


import pandas as pd

df=pd.read_csv("train.csv")
df


# In[26]:


df.head()


# In[27]:


df.tail()


# In[28]:


#passenger survived

import pandas as pd

df = pd.read_csv("train.csv")

df["Survived"].value_counts()

Survived
# 0    10
# 1     9
# Name: count, dtype: int64


# In[29]:


#passenger average age 

import pandas as pd

df = pd.read_csv("train.csv")

df["Age"].mean()

# np.float64(28.0)


# In[30]:


# passenger ticket class

import pandas as pd

df = pd.read_csv("train.csv")

df["Pclass"].value_counts()


# Pclass
# 3    12
# 1     4
# 2     3
# Name: count, dtype: int64


# In[33]:


#missing values in age 

import pandas as pd

df = pd.read_csv("train.csv")
df[df["Age"].isnull()]

