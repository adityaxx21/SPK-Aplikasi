from django.http.request import split_domain_port
from django.shortcuts import render
from numpy.core.defchararray import array
from numpy.lib.function_base import insert
from pandas.core.frame import DataFrame
import pandas as pd
import numpy as np
import sys
import json
import random
import datetime
import pandas as pd
import sqlite3


from django.contrib.staticfiles.storage import staticfiles_storage
# Pemanggilan data

# Normalisasi


def norm_AHP(P):
    norAHP = np.zeros([len(P), len(P[0])])
    for i in range(len(P)):
        for j in range(len(P[0])):
            norAHP[i][j] = P[i][j]/sum(P[i])
    return(norAHP)

# Bobot Kriteria


def weight_crit(P, norAHP):
    wAHP = np.zeros(len(P))
    for i in range(len(P)):
        count = 0
        for j in range(len(P[0])):
            count += norAHP[j][i]
        wAHP[i] = count/6
    return(wAHP)

# LambdaAX


def lamb_AX(P, wAHP):
    lAX = np.zeros(len(P))
    for i in range(len(P)):
        count = 0
        for j in range(len(P[0])):
            count += P[j][i] * wAHP[j]
        lAX[i] = count
    lamb_Max(P, wAHP, lAX)
    return(lAX)

# lMax


def lamb_Max(P, wAHP, lAX):
    lMax = 0
    for i in range(len(P)):
        lMax += lAX[i]/wAHP[i]
    lMax = lMax/len(P)
    return(lMax)

    #  CI


def CI_CR(lMax, P):
    CI = (lMax-len(P))/(len(P)-1)
    # Consitensy Ratio
    CR = CI / 1.24
    return(CR)

# Seleksi AHP


def Criteria(dataset_new):
    Criteria_AHP = []
    for k in range(len(dataset_new)):
        data_test1 = []
#         print("")
#         print("Kriteria K-",k+1)
        for i in range(len(dataset_new[0])):
            data_test = []
            for j in range(len(dataset_new[0])):
                data_test.append(dataset_new[k][j]/dataset_new[k][i])
            data_test1.append(data_test)
        Criteria_AHP.append(data_test1)
#         print(np.transpose(data_test1))
    return(Criteria_AHP)

# Normalisasi AHP


def Norm_AHP(Criteria_AHP):
    Norm_AHP = np.copy(Criteria_AHP)
    Bobot = []
#
    for i in range(len(Criteria_AHP)):
        for j in range(len(Criteria_AHP[0])):
            for k in range(len(Criteria_AHP[0])):
                count = np.sum(Criteria_AHP[i][j])
                Norm_AHP[i][j][k] = Norm_AHP[i][j][k]/count
        Norm_AHP[i] = np.transpose(Norm_AHP[i])

    for i in range(len(Criteria_AHP)):
        Count = []
        for j in range(len(Criteria_AHP[0])):
            Count.append(np.average(Norm_AHP[i][j]))
        Bobot.append(Count)
    return Bobot

# Scoring AHP


def rank(Bobot, Bobot_Alt):
    Score = np.zeros(len(Bobot_Alt[0]))
#     print("Score :")
#     print(Bobot)
    for i in range(len(Bobot_Alt[0])):
        Count = 0
        for j in range(len(Bobot)):
            Count1 = Bobot_Alt[j][i]*Bobot[j]
            Count += Count1
        Score[i] = Count
    accur = Score[0]
    Score = np.delete(Score, 0, 0)
#     for i in Score :
#         print(round(i,10))
    return(Score, accur)
# Normalisasi TOPSIS


def norm_TOPSIS(dataset_new):
    norTOPSIS = np.zeros([len(dataset_new), len(dataset_new[0])])
    for i in range(len(dataset_new)):
        for j in range(len(dataset_new[0])):
            norTOPSIS[i][j] = dataset_new[i][j]/np.sqrt(sum(dataset_new[i]**2))
    return(norTOPSIS)

# Normalisasi TOPSIS * BOBOT AHP


def norm_AHPxTOPSIS(dataset_new, norTOPSIS, wAHP):
    zTopsis = np.zeros([len(norTOPSIS), len(norTOPSIS[0])])
    for i in range(len(dataset_new)):
        for j in range(len(dataset_new[0])):
            zTopsis[i][j] = norTOPSIS[i][j]*wAHP[i]
    return(zTopsis)


# Solusi Positif Negatif
def SPM(dataset_new, zTopsis):
    Spm = np.zeros([2, len(dataset_new)])
    for i in range(len(Spm)):
        for j in range(len(Spm[0])):
            if i == 0:
                Spm[i][j] = max(zTopsis[j])
            else:
                Spm[i][j] = min(zTopsis[j])
    return(Spm)


def Dpos_neg(dataset_new, zTopsis, Spm):
    # Perhitungan D+
    print("")
    print("Perhitungan D+")
    Dp = np.zeros(len(dataset_new[0]))
    for j in range(len(Dp)):
        count = 0
        for i in range(len(dataset_new)):
            count += (zTopsis[i][j] - Spm[0][i])**2
        Dp[j] = np.sqrt(count)

    # Perhitungan D-
    print("")
    print("Perhitungan D-")
    Dn = np.zeros(len(dataset_new[0]))
    for j in range(len(Dn)):
        count = 0
        for i in range(len(dataset_new)):
            count += (zTopsis[i][j] - Spm[1][i])**2
        Dn[j] = np.sqrt(count)
#         print(Dn[j])
    return(Dp, Dn)

# Perhitungan C


def res_C(dataset_new, Dn, Dp):
    print("")
    C = np.zeros(len(dataset_new[0]))
    for i in range(len(C)):
        C[i] = Dn[i] / (Dp[i]+Dn[i])
    accur = C[0]
    C = np.delete(C, 0, 0)
    return(C, accur)

# Hasil Akhir


def result(dataset, data_a, C):
    np.set_printoptions(precision=3, suppress=True, threshold=sys.maxsize)
    data_b = dataset[(dataset['Id'] == data_a[0][0])]
    for i in range(1, len(data_a[0])):
        data_b = data_b.append(dataset[(dataset['Id'] == data_a[0][i])])
    data_b['Score'] = C
    data_b = data_b.sort_values(by=['Score'], ascending=True)
    return(data_b)


def accurate(data_b, dataset, accur):
    sortr = pd.DataFrame()
    sortr = sortr.append(data_b[(data_b['Score'] >= accur)])
    accuration = len(sortr['Id'])/len(dataset['Id'])*100
    return(accuration, sortr)


def rest(request):
    return render(request, 'rest.html')

def dataset_import():
    # Read sqlite query results into a pandas DataFrame
    seleksi1 = pd.read_excel(
            "https://github.com/adityaxx21/polosbae/raw/master/dataset.xlsx", sheet_name='seleksi')
        # seleksi diambil dari excel dataset.xlsx pada sheet dataset, data ini berisi seluruh laptop yang tersedia
    dataset1 = pd.read_excel(
            "https://github.com/adityaxx21/polosbae/raw/master/dataset.xlsx", sheet_name='dataset')
    con = sqlite3.connect(r"./data.sqlite")
    dataset = pd.read_sql_query("SELECT * from dataset", con)
    seleksi = pd.read_sql_query("SELECT * from seleksi", con)

    # Verify that result of SQL query is stored in the dataframe
    con.close()
    return(dataset,seleksi)


def index(request):
    if request.method == 'POST':
        dataset,seleksi2 = dataset_import()
        seleksi2 = seleksi2.replace(np.nan, "", regex=True)

        # seleksi2 = pd.read_excel(
        #     r'C:\Users\Prozire\OneDrive\Python\SPK_Aplikasi\dataset.xlsx', sheet_name='seleksi')
        # seleksi2 = seleksi2.replace(np.nan, "", regex=True)
        # dataset = pd.read_excel(
        #     r'C:\Users\Prozire\OneDrive\Python\SPK_Aplikasi\dataset.xlsx', sheet_name='dataset')
        np.set_printoptions(precision=10, suppress=True, threshold=sys.maxsize)
        
        cpu = float(request.POST["cpu"])
        gpu = float(request.POST["gpu"])
        ram = float(request.POST["ram"])
        disp = float(request.POST["disp"])
        store = float(request.POST["store"])
        price = float(request.POST["price"])
        if cpu == 0 :
            cpu = 100
        if gpu == 0 :
            gpu = 148
        if disp == 0 :
            disp = 35
        if store == 0 :
            store = 768
        if ram == 0 :
            ram = 8
        if price == 0 :
            price = 5700000        
        input_usr = [
            # # Proccessor 0: untuk default, 1-11 : sesuai kriteria
            # float(request.POST["cpu"]),
            # # Graphic 0: untuk default, 1-6 : sesuai kriteria
            # float(request.POST["gpu"]),
            # # Display 0: untuk default, 1-11 : sesuai kriteria
            # float(request.POST["disp"]),
            # # Ram 0: untuk default, 1-9 : sesuai kriteria
            # float(request.POST["ram"]),
            # # Storage 0: untuk default, 1-11 : sesuai kriteria
            # float(request.POST["store"]),
            # # Rentan harga untuk dibawah angka
            # float(request.POST["price"]),
            cpu,gpu,disp,ram,store,price
             ]
        # if (input_usr.count(0) > 1):
        #     input_usr = [100, 148, 35, 8, 768, 5700000]

        input_usr.insert(0, 40001)
        label = ["Id", "Score CPU", "Score GPU", "Score Display",
                 "Score Ram", "Score Storage", "Score Price"]
        data_a = dataset[['Id', 'scr_cpu', 'scr_gpu',
                          'scr_dis', 'scr_ram', 'scr_str', 'harga_baru']]
        data_a = np.transpose(data_a.to_numpy())
        data_a = np.insert(data_a, [0], [[input_usr[0]], [input_usr[1]], [input_usr[2]], [
                           input_usr[3]], [input_usr[4]], [input_usr[5]], [input_usr[6]]], axis=1)
        dataset_new = np.delete(data_a, 0, axis=0)


        count = 1
        P = np.zeros((6, 6))
        for i in range(6):
            for j in range(i, 6):
                if i == j:
                    P[i][j] = 1
                else:
                    count = count+1
                    P[i][j] = float(request.POST['P'+str(count)])
                    P[j][i] = float(request.POST['P'+str(count)]) / \
                        float(request.POST['P'+str(count)])**2
            # P = np.transpose(P)
        print(P)

        CR = 100
        while CR > 0.1 or CR == 0:
            # Normalisasi
            norAHP = norm_AHP(P)
            # Bobot Kriteria
            wAHP = weight_crit(P, norAHP)
        # LambdaAX
            lAX = lamb_AX(P, wAHP)

        # lMax
            lMax = lamb_Max(P, wAHP, lAX)

            # Consistensy Index

        # Seleksi hasil CI

            # Consitensy Ratio
            CR = CI_CR(lMax, P)
            print(CR)
            if CR > 0.1 or CR == 0:
                # Kriteria tingkat kepentingan
                # arraya = np.zeros((6,6))
                # for i in range(6):
                #     for j in range(6):
                #         a = random.randint(0, 1)
                #         if a == 1 :
                #             a=round(1/random.randint(1,9),4)
                #         else :
                #             a=random.randint(1,9)
                #         arraya[i,j] = a
                #         arraya[j,i] = 1/a
                #     arraya[i,i] = 1
                # P = np.copy(arraya)
                P = [[1, 0.5, 0.333333333, 0.333333333, 0.5, 0.25, ],
                [2, 1, 2, 0.5, 0.333333333, 1],
                [3, 0.25, 1, 0.333333333, 0.333333333, 0.5],
                [3, 2, 3, 1, 0.5, 4],
                [2, 3, 3, 2, 1, 4],
                [4, 1, 2, 0.25, 0.25, 1]]
                # P = [[1.0,	1.0,	4.0,	6.0	, 1.0,	9.0],
                #      [1.0	, 1.0,	2.0	, 3.0,	0.2	, 3.0],
                #      [0.25	, 0.5	, 1.0	, 4.0	, 0.2	, 6.0],
                #      [0.17	, 0.33,	0.25	, 1.0,	0.11,	1.0],
                #      [1.0	, 5.0	, 5.0	, 9.0	, 1.0	, 7.0],
                #      [0.11	, 0.33	, 0.17	, 1.0	, 0.14	, 1.0]]

    # Normalisasi TOPSIS
        norTOPSIS = norm_TOPSIS(dataset_new)
    # Normalisasi TOPSIS * BOBOT AHP
        zTopsis = norm_AHPxTOPSIS(dataset_new, norTOPSIS, wAHP)

    # Solusi Positif Negatif Positif
        Spm = SPM(dataset_new, zTopsis)
        Dp, Dn = Dpos_neg(dataset_new, zTopsis, Spm)
    # Perhitungan C
        C, accur = res_C(dataset_new, Dn, Dp)

        # Hasil Akhir
        np.set_printoptions(precision=3, suppress=True, threshold=sys.maxsize)
        data_b = result(dataset, data_a, C)
        
        sortr = pd.DataFrame()
        sortr = sortr.append(data_b[(data_b['Score'] >= accur)])
        accuration = len(sortr['Id'])/len(dataset['Id'])*100

        json_records = sortr.reset_index().to_json(orient='records')
        data = []
        data = json.loads(json_records)

        json_records = seleksi2.reset_index().to_json(orient='records')
        data1 = []
        data1 = json.loads(json_records)
        return render(request, 'index.html', {
            'norAHP': norAHP,
            'wAHP': wAHP,
            'lAX': lAX,
            'lMax': lMax,
            'CR': CR,
            'norTOPSIS': np.transpose(norTOPSIS),
            'zTopsis': np.transpose(zTopsis),
            'Dp': Dp,
            'Dn': Dn,
            'C': C,
            'data_b': data_b,
            'sortr': data,
            'Spm': Spm,
            'P': np.round(P, 2),
            'accuration': round(accuration, 2),
            'lent': len(sortr['Id']),
            'seleksi2': data1,
            'inpt_usr': input_usr,
            'label': label,
        })

    else:
        return render(request, 'index.html', {'uji': 'uji', })

# Pengujian Jumlah Data


def index1(request):
    x = []
    y = []
    # Panjang data lolos
    lent = []
    # Akurasi
    acc = []
    # Kecepatan Kompilasi
    time = []

    loopeng = []
    for i in range(1, 8):
        are = []
        begin_time = datetime.datetime.now()
        # Pemanggilan data
        # seleksi diambil dari excel dataset.xlsx pada sheet seleksi, data ini berisi kriteria yang bisa dipilih user
        dataset,seleksi = dataset_import()
        dataset = dataset.head(i*100)
        np.set_printoptions(precision=10, suppress=True, threshold=sys.maxsize)
        seleksi = seleksi.replace(np.nan, "", regex=True)
        # Kriteria
        input_usr = [
            # Proccessor 0: untuk default, 1-11 : sesuai kriteria
            100,
            # Graphic 0: untuk default, 1-6 : sesuai kriteria
            148,
            # Display 0: untuk default, 1-11 : sesuai kriteria
            35,
            # Ram 0: untuk default, 1-9 : sesuai kriteria
            8,
            # Storage 0: untuk default, 1-11 : sesuai kriteria
            768,
            # Rentan harga untuk dibawah angka
            5700000]

        input_usr.insert(0, 40001)
        data_a = dataset[['Id', 'scr_cpu', 'scr_gpu',
                          'scr_dis', 'scr_ram', 'scr_str', 'harga_baru']]
        data_a = np.transpose(data_a.to_numpy())
        data_a = np.insert(data_a, [0], [[input_usr[0]], [input_usr[1]], [input_usr[2]], [
                           input_usr[3]], [input_usr[4]], [input_usr[5]], [input_usr[6]]], axis=1)
        dataset_new = np.delete(data_a, 0, axis=0)
        # P = [[1.0,	1.0,	4.0,	6.0	, 1.0,	9.0],
        #              [1.0	, 1.0,	2.0	, 3.0,	0.2	, 3.0],
        #              [0.25	, 0.5	, 1.0	, 4.0	, 0.2	, 6.0],
        #              [0.17	, 0.33,	0.25	, 1.0,	0.11,	1.0],
        #              [1.0	, 5.0	, 5.0	, 9.0	, 1.0	, 7.0],
        #              [0.11	, 0.33	, 0.17	, 1.0	, 0.14	, 1.0]]
        P = [[1, 0.5, 0.333333333, 0.333333333, 0.5, 0.25, ],
             [2, 1, 2, 0.5, 0.333333333, 1],
             [3, 0.25, 1, 0.333333333, 0.333333333, 0.5],
             [3, 2, 3, 1, 0.5, 4],
             [2, 3, 3, 2, 1, 4],
             [4, 1, 2, 0.25, 0.25, 1]]
        norAHP = norm_AHP(P)
        wAHP = weight_crit(P, norAHP)
        lAX = lamb_AX(P, wAHP)
        lMax = lamb_Max(P, wAHP, lAX)
        CR = CI_CR(lMax, P)

        # Proses Pengitungan
        norTOPSIS = norm_TOPSIS(dataset_new)
        zTopsis = norm_AHPxTOPSIS(dataset_new, norTOPSIS, wAHP)
        Spm = SPM(dataset_new, zTopsis)
        Dp, Dn = Dpos_neg(dataset_new, zTopsis, Spm)
        C, accur = res_C(dataset_new, Dn, Dp)
        datab = result(dataset, data_a, C)
        # Akurasi
        sortr = pd.DataFrame()
        sortr = sortr.append(datab[(datab['Score'] >= accur)])

        accuration = len(sortr['Id'])/len(dataset['Id'])*100

        y.append(round(float(accuration), 3))
        are.append(len(sortr))
        are.append(round((accuration), 3))
        are.append(datetime.datetime.now() - begin_time)

        loopeng.append(are)
    y.append(0)
    return render(request, 'index1.html', {
        'loopeng': loopeng,
        'y': y,
    })

# Pengujian Kriteria Berpasangan


def index2(request):
    y = []
    loopeng = []
    for i in range(1, 8):
        are = []
        begin_time = datetime.datetime.now()
        # Pemanggilan data
        # seleksi diambil dari excel dataset.xlsx pada sheet seleksi, data ini berisi kriteria yang bisa dipilih user
        dataset,seleksi = dataset_import()
        np.set_printoptions(precision=10, suppress=True, threshold=sys.maxsize)
        seleksi = seleksi.replace(np.nan, "", regex=True)

        # Kriteria
        input_usr = [
            # Proccessor 0: untuk default, 1-11 : sesuai kriteria
            100,
            # Graphic 0: untuk default, 1-6 : sesuai kriteria
            148,
            # Display 0: untuk default, 1-11 : sesuai kriteria
            35,
            # Ram 0: untuk default, 1-9 : sesuai kriteria
            8,
            # Storage 0: untuk default, 1-11 : sesuai kriteria
            768,
            # Rentan harga untuk dibawah angka
            5700000]

        input_usr.insert(0, 40001)
        data_a = dataset[['Id', 'scr_cpu', 'scr_gpu',
                          'scr_dis', 'scr_ram', 'scr_str', 'harga_baru']]
        data_a = np.transpose(data_a.to_numpy())
        data_a = np.insert(data_a, [0], [[input_usr[0]], [input_usr[1]], [input_usr[2]], [
                           input_usr[3]], [input_usr[4]], [input_usr[5]], [input_usr[6]]], axis=1)
        dataset_new = np.delete(data_a, 0, axis=0)

        CR = 100
        while (CR > 0.1 or CR == 0):

            arraya = np.zeros((6, 6))
            for j in range(6):
                for k in range(6):
                    a = random.randint(0, 1)
                    if a == 1:
                        a = round(1/random.randint(1, 9), 4)
                    else:
                        a = random.randint(1, 9)
                    arraya[j, k] = a
                    arraya[k, j] = 1/a
                arraya[j, j] = 1
            P = np.copy(arraya)
            norAHP = norm_AHP(P)
            wAHP = weight_crit(P, norAHP)
            lAX = lamb_AX(P, wAHP)
            lMax = lamb_Max(P, wAHP, lAX)
            CR = CI_CR(lMax, P)

        # Proses Pengitungan
        norTOPSIS = norm_TOPSIS(dataset_new)
        zTopsis = norm_AHPxTOPSIS(dataset_new, norTOPSIS, wAHP)
        Spm = SPM(dataset_new, zTopsis)
        Dp, Dn = Dpos_neg(dataset_new, zTopsis, Spm)
        C, accur = res_C(dataset_new, Dn, Dp)
        datab = result(dataset, data_a, C)
        # Akurasi
        sortr = pd.DataFrame()
        sortr = sortr.append(datab[(datab['Score'] >= accur)])

        accuration = len(sortr['Id'])/len(dataset['Id'])*100

        y.append(round(float(accuration), 3))
        are.append(np.round(P, 2))
        are.append(len(sortr))
        are.append(round((accuration), 3))
        are.append(datetime.datetime.now() - begin_time)
        loopeng.append(are)
    y.append(0)
    return render(request, 'index2.html', {
        'loopeng': loopeng,
        'y': y,
    })

# Pengujian Metode AHP


def index3(request):
    y = []
    loopeng = []
    for i in range(1, 8):
        are = []
        begin_time = datetime.datetime.now()
        # Pemanggilan data
        # seleksi diambil dari excel dataset.xlsx pada sheet seleksi, data ini berisi kriteria yang bisa dipilih user
        dataset,seleksi = dataset_import()
        dataset = dataset.head(i*100)
        np.set_printoptions(precision=10, suppress=True, threshold=sys.maxsize)
        seleksi = seleksi.replace(np.nan, "", regex=True)
        # Kriteria
        input_usr = [
            # Proccessor 0: untuk default, 1-11 : sesuai kriteria
            100,
            # Graphic 0: untuk default, 1-6 : sesuai kriteria
            148,
            # Display 0: untuk default, 1-11 : sesuai kriteria
            35,
            # Ram 0: untuk default, 1-9 : sesuai kriteria
            8,
            # Storage 0: untuk default, 1-11 : sesuai kriteria
            768,
            # Rentan harga untuk dibawah angka
            5700000]

        input_usr.insert(0, 40001)
        data_a = dataset[['Id', 'scr_cpu', 'scr_gpu',
                          'scr_dis', 'scr_ram', 'scr_str', 'harga_baru']]
        data_a = np.transpose(data_a.to_numpy())
        data_a = np.insert(data_a, [0], [[input_usr[0]], [input_usr[1]], [input_usr[2]], [
                           input_usr[3]], [input_usr[4]], [input_usr[5]], [input_usr[6]]], axis=1)
        dataset_new = np.delete(data_a, 0, axis=0)

        P = [[1, 0.5, 0.333333333, 0.333333333, 0.5, 0.25, ],
             [2, 1, 2, 0.5, 0.333333333, 1],
             [3, 0.25, 1, 0.333333333, 0.333333333, 0.5],
             [3, 2, 3, 1, 0.5, 4],
             [2, 3, 3, 2, 1, 4],
             [4, 1, 2, 0.25, 0.25, 1]]
        # P = [[1.0,	1.0,	4.0,	6.0	, 1.0,	9.0],
        #              [1.0	, 1.0,	2.0	, 3.0,	0.2	, 3.0],
        #              [0.25	, 0.5	, 1.0	, 4.0	, 0.2	, 6.0],
        #              [0.17	, 0.33,	0.25	, 1.0,	0.11,	1.0],
        #              [1.0	, 5.0	, 5.0	, 9.0	, 1.0	, 7.0],
        #              [0.11	, 0.33	, 0.17	, 1.0	, 0.14	, 1.0]]
        norAHP = norm_AHP(P)
        wAHP = weight_crit(P, norAHP)
        lAX = lamb_AX(P, wAHP)
        lMax = lamb_Max(P, wAHP, lAX)
        CR = CI_CR(lMax, P)

        # Proses Pengitungan
        Criteria_AHP = Criteria(dataset_new)
        Bobot_Alt = Norm_AHP(Criteria_AHP)
        C, accur = rank(wAHP, Bobot_Alt)
        datab = result(dataset, data_a, C)
        # Akurasi
        sortr = pd.DataFrame()
        sortr = sortr.append(datab[(datab['Score'] >= accur)])

        accuration = len(sortr['Id'])/len(dataset['Id'])*100

        y.append(round(float(accuration), 3))
        are.append(len(sortr))
        are.append(round((accuration), 3))
        are.append(datetime.datetime.now() - begin_time)

        loopeng.append(are)
    y.append(0)
    return render(request, 'index3.html', {
        'loopeng': loopeng,
        'y': y,
    })
