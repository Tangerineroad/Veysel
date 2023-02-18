import datetime
from ddeclient_modified import DDEClient
import codecs
import os

def fillDict(allSyms):
    ALL_VALUES = dict()
    for e in allSyms:
        ALL_VALUES[e] = -1
    return ALL_VALUES            
                
def readSymbols():
    f = codecs.open("sabitler\\allSymbolsV4.csv","r","utf8")
    allSyms = [x.replace("\r","").replace("\n","") for x in f.readlines()]
    f.close()
    return allSyms

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

# now, to clear the screen
cls()

vsg = {'0223':'28.02.2023',
       '0323':'31.03.2023',
       '0423':'30.04.2023',
       '0523':'31.05.2023',
       '0623':'30.06.2023',
       '0723':'31.07.2023',
       '0823':'31.08.2023',
       '0923':'30.09.2023',
       '1023':'31.10.2023',
       '1123':'30.11.2023',
       '1223':'31.12.2023'}

def getDate(dStr):
    try:
        dt = datetime.datetime.date(datetime.datetime.strptime(vsg[dStr],'%d.%m.%Y'))
    except:
        dt = datetime.datetime.date(datetime.datetime.now())
    return dt


if __name__=='__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--first_id', dest='init_id', type=int, help='set first id')
    parser.add_argument('--final_id', dest='final_id', type=int, help='set final id')
    parser.add_argument('--number_of_lines', dest='num_of_lines', type=int, help='set number of lines in display')
    args = parser.parse_args()

    iid = args.init_id
    fid = args.final_id
    num_of_lines = args.num_of_lines

    allSymbols = readSymbols()
    allSyms = allSymbols[iid:fid]

    hisseler = dict()
    hesaplar = dict()

    for item in allSyms:
        temp = item.split('.')[0].split('_')[-1]
        if len(temp) < 6:
            cHisse = temp
            cVade = 'SPOT'
        else:
            cHisse = temp[:-4]
            cVade  = temp[-4:]

        hisseler[item] = cHisse

        tvadeler = list(set([x.split(".")[0].split("_")[-1][-4:] for x in allSyms if cHisse in x and "F_" in x]))
        vadeler = [x[2:]+x[:2] for x in sorted([x[2:]+x[:2] for x in tvadeler])]
    ##    print(vadeler)

        vadeler.insert(0,'SPOT')
        for ii in range(0,len(vadeler)):
            for jj in range(ii+1,len(vadeler)):
                if cVade in [vadeler[ii],vadeler[jj]]:

                    if vadeler[ii] == 'SPOT':
                        vlam= cHisse+".AMIKTAR1"
                        v1a = cHisse+".AFIYAT1"
                        v1s = cHisse+".SFIYAT1"
                        vlsm= cHisse+".SMIKTAR1"
                        v1n = cHisse+'_SPOT'
                    else:
                        v1am = "F_"+cHisse+vadeler[ii]+".AMIKTAR1"
                        v1a = "F_"+cHisse+vadeler[ii]+".AFIYAT1"
                        v1s = "F_"+cHisse+vadeler[ii]+".SFIYAT1"
                        v1sm = "F_"+cHisse+vadeler[ii]+".SMIKTAR1"
                        v1n = cHisse+"_"+vadeler[ii]

                    v2am = "F_"+cHisse+vadeler[jj]+".AMIKTAR1"
                    v2a = "F_"+cHisse+vadeler[jj]+".AFIYAT1"
                    v2s = "F_"+cHisse+vadeler[jj]+".SFIYAT1"
                    v2sm = "F_"+cHisse+vadeler[jj]+".SMIKTAR1"
                    v2n = cHisse+"_"+vadeler[jj]
                    
                    if item in hesaplar.keys():
                        hesaplar[item].append([[vlam,v1a,v1s,vlsm,v1n],[v2am,v2a,v2s,v2sm,v2n]])
                    else:
                        hesaplar[item] = [[[vlam,v1a,v1s,vlsm,v1n],[v2am,v2a,v2s,v2sm,v2n]]]

    try:
        dde = DDEClient("MTX", "DATA")
        for item in allSyms:
            dde.advise(item)
            dde.advise(item,stop=True)
    except OSError as e:
        print("Veri alinamiyor...")
        print(e)
        pass

    ALL_VALUES = fillDict(allSyms)
    ALL_PAIRS = dict()
    ktb_old = []
    btk_old = []
    first_time = True
    while True:
        d1 = datetime.datetime.now()
        for item in allSyms:
            try:
                value = float(dde.request(item=item,timeout=300).replace(b',',b'.'))
            except Exception as exp:
                value = -1

            if value >= 0 and (not value == ALL_VALUES[item]):
                ALL_VALUES[item] = value

        for item in allSyms:
            for each in hesaplar[item]:
                sam= ALL_VALUES[each[0][0]]
                sa = ALL_VALUES[each[0][1]]
                ss = ALL_VALUES[each[0][2]]
                ssm= ALL_VALUES[each[0][3]]
                
                vam= ALL_VALUES[each[1][0]]
                va = ALL_VALUES[each[1][1]]
                vs = ALL_VALUES[each[1][2]]
                vsm= ALL_VALUES[each[1][3]]

                if sa > 0 and ss > 0 and va > 0 and vs > 0:
                    sn = each[0][4]
                    vn = each[1][4]
                
                    getiri = (va+vs) / (sa+ss)
                    #date1 = getDate(sn.split("_")[1])
                    #date2 = getDate(vn.split("_")[1])
                    #vkg = (date2-date1).days
                    vkg=10
                    getiri_norm = ((getiri-1)/vkg*365)*100
                    
                    pair = sn.ljust(10) + '-' + vn.ljust(10)
                    price = ' : {:10.2f} {:10.2f} {:10.2f} {:10.2f} | {:10.2f} {:10.2f} {:10.2f} {:10.2f} | {:10.4f}  |'.format(sam,sa,ss,ssm,vam,va,vs,vsm,getiri_norm)

                    ALL_PAIRS[pair] = [getiri_norm,price]

        btk = sorted(ALL_PAIRS.items(), key=lambda kv: kv[1], reverse=True)

        const1 = not [(x[0],x[1]) for x in btk_old[:num_of_lines]] == [(x[0],x[1]) for x in btk[:num_of_lines]]

        if const1:
            btk_old = btk
            
            cls()

            print("|---------------------------------------------------------------------------------------------------------------------------------|")
            print("|                                            Largest to smallest                                                                  |")
            print("|                                                                                                                                 |")
            print("| "+'{:<10} {:<10} : {:>10} {:>10} {:>10} {:>10} | {:>10} {:>10} {:>10} {:>10} | {:>10}  |'.format('SPOT', 'VADELI', 'SPOTAM', 'SPOTAF', 'SPOTSF', 'SPOTSM', 'VADEAM', 'VADEAF', 'VADESF', 'VADESM','Getiri '))
            print("|---------------------------------------------------------------------------------------------------------------------------------|")
            for ind in range(0,len(btk)):
                if ind < len(hisseler)/8:
                    print("| "+btk[ind][0] + btk[ind][1][1] )
            print("|---------------------------------------------------------------------------------------------------------------------------------|")
            first_time = True
        
        d2 = datetime.datetime.now()






