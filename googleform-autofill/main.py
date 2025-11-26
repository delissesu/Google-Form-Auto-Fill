import requests
import json
import random
import re
import datetime
import kagglehub
import os
import glob
import time

# ini link gform nya
url_gform = "https://docs.google.com/forms/d/e/1FAIpQLScyVWGpabtrQKANc58eqk_gOJLzDkMLTW3Vt5rtRyqk-LPE0w/viewform"

# fungsi buat minta nama dari dataset kaggle
def ambil_nama_dari_kaggle():
    try:
        # Download latest version
        print("Lagi download dataset nama indo dari kaggle...")
        path = kagglehub.dataset_download("dionisiusdh/indonesian-names")
        print("Dataset ada di:", path)
        
        # cari file csv di folder itu
        # pake glob biar gampang nyarinya
        list_file = glob.glob(os.path.join(path, "*.csv"))
        
        if list_file:
            nama_file = list_file[0]
            print("Pake file:", nama_file)
            
            # baca file csv nya manual aja biar ga ribet install pandas
            file = open(nama_file, "r")
            baris = file.readlines()
            file.close()
            
            # pilih satu baris acak (skip baris pertama judul)
            pilihan = random.choice(baris[1:])
            
            # isinya biasanya: nama,gender atau semacamnya
            # kita ambil yang paling depan aja (sebelum koma)
            data = pilihan.split(",")
            nama = data[0]
            
            # bersihin nama
            nama = nama.strip().title()
            # kadang ada tanda kutipnya, buang aja
            nama = nama.replace('"', '').replace("'", "")
            
            print("Dapet nama dari kaggle: " + nama)
            return nama
        else:
            print("Waduh ga nemu file csv nya di folder itu.")
            return "Budi Santoso"

    except Exception as e:
        print("Gagal ambil dari kaggle: " + str(e))
        return "Budi Santoso" # kalo error tetep budi andalan gue

# fungsi buat ngambil data dari gform
def ambil_data_form(url):
    # ganti url jadi formResponse biar bisa disubmit
    url_response = url.replace('/viewform', '/formResponse')
    
    # request ke google
    print("Lagi ngambil data dari: " + url)
    r = requests.get(url)
    
    # cari variabel FB_PUBLIC_LOAD_DATA_ di html nya
    # ini isinya data2 pertanyaan gform
    # pake regex yang agak ribet biar kena semua
    data_mentah = re.search(r'var FB_PUBLIC_LOAD_DATA_ = (\[[\s\S]*?\]);', r.text)
    
    if data_mentah:
        # kalo ketemu, di load jadi json
        data_json = json.loads(data_mentah.group(1))
        return data_json, url_response
    else:
        print("Waduh, ga nemu datanya. Coba cek link nya lagi.")
        return None, None

# fungsi buat ngisi data acak
def isi_data_acak(data_form):
    data_buat_dikirim = {}
    
    # ambil nama dulu
    nama_orang = ambil_nama_dari_kaggle()
    
    # loop semua pertanyaan di form
    # data_form[1][1] itu isinya list pertanyaan
    for pertanyaan in data_form[1][1]:
        # ambil id pertanyaan
        id_pertanyaan = pertanyaan[4][0][0]
        id_pertanyaan_str = str(id_pertanyaan)
        
        # ambil tipe pertanyaan (text, pilihan ganda, dll)
        tipe = pertanyaan[3]
        
        # ambil pilihan jawaban kalo ada (misal pilihan ganda)
        pilihan = []
        if pertanyaan[4][0][1]:
            for p in pertanyaan[4][0][1]:
                pilihan.append(p[0])
        
        # Nama Inisial (ID: 1884265043)
        if id_pertanyaan_str == '1884265043':
            # pake nama yang tadi diambil dari web
            data_buat_dikirim["entry." + id_pertanyaan_str] = nama_orang
            
        # 2. Jenis Kelamin (ID: 1212348438)
        elif id_pertanyaan_str == '1212348438':
            # pilih acak cowo atau cewe
            yang_dipilih = random.choice(['Laki - Laki', 'Perempuan'])
            data_buat_dikirim["entry." + id_pertanyaan_str] = yang_dipilih
            # simpen dulu buat nentuin tinggi badan ntar
            global gender_tadi
            gender_tadi = yang_dipilih

        # 3. Tinggi Badan (ID: 513669972)
        elif id_pertanyaan_str == '513669972':
            # tinggi badan acak aja lah 160 sampe 175
            tinggi = random.randint(160, 175)
            data_buat_dikirim["entry." + id_pertanyaan_str] = str(tinggi)
            # simpen buat itung berat badan
            global tinggi_tadi
            tinggi_tadi = tinggi

        # 4. Berat Badan (ID: 815861936)
        elif id_pertanyaan_str == '815861936':
            # itung berat biar ideal (BMI normal)
            # rumusnya: berat = BMI * (tinggi meter kuadrat)
            tinggi_meter = tinggi_tadi / 100
            bmi_acak = random.uniform(18.5, 24.9)
            berat = bmi_acak * (tinggi_meter * tinggi_meter)
            berat_jadi = int(berat) # jadiin angka bulet
            data_buat_dikirim["entry." + id_pertanyaan_str] = str(berat_jadi)
            
        # Kalo ada pertanyaan lain yg ga kita kenal, isi ngasal aja
        else:
            if tipe == 0 or tipe == 1: # isian teks
                data_buat_dikirim["entry." + id_pertanyaan_str] = "Isi ngasal"
            elif tipe == 2 or tipe == 3: # pilihan ganda / dropdown
                if pilihan:
                    data_buat_dikirim["entry." + id_pertanyaan_str] = random.choice(pilihan)
            elif tipe == 4: # checkbox
                if pilihan:
                    data_buat_dikirim["entry." + id_pertanyaan_str] = random.choice(pilihan)

    return data_buat_dikirim


# Ambil data form
data_form, url_submit = ambil_data_form(url_gform)

if data_form and url_submit:
    tambah_data = int(input("Mau nambahin berapa orang?: "))
    target = int(input("Target orangnya harusnya berapa?: ")) - tambah_data
    print("Berarti kurang " + str(target) + " lagi nih.")
    try:
        jumlah = int(input("Mau ngisi berapa orang? (Saran: " + str(target) + "): "))
    except:
        print("Yah, bukan angka ya. Yaudah deh, masukin satu aja.")
        jumlah = 1

    print("Isi" + str(jumlah) + " kali!")
    
    for i in range(jumlah):
        print("\nIsi data ke-" + str(i+1))
        
        # Bikin data jawaban
        jawaban = isi_data_acak(data_form)
        
        print("Data yang mau dikirim:")
        print(jawaban)
        
        # Kirim ke google (Submit)
        try:
            kirim = requests.post(url_submit, data=jawaban)
            
            if kirim.status_code == 200:
                print("Mantap! Berhasil ke kirim cuy.")
            else:
                print("Yah gagal. Error code: " + str(kirim.status_code))
                
        except Exception as e:
            print("Ada error pas ngirim: " + str(e))
        
        # Delay acak 2-3 menit biar ga keliatan kayak bot
        # Kecuali kalo udah yang terakhir, ga usah delay
        if i < jumlah - 1:
            delay_detik = random.randint(120, 180)  # 2-3 menit dalam detik
            menit = delay_detik // 60
            detik = delay_detik % 60
            print(f"Nunggu dulu {menit} menit {detik} detik biar ga dicurigai...")
            time.sleep(delay_detik)
            
    print("\nSelesai bos! Udah dikirim semua.")

else:
    print("Gagal ambil data form, coba cek koneksi atau link nya.")
