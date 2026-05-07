#!/usr/bin/env python
# coding: utf-8

# In[6]:


pip install matplotlib


# In[7]:


pip install seaborn


# **Data Visualization**: data visualization a data ne graph,chart,dashboard jevi visual form ma batava mate use thay jethi saralatathi samjay jay.
#                         jo koi data number ma hoy to ene joy ne khaber no pade k kayo data u keva mage che and visualization thi khaber pade k kayo data su keva mage che .
#                         jem k student na marks and subject vise hoy to chart thi khaber pade k kayo subject e sara progress karo che am.

# **Bar chart** : bar chart is type of graph.It is used to compare different catagories of data.bar chart ma catagories comapre karvi easy bane che. suppose k
#                 class ma ketla student each subject ma pass thaya. bar chart instantly batave k kaya subject ma vadhu student pass thaya am.

# In[13]:


#bar chart

import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv("train.csv")

survival_count = df.groupby("Pclass")["Survived"].sum()


survival_count.plot(kind="bar",color=["green", "orange", "red"])


plt.title("Survival Count by Passenger Class")
plt.xlabel("Passenger Class")
plt.ylabel("Number of Survivors")

plt.show()


# **Histogram** : histogram chart show kare k how data is distributed.histogram ma numbers ni distribution batave che. histogram ma data group ma hoy che.
#                 Machine Learning ma histogram thi data samajva easy bane.Titanic dataset ma passenger age Histogram thi khabar pade.jem k ketla young che k ketla old che.

# In[16]:


#histogram

import pandas as pd
import matplotlib.pyplot as plt


titanic = pd.read_csv("train.csv")


plt.hist(titanic['Age'])

plt.xlabel("Age")
plt.ylabel("Number of Passengers")
plt.title("Age Distribution of All Passengers")


plt.show()


# **Scatter plot** : scatter plot e ak chart che. te 2 numeric value vache no relation batave che.

# In[21]:


#sactter plot

import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("train.csv")

plt.scatter(df["Age"], df["Fare"],s=20)

plt.xlabel("Age")
plt.ylabel("Fare")
plt.title("Age vs Fare")

plt.show()


# **Heatmap** : heatmap e ak chart che. jema number ne color davara batava ma ave che. jaya value vadhare hoy taya color dark/strong hoy. and jaya value ochi hoy taya light color
#               hoy che. number ne color ma convert karvu atle heatmap atle pattern and relation fast dekhay.

# In[24]:


#heatmap


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# CSV file load using pandas
df = pd.read_csv("train.csv")

# Correlation between numeric columns
corr = df.corr(numeric_only=True)

# Create heatmap
plt.figure(figsize=(10,7))

sns.heatmap(
    corr,
    annot=True,
    cmap="coolwarm",
    linewidths=0.5
)

plt.title("Titanic Dataset Heatmap")

plt.show()

