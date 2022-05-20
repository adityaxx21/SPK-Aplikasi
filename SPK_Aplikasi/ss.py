def index1(request):
    x = []
    y = []
    cun = 0
    for i in range (7,8) :
        seleksi2 = pd.read_excel(r'C:\Users\Prozire\OneDrive\Python\Ipymb\dataset(AutoRecovered)-Copy.xlsx', sheet_name='seleksi')
        seleksi2 = seleksi2.replace(np.nan, "", regex=True)
        dataset = pd.read_excel(r'C:\Users\Prozire\OneDrive\Python\Ipymb\dataset(AutoRecovered)-Copy.xlsx', sheet_name='Sheet1')
        dataset = dataset.head(100*i+34)
        np.set_printoptions(precision=3, suppress=True, threshold=sys.maxsize)
        input_usr = [100, 148, 35, 8, 768, 5700000]
        input_usr.insert(0, 40001)
        label = ["Id", "Score CPU", "Score GPU", "Score Display","Score Ram", "Score Storage", "Score Price"]
        data_a = dataset[['Id', 'scr_cpu', 'scr_gpu','scr_dis', 'scr_ram', 'scr_str', 'harga_baru']]
        data_a = np.transpose(data_a.to_numpy())
        data_a = np.insert(data_a, [0], [[input_usr[0]], [input_usr[1]], [input_usr[2]], [input_usr[3]], [input_usr[4]], [input_usr[5]], [input_usr[6]]], axis=1)
        dataset_new = np.delete(data_a, 0, axis=0)

        count = 1
        P = np.zeros((6, 6))
        # for i in range(6):
        #     for j in range(i, 6):
        #         if i == j:
        #             P[i][j] = 1
        #         else:
        #             count = count+1
        #             P[i][j] = float(request.POST['P'+str(count)])
        #             P[j][i] = float(request.POST['P'+str(count)]) / float(request.POST['P'+str(count)])**2

        P = [[1,    0.333, 1,  8,   6.998, 3],
            [3,   1,  2,   9.001, 5.999, 4],
            [1, 0.5,  1, 3,  9.001, 1],
            [0.125, 0.111, 0.333, 1, 1, 0.143],
            [0.143, 0.167, 0.111, 1,  1,  0.167],
            [0.333, 0.25, 1,   7,   6,   1]]
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
            # Seleksi hasil CI
            CI = (lMax-len(P))/(len(P)-1)
            # Consitensy Ratio
            CR = CI / 1.24
            if CR > 0.1 or CR == 0:
                # Kriteria tingkat kepentingan
                arraya = np.zeros((6, 6))
                for i in range(6):
                    for j in range(6):
                        a = random.randint(0, 1)
                        if a == 1:
                            a = round(1/random.randint(1, 9), 4)
                        else:
                            a = random.randint(1, 9)
                        arraya[i, j] = a
                        arraya[j, i] = 1/a
                    arraya[i, i] = 1
                P = np.transpose(P)
                P = np.copy(arraya)
        # Normalisasi TOPSIS
        norTOPSIS = norm_TOPSIS(dataset_new)
        # Normalisasi TOPSIS * BOBOT AHP
        zTopsis = norm_AHPxTOPSIS(dataset_new, norTOPSIS, wAHP)
        # Solusi Positif Negatif
        Spm = SPM(dataset_new, zTopsis)
        #     Perhitungan D+ dan D-
        Dp, Dn = Dpos_neg(dataset_new, zTopsis, Spm)
        # Perhitungan C
        C, accur = res_C(dataset_new, Dn, Dp)
        # Hasil Akhir
        data_b = result(dataset, data_a, C)
        accuration, sortr = accurate(data_b, dataset, accur)
        y.append(round(float(accuration),2))
        x.append("K-"+str(i))
        Jumlah_data =i*100+34

        json_records = sortr.reset_index().to_json(orient='records')
        data = []
        data = json.loads(json_records)

        json_records = seleksi2.reset_index().to_json(orient='records')
        data1 = []
        data1 = json.loads(json_records)
    return render(request, 'index1.html', {
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
        'Jumlah_data' : Jumlah_data,
    })




# Normalisasi
def norm_AHP(P) :
    norAHP = np.zeros([len(P), len(P[0])])
    for i in range(len(P)):
        for j in range(len(P[0])):
            norAHP[j][i] = P[i][j]/sum(P[i])
    return(norAHP)

# Bobot Kriteria
def weight_crit(P,norAHP):
    wAHP = np.zeros(len(P))
    for i in range(len(P)):
        count = 0
        for j in range(len(P[0])):
            count += norAHP[j][i]
        wAHP[i] = count/6
    return(wAHP)

# LambdaAX
def lamb_AX(P,wAHP):
    lAX = np.zeros(len(P))
    for i in range(len(P)):
        count = 0
        for j in range(len(P[0])):
            count += P[j][i] * wAHP[j]
        lAX[i] = count
    lamb_Max(P,wAHP,lAX)
    return(lAX)

# lMax
def lamb_Max(P,wAHP,lAX) :
    lMax = 0
    for i in range(len(P)):
        lMax += lAX[i]/wAHP[i]
    lMax = lMax/len(P)
    return(lMax)



# Seleksi hasil CI
def CI_CR(lMax,P):
    CI = (lMax-len(P))/(len(P)-1)
    CR = CI / 1.24
    return(CR)

# Normalisasi TOPSIS
def norm_TOPSIS(dataset_new):
    norTOPSIS = np.zeros([len(dataset_new), len(dataset_new[0])])
    for i in range(len(dataset_new)):
        for j in range(len(dataset_new[0])):
            norTOPSIS[i][j] = dataset_new[i][j]/np.sqrt(sum(dataset_new[i]**2))
    return(norTOPSIS)

# Normalisasi TOPSIS * BOBOT AHP
def norm_AHPxTOPSIS(dataset_new,norTOPSIS,wAHP):
    zTopsis = np.zeros([len(dataset_new), len(dataset_new[0])])
    for i in range(len(dataset_new)):
        for j in range(len(dataset_new[0])):
            zTopsis[i][j] = norTOPSIS[i][j]*wAHP[i]
    return(zTopsis)


# Solusi Positif Negatif
def SPM(dataset_new,zTopsis):
    Spm = np.zeros([2, len(dataset_new)])
    for i in range(len(Spm)):
        for j in range(len(Spm[0])):    
            if i == 0 :
                Spm[i][j] = max(zTopsis[j])
            else :
                Spm[i][j] = min(zTopsis[j])
    return(Spm)

def Dpos_neg(dataset_new,zTopsis,Spm):
    # Perhitungan D+
    Dp = np.zeros(len(dataset_new[0]))
    for j in range(len(Dp)):
        count = 0
        for i in range(len(dataset_new)):
            count += (zTopsis[i][j] - Spm[0][i])**2
        Dp[j] = np.sqrt(count)

    # Perhitungan D-
    Dn = np.zeros(len(dataset_new[0]))
    for j in range(len(Dn)):
        count = 0
        for i in range(len(dataset_new)):
            count += (zTopsis[i][j] - Spm[1][i])**2
        Dn[j] = np.sqrt(count)
    return(Dp,Dn)

# Perhitungan C
def res_C(dataset_new,Dn,Dp):
    print("")
    C = np.zeros(len(dataset_new[0]))
    for i in range(len(C)):
        C[i] = Dn[i] / (Dp[i]+Dn[i])
    accur = C[0]
    C = np.delete(C, 0, 0)
    return(C,accur)

# Hasil Akhir
def result(dataset,data_a,C):
    np.set_printoptions(precision=3, suppress=True, threshold=sys.maxsize)
    data_b = dataset[(dataset['Id'] == data_a[0][0])]
    for i in range(1, len(data_a[0])):
        data_b = data_b.append(dataset[(dataset['Id'] == data_a[0][i])])
    data_b['Score'] = C
    data_b = data_b.sort_values(by=['Score'], ascending=False)
    return(data_b)

def accurate(data_b,dataset,accur) :
    sortr = pd.DataFrame()
    sortr = sortr.append(data_b[(data_b['Score'] >= accur)])
    accuration = len(sortr['Id'])/len(dataset['Id'])*100
    return(accuration,sortr)



def rest(request):
    return render(request, 'rest.html')

def index(request):
    if request.method == 'POST':
        # dataset = staticfiles_storage.url('../data/dataset(AutoRecovered)-Copy.xlsx')
        # dataset = request.FILES['data']
        # seleksi diambil dari excel dataset.xlsx pada sheet seleksi, data ini berisi kriteria yang bisa dipilih user
        # seleksi2 = pd.read_excel(dataset, sheet_name='seleksi')
        seleksi2 = pd.read_excel(r'C:\Users\Prozire\OneDrive\Python\Ipymb\dataset(AutoRecovered)-Copy.xlsx', sheet_name='seleksi')
        seleksi2 = seleksi2.replace(np.nan, "", regex=True)
        # seleksi diambil dari excel dataset.xlsx pada sheet dataset, data ini berisi seluruh laptop yang tersedia
        dataset = pd.read_excel(r'C:\Users\Prozire\OneDrive\Python\Ipymb\dataset(AutoRecovered)-Copy.xlsx', sheet_name='Sheet1')
        # dataset = dataset.head(30)
        np.set_printoptions(precision=3, suppress=True, threshold=sys.maxsize)
        # print(seleksi)
        # Kriteria
        # try :
        input_usr = [
            # Proccessor 0: untuk default, 1-11 : sesuai kriteria
            float(request.POST["cpu"]),
            # Graphic 0: untuk default, 1-6 : sesuai kriteria
            float(request.POST["gpu"]),
            # Display 0: untuk default, 1-11 : sesuai kriteria
            float(request.POST["disp"]),
            # Ram 0: untuk default, 1-9 : sesuai kriteria
            float(request.POST["ram"]),
            # Storage 0: untuk default, 1-11 : sesuai kriteria
            float(request.POST["store"]),
            # Rentan harga untuk dibawah angka
            float(request.POST["price"]),] 
        if (input_usr.count(0) > 1) :
            input_usr = [100,148,35,8,768,5700000]            

        input_usr.insert(0,40001)
        label = ["Id","Score CPU","Score GPU","Score Display","Score Ram","Score Storage","Score Price"]
        data_a = dataset[['Id', 'scr_cpu', 'scr_gpu', 'scr_dis', 'scr_ram', 'scr_str', 'harga_baru']]
               # data_a = dataset.loc[['Id', 'scr_cpu', 'scr_gpu', 'scr_dis', 'scr_ram', 'scr_str', 'harga_baru']]
        data_a = np.transpose(data_a.to_numpy())
        data_a = np.insert(data_a, [0], [[input_usr[0]],[input_usr[1]],[input_usr[2]],[input_usr[3]],[input_usr[4]],[input_usr[5]],[input_usr[6]]], axis=1)
        dataset_new = np.delete(data_a, 0, axis=0)
        
        count = 1
        P = np.zeros((6,6))
        for i in range (6) :
            for j in range(i,6):
                if i==j:
                    P[i][j] = 1
                else :
                    count = count+1
                    P[i][j] = float(request.POST['P'+str(count)])
                    P[j][i] = float(request.POST['P'+str(count)])/float(request.POST['P'+str(count)])**2
            P = np.transpose(P)
        
        
        CR = 100
        while CR > 0.1 or CR == 0:
            # Normalisasi
            norAHP = norm_AHP(P)
            
            # Bobot Kriteria
            wAHP = weight_crit(P,norAHP)
            
            # LambdaAX
            lAX = lamb_AX(P,wAHP)

            # lMax
            lMax = lamb_Max(P,wAHP,lAX)

            # Seleksi hasil CI
            CI = (lMax-len(P))/(len(P)-1)

            # Consitensy Ratio
            CR = CI / 1.24
            if CR > 0.1 or CR == 0 :
                #Kriteria tingkat kepentingan
                arraya = np.zeros((6,6))
                for i in range(6):
                    for j in range(6):
                        a = random.randint(0, 1)
                        if a == 1 :
                            a=round(1/random.randint(1,9),4)
                        else :
                            a=random.randint(1,9)
                        arraya[i,j] = a
                        arraya[j,i] = 1/a
                    arraya[i,i] = 1
                P = np.transpose(P)
                P = np.copy(arraya)
                    
#         print(P)

    # Normalisasi TOPSIS
        norTOPSIS = norm_TOPSIS(dataset_new)

    # Normalisasi TOPSIS * BOBOT AHP
        zTopsis = norm_AHPxTOPSIS(dataset_new,norTOPSIS,wAHP)

    # Solusi Positif Negatif
        Spm = SPM(dataset_new,zTopsis)

    #     Perhitungan D+ dan D-
        Dp,Dn = Dpos_neg(dataset_new,zTopsis,Spm)

    # Perhitungan C
        C,accur = res_C(dataset_new,Dn,Dp)

        # Hasil Akhir
        data_b = result(dataset,data_a,C)

        accuration,sortr = accurate(data_b,dataset,accur)

        
        json_records = sortr.reset_index().to_json(orient ='records') 
        data = [] 
        data = json.loads(json_records)

        json_records = seleksi2.reset_index().to_json(orient ='records') 
        data1 = [] 
        data1 = json.loads(json_records)
        return render(request, 'index.html', {
            'norAHP' : norAHP,
            'wAHP' : wAHP,
            'lAX' : lAX,
            'lMax' : lMax,
            'CR' : CR,
            'norTOPSIS' : np.transpose(norTOPSIS),
            'zTopsis' : np.transpose(zTopsis) ,
            'Dp' : Dp,
            'Dn' : Dn,
            'C' : C,
            'data_b' : data_b,
            'sortr' : data,
            'Spm' :Spm,
            'P' :np.round(P,2),
            'accuration' : round(accuration,2) ,
            'lent' : len(sortr['Id']),
            'seleksi2' : data1,
            'inpt_usr' : input_usr,
            'label' : label,
        })

    else:
        return render(request, 'index.html',{'uji' : 'uji',})