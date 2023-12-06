import pyodbc
from typing import Annotated
from fastapi import Depends
from fastapi import FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime,timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeRegressor
import json
import requests
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
import random
from fastapi.middleware.cors import CORSMiddleware

connection_string = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:healthcareghaylan.database.windows.net,1433;Database=healthcare;Uid=sqladmin;Pwd=Mikdar123;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
def get_conn():
   # This connection option is defined by microsoft in msodbcsql.h
    conn = pyodbc.connect(connection_string)
    return conn

admin_db = {
    "admin": {
        "username": "ghaylan",
        "patientID": "12345678",
        "hashed_password": "$2b$12$InzccdYhjsaJts6wkz0OI.tvz4tJP0XR6VL/e9F0vlrnUh9MAsVsG", #apis
        "role": 'admin',
		"tokenIntegrasi":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJnaGF5bGFuIiwiaWQiOiI4In0.nmv0imRL9VvkHboO97poBvZoD-dMEMRkLJF48u7nrh8"
    }
}

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

class Item(BaseModel):
	bloodPressure: int
	weight: int
	height: int

class Hasil(BaseModel):
	def __init__(self, idTest,idPasien,idDokter,hasilUji) :
		self.idTest = idTest
		self.idPasien = idPasien
		self.hasilUji = hasilUji
class User:
	def __init__(self, name, password_hashed, patientId, role, integrasiToken):
		self.name = name
		self.password_hashed = password_hashed
		self.patientId = patientId
		self.role = role
		self.integrasiToken = integrasiToken



pwd_context = CryptContext(schemes=["bcrypt"], deprecated=["auto"])


app = FastAPI()
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
oauth_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
	return pwd_context.verify(plain_password, hashed_password)

def get_password_hashed(password):
	return pwd_context.hash(password)

def gps_get_longitude():
	result = random.randint(-90, 90)
	return result
def gps_get_latitude():
	result = random.randint(-90, 90)
	return result

def check_user(username:str):
	if username == "ghaylan":
		return True
	conn = get_conn()
	cursor = conn.cursor()
	cursor.execute("SELECT username as name FROM akun where username='%s' ;" %(username))
	for row in cursor.fetchall():
		if row.name == username or username == 'ghaylan':
			return True
	return False



async def get_curr_user(token : str = Depends(oauth_scheme)):
	payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
	if payload.get('role') == 'admin':
		try:
			admin = User(name = admin_db["admin"]["username"],password_hashed=admin_db["admin"]["hashed_password"],patientId=admin_db["admin"]["patientID"],role=admin_db["admin"]["role"], integrasiToken= admin_db["admin"]["tokenIntegrasi"])
			return admin
		except:
			raise HTTPException(status_code=401, detail="Invalid Username or Password")
	elif payload.get('role') == 'pasien':
		try:
			name=payload.get('username')
			nama=[]
			passw=[]
			id=[]
			token=[]
			conn = get_conn()
			cursor = conn.cursor()
			cursor.execute("SELECT username FROM akun where username='%s' ;" %(name))
			for row in cursor.fetchall():
				nama.append(f"{row.username}")
			cursor.execute("SELECT tokenIntegrasi FROM akun where username='%s' ;" %(name))
			for row in cursor.fetchall():
				token.append(f"{row.tokenIntegrasi}")
			cursor.execute("SELECT pass as pword FROM akun where username='%s' ;" %(name))
			for row in cursor.fetchall():
				passw.append(f"{row.pword}")
			cursor.execute("SELECT pasienID FROM akun where username='%s' ;" %(name))
			for row in cursor.fetchall():
				id.append(f"{row.pasienID}")
				
				user = User(name = nama[0], password_hashed=passw[0], patientId=id[0],role='pasien', integrasiToken=token[0])
				nama=[]
				passw=[]
				id=[]
				return user
		except:
			raise HTTPException(status_code=401, detail="Invalid Username or Password")
		

def authenticate_user(username:str,password:str):
	hashed_password=get_password_hashed(password)
	username_correct=check_user(username)
	if username_correct:
		rows=[]
		conn = get_conn()
		cursor = conn.cursor()
		tokenIntegrasi=''
		if username == 'ghaylan':
			if not verify_password(password, admin_db["admin"]["hashed_password"]):
				raise HTTPException(status_code=401, detail='invalid password')
			else:
				url = 'https://hospicall.azurewebsites.net/token'
		
				headers = {
                    'accept': 'application/json',
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
				data = {
                    'grant_type': '',
                    'username': username,
                    'password': password,
                    'scope': '',
                    'client_id': '',
                    'client_secret': ''
                }
				response = requests.post(url, headers=headers, data=data)
				if response.status_code == 200:
					result = response.json()
					tokenIntegrasi = result.get('access_token')
					admin = User(name = admin_db["admin"]["username"],password_hashed=admin_db["admin"]["hashed_password"],patientId=admin_db["admin"]["patientID"],role=admin_db["admin"]["role"], integrasiToken= tokenIntegrasi)
					return admin
		cursor.execute("SELECT pass as pword FROM akun where username = '%s'" %(username))
		for row in cursor.fetchall():
			rows.append(f"{row.pword}")
		if not verify_password(password, rows[0]):
			raise HTTPException(status_code=401, detail='invalid password')
		else:
			rows=[]
			idpasien=[]
			cursor.execute("SELECT pasienID FROM akun where username = '%s'" %(username))
			for row in cursor.fetchall():
				idpasien.append(f"{row.pasienID}")
				url = 'https://hospicall.azurewebsites.net/token'
				headers = {
					'accept': 'application/json',
					'Content-Type': 'application/x-www-form-urlencoded'
				}
				data = {
					'grant_type': '',
					'username': username,
					'password': password,
					'scope': '',
					'client_id': '',
					'client_secret': ''
				}
				response = requests.post(url, headers=headers, data=data)
				if response.status_code == 200:
					result = response.json()
					tokenIntegrasi = result.get('access_token')
					user = User(name = username, password_hashed=hashed_password, patientId=idpasien[0],role='pasien', integrasiToken=tokenIntegrasi)
				idpasien=[]
				return user 
	else:
		raise HTTPException(status_code=402, detail="invalid username")
	
@app.post("/token", tags=['generate token'])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
	user = authenticate_user(form_data.username,form_data.password)
	token = jwt.encode({'username':user.name, 'id' : user.patientId, 'role':user.role}, SECRET_KEY)
	return {"access_token": token, "token_type":"bearer"}

@app.post("/daftar", tags=['all can access'])
async def pasien_daftar(nama : str, riwayatPenyakit : str):
	conn = get_conn()
	rows=[]
	cursor = conn.cursor()
	cursor.execute("SELECT pasienID FROM pasien ORDER BY pasienID DESC")
	for row in cursor.fetchall():
		rows.append(f"{row.pasienID+1}")
	cursor.execute('''INSERT INTO pasien VALUES ('%s','%s','%s')''' %(rows[0],nama,riwayatPenyakit))
	conn.commit()
	return "pasien berhasil didaftarkan dengan id = %s" %(rows[0])

@app.get("/emergency", tags=['all can access', 'hasil integrasi'])
async def get_healthcare_phone_number(longitude : float, latitude : float):
	url='https://hospicall.azurewebsites.net/emergency'
	headers={
		'accept':'application/json',
		'Content-Type':'application/x-www-form-urlencoded'
	}
	data={
		'longitude':longitude,
		'latitude':latitude
	}
	
	response = requests.get(url,headers=headers,params=data)
	
	if response.status_code==200:
		data=response.json()
		return data
	else:
		return response.text
	
@app.get("/healthcare", tags=['all can access', 'hasil integrasi'])
async def get_all_healthcare_facilites():
	url='https://hospicall.azurewebsites.net/healthcare'
	headers={
		'accept':'application/json',
		'Content-Type':'application/x-www-form-urlencoded'
	}
	
	response = requests.get(url,headers=headers)
	
	if response.status_code==200:
		data=response.json()
		return data
	else:
		return response.text
	
@app.post("/emergency", tags=['all can access', 'hasil integrasi'])
async def make_call():
	longitude=gps_get_longitude()
	latitude = gps_get_latitude()
	url='https://hospicall.azurewebsites.net/emergency/'
	headers={
		'accept':'application/json',
		'Content-Type':'application/x-www-form-urlencoded'
	}
	data ={
		'longitude':longitude,
		'latitude':latitude
	}
	
	response = requests.post(url,headers=headers, params=data)
	
	if response.status_code==200:
		data=response.json()
		return data
	else:
		return response.text


@app.post("/users", tags=['all can access'])
async def create_user(username: str, password: str, patientId, phoneNumber:str):
	if not check_user(username):
		password_hashed = get_password_hashed(password)
		conn = get_conn()
		cursor = conn.cursor()
		
		url = 'https://hospicall.azurewebsites.net/register'
		headers = {
			'accept': 'application/json',
			'Content-Type': 'application/json'
		}
		data = {
			
			"first_name": username,
			"last_name": username,
			"email": username +"@gmail.com",
			"username": username,
			"password": password,
			"phone_number": phoneNumber
		}

		response = requests.post(url, headers=headers, json=data)
		
		# Jika berhasil register
		if response.status_code == 200:
			url = 'https://hospicall.azurewebsites.net/token'
			headers = {
				'accept': 'application/json',
				'Content-Type': 'application/x-www-form-urlencoded'
			}
			data = {
				'grant_type': '',
				'username': username,
				'password': password,
				'scope': '',
				'client_id': '',
				'client_secret': ''
			}

			response = requests.post(url, headers=headers, data=data)

			if response.status_code == 200:
				result = response.json()
				integrasiToken = result.get('access_token')
				print('Access Token:', integrasiToken)
				cursor.execute('''INSERT INTO akun VALUES ('%s','%s','%s','%s')''' %(username, password_hashed, patientId, integrasiToken))
				conn.commit()
			else:
				raise HTTPException(status_code=405, detail="username sudah dipakai")
		else:
			raise HTTPException(status_code=404, detail="username sudah ")
		return "user created successfully"
	else:
		raise HTTPException(status_code=403, detail="username sudah dipakai")

@app.get("/users/profile", tags =['pasien access'])
async def profile(user: User = Depends(get_curr_user)):
	temp=[]
	conn = get_conn()
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM pasien where pasienID = '%s'" %(user.patientId))
	temp=cursor.fetchone()
	return {
		"ID pasien":temp[0],
		"Nama pasien":temp[1],
		"riwayat penyakit":temp[2]
	}


@app.get('/all/hasiluji', tags =['admin access'])
async def read_all_hasilUji(user: User = Depends(get_curr_user)):
	if user.role == 'admin':
		rows=[]
		conn = get_conn()
		cursor = conn.cursor()
		cari = cursor.execute("SELECT * FROM hasilUji")
		for row in cursor.fetchall():
			rows.append({"ujiID":row.ujiID, "pasienID":row.pasienID, "hasil":row.hasilUji})
		return rows
	
	else:
		raise HTTPException(status_code=405, detail="unauthorized")

@app.get('/hasilUji', tags=['pasien access'])
async def read_all_hasil_test_pasien(user: User = Depends(get_curr_user)):
	if user.role == 'pasien':
		rows=[]
		conn = get_conn()
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM hasilUji where pasienID = %s"%(user.patientId))
		for row in cursor.fetchall():
			rows.append({"ujiID":row.ujiID, "pasienID":row.pasienID, "hasil":row.hasilUji})
		return rows
	else:
		raise HTTPException(status_code=405, detail="unauthorized")

@app.get('/all/akun', tags=['admin access'])
async def read_all_akun(user: User = Depends(get_curr_user)):
	if user.role == 'admin':
		rows=[]
		conn = get_conn()
		cursor = conn.cursor()
		cursor.execute("SELECT username, pass as password, pasienID FROM akun")
		for row in cursor.fetchall():
			rows.append({"username":row.username, "password":row.password, "pasienID":row.pasienID})
		return rows
	else:
		raise HTTPException(status_code=405, detail="unauthorized")
	
@app.get('/all/pasien', tags=['admin access'])
async def read_all_pasien(user: User = Depends(get_curr_user)):
	if user.role == 'admin':
		rows=[]
		conn = get_conn()
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM pasien")
		for row in cursor.fetchall():
			rows.append({"pasienID":row.pasienID, "nama pasien":row.pasienNama, "riwayat penyakit":row.riwayatPenyakit})
			
		return rows
	else:
		raise HTTPException(status_code=405, detail="unauthorized")

@app.delete('/pasien/{pasienID}', tags=['admin access'])
async def delete_pasien_data(pasienID: int,user: User = Depends(get_curr_user)):
	if user.role == 'admin':
		rows=[]
		conn = get_conn()
		cursor = conn.cursor()
		cursor.execute("SELECT count(*) as hasil FROM pasien where pasienID = %s" %(pasienID))
		for row in cursor.fetchall():
			rows.append(f"{row.hasil}")
		if rows[0]=='1':
			akun=[]
			hasil=[]
			cursor.execute("SELECT count(*) as hasil FROM akun where pasienID = %s" %(pasienID))
			for row in cursor.fetchall():
				akun.append(f"{row.hasil}")
			cursor.execute("SELECT count(*) as hasil FROM hasilUji akun where pasienID = %s" %(pasienID))
			for row in cursor.fetchall():
				hasil.append(f"{row.hasil}")
			if akun[0] == '1':
				cursor.execute("DELETE FROM akun WHERE pasienID = '%s'" %(pasienID))
				conn.commit()
			if hasil[0]!='0':
				cursor.execute("DELETE FROM hasilUji WHERE pasienID = %s" %(pasienID))
				conn.commit()
			cursor.execute("DELETE FROM pasien WHERE pasienID = %s" %(pasienID))
			conn.commit()
			return "data pasien dengan id %s berhasil dihapus" %(pasienID)
		else:
			return "tidak ada pasien dengan id %s" %(pasienID)
	else:
		raise HTTPException(status_code=405, detail="unauthorized")

@app.delete('/hasilUji/{ujiID}', tags=['admin access'])
async def delete_data_hasil_uji(ujiID: int,user: User = Depends(get_curr_user)):
	if user.role == 'admin':
		rows=[]
		conn = get_conn()
		cursor = conn.cursor()
		cursor.execute("SELECT count(*) as hasil FROM hasilUji where ujiID = %s" %(ujiID))
		for row in cursor.fetchall():
			rows.append(f"{row.hasil}")
		if rows[0]!='0':
			cursor.execute("DELETE FROM hasilUji WHERE ujiID = %s" %(ujiID))
			conn.commit()
			return "data hasil uji dengan id %s berhasil dihapus" %(ujiID)
		else:
			return "tidak ada hasil uji dengan id %s" %(ujiID)
	else:
		raise HTTPException(status_code=405, detail="unauthorized")

@app.delete('/akun/{pasienID}',tags=['admin access'])
async def delete_akun(pasienID: int,user: User = Depends(get_curr_user)):
	if user.role == 'admin':
		rows=[]
		conn = get_conn()
		cursor = conn.cursor()
		cursor.execute("SELECT count(*) as hasil FROM akun where pasienID = '%s'" %(pasienID))
		for row in cursor.fetchall():
			rows.append(f"{row.hasil}")
		if rows[0]=='1':
			hasil=[]
			cursor.execute("SELECT count(*) as hasil FROM hasilUji akun where pasienID = %s" %(pasienID))
			for row in cursor.fetchall():
				hasil.append(f"{row.hasil}")
			if hasil[0]!='0':
				cursor.execute("DELETE FROM hasilUji WHERE pasienID = %s" %(pasienID))
				conn.commit()
			cursor.execute("DELETE FROM akun WHERE pasienID = '%s'" %(pasienID))
			conn.commit()
			return "akun dengan pasienID %s berhasil dihapus" %(pasienID)
		else:
			return "tidak ada akun dengan pasienID %s" %(pasienID)
	else:
		raise HTTPException(status_code=405, detail="unauthorized")

@app.put('/riwayat/{pasienID}',tags=['admin access'])
async def update_riwayat_penyakit(riwayatPenyakit:str,pasienID: int,user: User = Depends(get_curr_user)):
	if user.role == 'admin':
		rows=[]
		conn = get_conn()
		cursor = conn.cursor()
		cursor.execute("SELECT count(*) as hasil FROM pasien where pasienID = '%s'" %(pasienID))
		for row in cursor.fetchall():
			rows.append(f"{row.hasil}")
		if rows[0]=='1':
			cursor.execute("UPDATE pasien SET riwayatPenyakit = '%s' WHERE pasienID = '%s'" %(riwayatPenyakit,pasienID))
			conn.commit()
			return "riwayat penyakit akun dengan pasienID %s berhasil diubah" %(pasienID)
		else:
			return "tidak ada akun dengan pasienID %s" %(pasienID)
	else:
		raise HTTPException(status_code=405, detail="unauthorized")
	
@app.put('/nama/{pasienID}', tags=['admin access'])
async def update_nama_pasien(nama:str,pasienID: int,user: User = Depends(get_curr_user)):
	if user.role == 'admin':
		rows=[]
		conn = get_conn()
		cursor = conn.cursor()
		cursor.execute("SELECT count(*) as hasil FROM pasien where pasienID = '%s'" %(pasienID))
		for row in cursor.fetchall():
			rows.append(f"{row.hasil}")
		if rows[0]=='1':
			cursor.execute("UPDATE pasien SET pasienNama = '%s' WHERE pasienID = '%s'" %(nama,pasienID))
			conn.commit()
			return "nama pasien akun dengan pasienID %s berhasil diubah" %(pasienID)
		else:
			return "tidak ada akun dengan pasienID %s" %(pasienID)
	else:
		raise HTTPException(status_code=405, detail="unauthorized")

@app.post('/predict',tags=['pasien access','admin access', 'hasil integrasi'])
async def check_disease(item: Item, user: User = Depends(get_curr_user)):
	dataset1 = pd.read_csv('MOCK_DATA (1).csv')
	X=dataset1[['TekananDarah', 'TinggiBadan', 'BeratBadan']]
	y=dataset1['Penyakit'] 
	X=X.values
	y=y.values
	svr = DecisionTreeRegressor()
	svr.fit(X,y)
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
	hasil = penyakit
	result=[]
	if hasil == 'sehat':
		longitude = gps_get_longitude()
		latitude = gps_get_latitude()
		url = f'https://hospicall.azurewebsites.net/emergency/'
		headers = {
			'accept' : 'application/json',
			'Content-Type' : 'application/x-www-form-urlencoded'
		}
		data ={
			'longitude' : longitude,
			'latitude' : latitude
		}
		response = requests.get(url,headers=headers, params=data)
		hasil = response.json()
		hasil_test_attribute = {"hasil test": {"hasil prediksi":penyakit, "tekanan darah" : item.bloodPressure, "tinggi badan":item.height, "berat badan":item.weight}}
		hasil.update(hasil_test_attribute)
		result.append(hasil)
	else:
		longitude = gps_get_longitude()
		latitude = gps_get_latitude()
		url = 'https://hospicall.azurewebsites.net/emergency/'
		headers = {
			'accept' : 'application/json',
			'Content-Type' : 'application/x-www-form-urlencoded'
		}
		data ={
			'longitude' : longitude,
			'latitude' : latitude
		}
		response = requests.post(url,headers=headers, params=data)
		
		hasil = response.json()
		hasil_test_attribute = {"hasil test": {"hasil prediksi":penyakit, "tekanan darah" : item.bloodPressure, "tinggi badan":item.height, "berat badan":item.weight}}
		hasil.append(hasil_test_attribute)
		result.append(hasil)

	if user.role=='admin':
		return result
	else:
		conn = get_conn()
		cursor = conn.cursor()
		rows=[]
		cursor.execute('''SELECT ujiID FROM hasilUji ORDER BY ujiID DESC''')
		for row in cursor.fetchall():
			rows.append(f"{row.ujiID+1}")
		
		else:
			id = user.patientId
		cursor.execute('''INSERT INTO hasilUji (ujiID,pasienID,hasilUji) VALUES ('%s','%s','%s')''' %(rows[0],id,penyakit))
		conn.commit()
		return result
	

@app.get("/{facility_id}", tags = ['hasil integrasi'])
async def get_health_facility_by_id(facility_id: str, user: User = Depends(get_curr_user)):
	url = f'https://hospicall.azurewebsites.net/healthcare/{facility_id}'
	headers = {
		'accept' : 'application/json',
		'Authorization' : 'bearer '+user.integrasiToken,
		'Content-Type' : 'application/x-www-form-urlencoded'
	}
	data ={
		'facility_id' : facility_id
	}
	response = requests.get(url,headers=headers, params=data)
	if response.status_code == 200:
		data=response.json()
		return data
	else:
		raise HTTPException(status_code=405, detail=print(user.integrasiToken))



