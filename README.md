# TubesTST
API ini digunakan untuk sebuah healthcare, salah satu fungsinya adalah melakukan prediksi penyakit tekanan darah dari pengguna.




list command

get('/all')
- memberikan seluruh hasil test kesehatan yang ada

post('/predict')
- memberikan hasil prediksi penyakit dengan input application/jason
  contoh body
  {
  "idPasien": 1,"idDokter":1,
  "bloodPressure": 199,
  "weight":50, "height":160
  }


  untuk saat ini hanya tersedia pasien dengan id=1 dan id=2
