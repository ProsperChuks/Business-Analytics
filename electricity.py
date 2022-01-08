# -*- coding: utf-8 -*-
"""Electricity.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1G2HwnSeq0bKj-hQvSyKusABOdIFm_-zF

# Dependencies
"""

import pickle
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import pandas as pd

"""# De-serializing data"""

electric = pickle.load(open('/content/drive/MyDrive/Colab Notebooks/Assessment/ML&Business_Analytics/serialized files/electric.pkl', 'rb'))
electric

"""# Preprocessing"""

electric = electric[['user_id', 'TotalTransactionAmount', 'Tx_Count', 'DaysSinceLastTrans']]
electric

electric.describe()

elec_customers = electric.groupby(['user_id']).agg({
    'TotalTransactionAmount': 'sum',
    'Tx_Count': 'count',
    'DaysSinceLastTrans' : 'sum'
})

elec_customers.rename(columns={'TotalTransactionAmount': 'Amount',
                                 'Tx_Count': 'Freq',
                                'DaysSinceLastTrans': 'Re'}, inplace=True)
elec_customers

print(elec_customers.Re.skew())
print(elec_customers.Freq.skew())
print(elec_customers.Amount.skew())

"""## Converting Data to Gaussian Distribution

### Visualization
"""

import warnings
warnings.filterwarnings('ignore')

fig, ax = plt.subplots(2, 2, figsize=(12, 7))

fig = sns.distplot(elec_customers.Re, color='b', ax=ax[0, 0])
fig = sns.distplot(elec_customers.Amount, color='g', ax=ax[0, 1])
fig = sns.distplot(elec_customers.Freq, color='y', ax=ax[1, 0])
ax[0, 0].set_title('Recency')
ax[0, 1].set_title('Income')
ax[1, 0].set_title('Frequency')

plt.tight_layout()
plt.show()

"""### Log Transformation"""

log_trans = pd.DataFrame()
log_trans['Amount'] = np.log(elec_customers['Amount'])
log_trans['Freq'] = np.log(elec_customers['Freq'])
log_trans['Re'] = np.log(elec_customers['Re'])

print(log_trans.Re.skew())
print(log_trans.Freq.skew())
print(log_trans.Amount.skew())

"""#### After-Log-Transformation"""

fig, ax = plt.subplots(2, 2, figsize=(12, 7))

fig = sns.distplot(log_trans.Re, color='b', ax=ax[0, 0])
fig = sns.distplot(log_trans.Amount, color='g', ax=ax[0, 1])
fig = sns.distplot(log_trans.Freq, color='y', ax=ax[1, 0])
ax[0, 0].set_title('Recency')
ax[0, 1].set_title('Income')
ax[1, 0].set_title('Frequency')

plt.tight_layout()
plt.show()

"""### BoxCox Transfromation"""

boxcox_trans = pd.DataFrame()
boxcox_trans['Amount'] = stats.boxcox(elec_customers['Amount'])[0]
boxcox_trans['Freq'] = stats.boxcox(elec_customers['Freq'])[0]
boxcox_trans['Re'] = stats.boxcox(elec_customers['Re'])[0]

print(boxcox_trans.Re.skew())
print(boxcox_trans.Freq.skew())
print(boxcox_trans.Amount.skew())

"""#### After-Boxcox-Transformation"""

fig, ax = plt.subplots(2, 2, figsize=(12, 7))

fig = sns.distplot(boxcox_trans.Re, color='b', ax=ax[0, 0])
fig = sns.distplot(boxcox_trans.Amount, color='g', ax=ax[0, 1])
fig = sns.distplot(boxcox_trans.Freq, color='y', ax=ax[1, 0])
ax[0, 0].set_title('Recency')
ax[0, 1].set_title('Income')
ax[1, 0].set_title('Frequency')

plt.tight_layout()
plt.show()

"""### Square Root Transformation"""

square_trans = pd.DataFrame()
square_trans['Amount'] = np.sqrt(elec_customers['Amount'])
square_trans['Freq'] = np.sqrt(elec_customers['Freq'])
square_trans['Re'] = np.sqrt(elec_customers['Re'])

print(square_trans.Re.skew())
print(square_trans.Freq.skew())
print(square_trans.Amount.skew())

"""#### After-Square-Root-Transformation"""

fig, ax = plt.subplots(2, 2, figsize=(12, 7))

fig = sns.distplot(square_trans.Re, color='b', ax=ax[0, 0])
fig = sns.distplot(square_trans.Amount, color='g', ax=ax[0, 1])
fig = sns.distplot(square_trans.Freq, color='y', ax=ax[1, 0])
ax[0, 0].set_title('Recency')
ax[0, 1].set_title('Income')
ax[1, 0].set_title('Frequency')

plt.tight_layout()
plt.show()

"""<b>BOX COX Transfroms the Data Better</b>

### Normalization
"""

scale = StandardScaler()
scale.fit(boxcox_trans)
electric_normalized = scale.transform(boxcox_trans)

fig, ax = plt.subplots(2, 2, figsize=(12, 7))

fig = sns.distplot(electric_normalized[0], color='b', ax=ax[0, 0])
fig = sns.distplot(electric_normalized[1], color='g', ax=ax[0, 1])
fig = sns.distplot(electric_normalized[2], color='y', ax=ax[1, 0])
ax[0, 0].set_title('Recency')
ax[0, 1].set_title('Income')
ax[1, 0].set_title('Frequency')

plt.tight_layout()
plt.show()

print(electric_normalized.mean(axis = 0).round(2))
print(electric_normalized.std(axis = 0).round(2))

"""## Clustering

### Hyperparameter Tuning using the Elbow Method
"""

sse = {}

for k in range(1, 11):
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(electric_normalized)
    sse[k] = kmeans.inertia_
plt.title('The Elbow Method')
plt.xlabel('Number of Clusters')
plt.ylabel('Sum of Squared Distance')
sns.pointplot(x=list(sse.keys()), y=list(sse.values()))
plt.show()

model = KMeans(n_clusters=3, random_state=42)
model.fit(electric_normalized)
model.labels_

"""### Matching labels with each customer"""

elec_customers["Cluster"] = model.labels_
elec_customers.groupby('Cluster').agg({
    'Re':'mean',
    'Freq':'mean',
    'Amount':['mean', 'count']}).round(2)

"""### Melting the Dataframe"""

df_normalized = pd.DataFrame(electric_normalized, columns=['Re', 'Freq', 'Amount'])
df_normalized['Cust ID'] = elec_customers.index
df_normalized['Cluster'] = model.labels_

df_nor_melt = pd.melt(df_normalized.reset_index(),
                      id_vars=['Cust ID', 'Cluster'],
                      value_vars=['Re','Freq','Amount'],
                      var_name='Attribute',
                      value_name='Value')
df_nor_melt

plt.figure(figsize=(15, 8))
sns.lineplot('Attribute', 'Value', hue='Cluster', data=df_nor_melt)
plt.show()