#!/usr/bin/env python
# coding: utf-8

# In[51]:


# Use the Iris dataset - it comes built into scikit-learn

# Import library
from sklearn.datasets import load_iris

# Load Iris dataset
iris = load_iris()

# Print feature names
print("Feature Names:")
print(iris.feature_names)

# Print target names
print("\nTarget Names:")
print(iris.target_names)

# Print first 5 rows of data
print("\nFirst 5 Data Rows:")
print(iris.data[:5])

# Print first 5 target values
print("\nFirst 5 Target Values:")
print(iris.target[:5])


# In[57]:


#Logistic Regression
# Import libraries

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

# 1. Scikit-learn માંથી Iris dataset load કરો
iris_data = load_iris()


# shuffle rows
df = df.sample(frac=1, random_state=42)

# Dataset જુઓ
print(df.head())



# -------------------------------
# Train-Test Split
# -------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,   # 20% testing
    random_state=42
)

# -------------------------------
# Logistic Regression Model
# -------------------------------
model = LogisticRegression()

# Model train કરો
model.fit(X_train, y_train)

# -------------------------------
# Prediction
# -------------------------------
y_pred = model.predict(X_test)


# -------------------------------
# New Flower Prediction
# -------------------------------
new_flower = pd.DataFrame(
    [[5.1, 3.5, 1.4, 0.2]],
    columns=iris_data.feature_names
)
prediction = model.predict(new_flower)

flower_name = iris_data.target_names[prediction[0]]


print("\nPredicted Flower:", flower_name)


# In[58]:


# Decision Tree

# Import libraries

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier


# -----------------------------------
# 1. Load Iris Dataset
# -----------------------------------
iris_data = load_iris()



# shuffle rows
df = df.sample(frac=1, random_state=42)

# Dataset જુઓ
print(df.head())



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
# Decision Tree Model
# -----------------------------------
model = DecisionTreeClassifier()

# Model Train કરો
model.fit(X_train, y_train)

# -----------------------------------
# Prediction
# -----------------------------------
y_pred = model.predict(X_test)

# -----------------------------------
# New Flower Prediction
# -----------------------------------
new_flower = pd.DataFrame(
    [[7.1, 5.5, 6.4, 1.2]],
    columns=iris_data.feature_names
)

prediction = model.predict(new_flower)

flower_name = iris_data.target_names[prediction[0]]

print("\nPredicted Flower:", flower_name)


# In[59]:


# Random Forest

# Import libraries

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

# -----------------------------------
# 1. Load Iris Dataset
# -----------------------------------
iris_data = load_iris()


# shuffle rows
df = df.sample(frac=1, random_state=42)

# Dataset જુઓ
print(df.head())



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
# Random Forest Model
# -----------------------------------
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

# Model Train કરો
model.fit(X_train, y_train)

# -----------------------------------
# Prediction
# -----------------------------------
y_pred = model.predict(X_test)



# -----------------------------------
# New Flower Prediction
# -----------------------------------
new_flower = pd.DataFrame(
    [[5.1, 3.5, 1.4, 0.2]],
    columns=iris_data.feature_names
)

prediction = model.predict(new_flower)

flower_name = iris_data.target_names[prediction[0]]

print("\nPredicted Flower:", flower_name)


# In[42]:


# Compare Logistic Regression, Decision Tree, Random Forest

# -----------------------------------
# Import Libraries
# -----------------------------------


from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import accuracy_score

# -----------------------------------
# Load Dataset
# -----------------------------------
iris_data = load_iris()


# -----------------------------------
# Train-Test Split
# -----------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# ===================================
# 1. Logistic Regression
# ===================================
log_model = LogisticRegression()

log_model.fit(X_train, y_train)

log_pred = log_model.predict(X_test)

log_accuracy = accuracy_score(y_test, log_pred)

# ===================================
# 2. Decision Tree
# ===================================
tree_model = DecisionTreeClassifier()

tree_model.fit(X_train, y_train)

tree_pred = tree_model.predict(X_test)

tree_accuracy = accuracy_score(y_test, tree_pred)

# ===================================
# 3. Random Forest
# ===================================
forest_model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

forest_model.fit(X_train, y_train)

forest_pred = forest_model.predict(X_test)

forest_accuracy = accuracy_score(y_test, forest_pred)




print("\nTraining Accuracy")
print("Logistic Regression :", log_model.score(X_train, y_train))
print("Decision Tree       :", tree_model.score(X_train, y_train))
print("Random Forest       :", forest_model.score(X_train, y_train))


print("\nTesting Accuracy")
print("Logistic Regression :", log_model.score(X_test, y_test))
print("Decision Tree       :", tree_model.score(X_test, y_test))
print("Random Forest       :", forest_model.score(X_test, y_test))



# **Which Model Best** 
# 
# In this dataset, all three models gave the same testing accuracy of 100%.
# However, I think Random Forest performed the best because it combines many decision trees together, which makes the model more stable and reduces overfitting.
# 
# Decision Tree can sometimes memorize the training data, but Random Forest takes votes from multiple trees, so its predictions are usually more reliable.
# 
# Logistic Regression also performed well, but it works best for simple patterns. Since Random Forest can handle complex patterns better, I think it is the best model among the three.
# 
# Iris dataset is a very easy dataset. So Logistic Regression also works perfectly.
