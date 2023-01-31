import pandas as pd
import os
import numpy as np
import csv
import json

file = "new_messages.csv"

df = pd.read_csv(file)

#reset the index

df.reset_index(drop=True, inplace=True)

#drop "Unnamed Column and cdifid column"

df.drop(df.filter(regex="Unnamed"), axis = 1, inplace = True)
df.drop(df.filter(regex="Target.Identification.cdifid"), axis = 1, inplace = True)

#Delete "Iridium Ranger from DF"

df["Target.Identification.number"] = df["Target.Identification.number"].str.replace(r"[^0-9.]", "")
df["Target.Identification.description"] = df["Target.Identification.description"].str.replace(r"[^0-9.]", "")

#convert to dictionary

myhtml = df.to_dict("record")

# Convert dict to json with correct format

json_object = json.dumps(myhtml, indent = 4) 

newdf2 = str("var data = ") + json_object

print(newdf2)

file = open('data3.js','w')
file.write(newdf2)
file.close



