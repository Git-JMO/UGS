import pandas as pd
import os
import numpy as np
import csv
import json

#import the new UG file
file = "C:\\Users\\MoraleJ\\Documents\\new_messages.csv"
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

#Convert to string and add "var data =" before dictionary 
newdf = str("var data =") + str(myhtml)

#Write js file
#file = open('C:\\Users\\MoraleJ\\Documents\\test.js','w')
#file.write(newdf)
#file.close

#The above works perfect; however, the file is not recognized as a js file in VS Code
#due to change in format when converting to string. We need to find a way to add "var data =" in front of myhtml
#without changing the format.

jsonString = json.dumps(myhtml)
newdf2 = str("var data = ") + jsonString

file = open('C:\\Users\\MoraleJ\\Documents\\test.js','w')
file.write(newdf2)
file.close

print(newdf2)
