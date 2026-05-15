#!/usr/bin/env python
# coding: utf-8

# In[4]:


# -----------------------------------
# Import Libraries
# -----------------------------------

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import classification_report

# -----------------------------------
# Load Dataset
# -----------------------------------

iris = load_iris()

X = iris.data
y = iris.target

# -----------------------------------
# Train-Test Split
# -----------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# -----------------------------------
# Train Model
# -----------------------------------

model = RandomForestClassifier(random_state=42)

model.fit(X_train, y_train)

# -----------------------------------
# Predictions
# -----------------------------------

y_pred = model.predict(X_test)

# -----------------------------------
# Classification Report
# -----------------------------------

report = classification_report(y_test, y_pred)

print(report)


# In[7]:


from sklearn.metrics import confusion_matrix

y_true = [0,0,0,1,1,1,1]
y_pred = [0,0,1,1,0,1,1]

cm = confusion_matrix(y_true, y_pred)

print(cm)


# In[13]:


import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

# 1. Tamara actual ane predicted data (Example)
# 1 = Dog, 0 = Cat
actual_data = [1, 1, 1, 1, 1, 1, 0, 0, 0, 0]
predicted_data = [1, 1, 1, 1, 1, 0, 0, 0, 1, 1]

# 2. Confusion matrix compute karo
cm = confusion_matrix(actual_data, predicted_data)

# 3. Matrix ne draw karva mate Display tool vapro
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['Cat', 'Dog'])

# 4. Plot draw karo
disp.plot(cmap=plt.cm.Blues)
plt.title("Confusion Matrix")
plt.show()


# **When Precision matters more than Recall**
# 
# Situation: Spam Email Detection
# suppose gmail filter kare che k email spam che k nai.
# 
# Goal: Jo system kahe “aa spam che”, to almost sure spam j hovu joie.
# **Why Precision Important?**:
# 
# Imagine important email avi:
# 
# Job offer
# College admission
# Bank OTP
# 
# Ane model ene spam ma muki de 
# 
# To user important mail joi j nahi shake.
# 
# So ahiya False Positive dangerous che.
# 
# False Positive = Normal email ne spam kahi devu.
# 
# Example
# 
# 100 emails ma:
# 
# 10 actual spam hata
# Model e 12 emails ne spam kidha
# Tema thi 9 really spam hata
# 3 normal emails hata
# 
# So:
# Precision = Correct spam detected / Total spam predicted
# 
# Matlab:
# “System je spam kahe che, ema 75% sachu che.”
# 
# Real-world meaning:
# Spam filter ma:
# 
# Thoda spam miss thai jai to chale
# Pan important email block na thavi joie
# 
# Etle Precision > Recall
# 
# **When Recall matters more than Precision** :
# 
# Situation: Cancer Detection
# Hospital ma AI detect kare che ke patient ne cancer che ke nahi.
# 
# Goal:Jitla possible cancer patients hoy badha pakdai java joie.
# 
# **Why Recall Important?** 
# 
# Suppose person ne actual cancer che pan model kahe: “Tamne cancer nathi.” Aa khub dangerous che.Treatment late thai shake.Ahiya  False Negative dangerous che.
# 
# False Negative = Sick person ne healthy kahi devu.
# 
# Example:
# 100 patients ma:
# 20 ne actual cancer hato
# Model e 18 cancer patients pakdya
# 2 miss kari didha
# 
# So:
# 
# Recall = Correct cancer detected / Total actual cancer cases
# 
# Matlab:
# “Actual cancer vala 90% loko system e pakdi lidha.”
# 
# Real-world meaning:
# Hospital ma:
# 
# Thoda healthy loko ne extra test mate moklava chale
# Pan actual cancer patient miss na thavo joie
# Etle Recall > Precision
