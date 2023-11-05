from fastapi import FastAPI, HTTPException
import json
from pydantic import BaseModel
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeRegressor

class Item(BaseModel):
	idPasien: int
	idDokter:int
	bloodPressure: int
	weight: int
	height: int

class Hasil(BaseModel):
	def __init__(self, idTest,idPasien,idDokter,hasilUji) :
		self.idTest = idTest
		self.idPasien = idPasien
		self.idDokter = idDokter
		self.hasilUji = hasilUji
       
	



json_filename="pasien.json"

with open('hasilTest.json',"r") as read_file:
	test = json.load(read_file)
with open(json_filename,"r") as read_file:
	data = json.load(read_file)
app = FastAPI()

dataset1 = pd.read_csv('MOCK_DATA (1).csv')
X=dataset1[['TekananDarah', 'TinggiBadan', 'BeratBadan']]
y=dataset1['Penyakit'] 
X=X.values
y=y.values
svr = DecisionTreeRegressor()
svr.fit(X,y)
app = FastAPI()

@app.get('/all')
async def read_all_hasil():
	return test['hasil']

@app.post('/predict')
async def check_disease(item: Item):
	i = 0
	item_dict = item.dict()
	y_pred=svr.predict([[item_dict.get("bloodPressure"),item_dict.get("weight"),item_dict.get("height")]])
	y_pred=y_pred.tolist()
	penyakit = "sehat"
	if y_pred[0] == 1:
		penyakit = "sehat"
	elif y_pred[0] == 2:
		penyakit = "darah rendah"
	else:
		penyakit= "darah tinggi"
		
		
	item_found = False
	for pasien in data['pasien']:
		if pasien['idPasien'] == item_dict['idPasien']:
			for jumlah in test["hasil"]:
				i=i+1
			i=i+1
			input= {
                "idTest": i,
                "idPasien": item_dict.get("idPasien"),
                "idDokter": item_dict.get("idDokter"),
				"hasilUji":penyakit  # Mengubah hasil prediksi menjadi string
            }
			test["hasil"].append(input)
			with open('hasilTest.json',"w") as write_file:
				json.dump(test, write_file)
			return penyakit
    
	raise HTTPException(
		status_code=404, detail=f'id pasien tidka ditemukan'
	)
	




