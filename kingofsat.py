from bs4 import BeautifulSoup
import requests, sqlite3
import math

# ## Extract all Free-to-air channels from the given satellite

dictinaryOfsatellites = {'ASTRA_19_2E':['https://en.kingofsat.net/pos-19.2E.php', '8'],
                         'Hot_Bird_13E':['https://en.kingofsat.net/pos-13E.php', '6'],
                         'Eutelsat_16A_16E':['https://en.kingofsat.net/pos-16E.php', '7'],
                         'ASTRA_3B_23_5E':['https://en.kingofsat.net/pos-23.5E.php', '10'],
                         'Astra_4A_4_8E':['https://en.kingofsat.net/pos-4.8E.php', '52'],
                         'Eutelsat_7E':['https://en.kingofsat.net/pos-7E.php', '4'],
                         'Eurobird_9E':['https://en.kingofsat.net/pos-9E.php', '51'],
                         }


class kingofsat:

    def __init__(self, sat='', filename='', alisatID=''):

        self.sat = sat
        self.alisatid = alisatID
        self.satFreq = ''
        self.filename = filename
        self.satParameters = {

            # 'transponderParameters':[],
            # 'tansponderChannels':[]

        }

        self.channels = []

    def get(self):
        # self.sat=sat
        s = '#EXTM3U\n'
        counter = 0
        if self.sat:
            self.page = requests.get(self.sat).text
            self.soup = BeautifulSoup(self.page, "html.parser")
            conta = self.soup.find_all('table', class_='frq')
        for el in range(len(conta)):
            
            satelites = conta[el].find_all('td')[:-1]
            try:
                satFreq = int(math.floor(float(satelites[2].string)))
            except:
                satFreq = (satelites[2].string)
            # print(satelites[2].string)
            for headerElement in satelites:
                self.satParameters.setdefault(satFreq, {}).setdefault('transponderParameters', []).append(headerElement.get_text())

            prn = conta[el].next_sibling.next_sibling.find_all('a', class_='A3')
            try:

                for el1 in prn:
                    counter += 1
                    el = el1.parent.parent.find_all('td')
                    chanName = el[2].get_text().strip()
                    provider = 'satoperator'
                    satellite = self.satParameters[satFreq]['transponderParameters'][1]
                    if satellite[0].isdigit() == True: satellite = satellite[1:]
                    if satellite[0].isdigit() == True: satellite = satellite[1:]
                    transponder = satFreq
                    fr = self.satParameters[satFreq]['transponderParameters'][3]
                    lnb = self.satParameters[satFreq]['transponderParameters'][4]
                    fec = self.satParameters[satFreq]['transponderParameters'][8][-3:]
                    deg = self.satParameters[satFreq]['transponderParameters'][0][:4] + self.satParameters[satFreq]['transponderParameters'][0][5:]
                    sid = el[7].get_text()
                    vpid = el[8].get_text()
                    apid = el[9].get_text().split()[0]
                    pmt = el[10].get_text()
                    ttx = el[12].get_text()
                    nid = self.satParameters[satFreq]['transponderParameters'][10][4:]
                    tid = self.satParameters[satFreq]['transponderParameters'][11][4:]
                    SR = self.satParameters[satFreq]['transponderParameters'][8].split()[0]
                    dvbType = self.satParameters[satFreq]['transponderParameters'][6]
                    mtype = self.satParameters[satFreq]['transponderParameters'][7]
                    Freechannel = el[6].get_text()
                    
                    # print('''(channel,transponder,fr,lnb,fec,degree,vpid,apid,sid,nid,tid) values ("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")''' % (chanName, transponder, fr, lnb, fec, deg, vpid, apid, sid, nid, tid))
                    # print(satellite, transponder, fr, SR, dvbType, mtype, fec, chanName, vpid, apid, pmt, ttx)
                    lista = 'alisatid={alisatId}&freq={freq}&pol={pol}&ro=0.35&msys={dvbtype}&mtype={mtype}&plts=on&sr={SR}&fec={fec}&pids=0,17,18,{vpid},{apid},{pmt}'
                    if "Clear" in Freechannel.strip() :
                        formattedchannel = lista.format(alisatId=self.alisatid, freq=transponder, pol=fr.lower(), dvbtype=dvbType.replace('-', '').lower(), mtype=mtype.lower(), SR=SR, fec=fec.replace('/', ''), vpid=vpid.strip(), apid=apid, pmt=pmt.strip())
                        s += '#EXTINF:0,{counter}. {channelName}\nrtsp://sat.ip/?{queries}\n'.format(channelName=chanName, queries=formattedchannel, counter=counter)
                    elif 'BISS' in Freechannel.strip() :
                        formattedchannel = lista.format(alisatId=self.alisatid, freq=transponder, pol=fr.lower(), dvbtype=dvbType.replace('-', '').lower(), mtype=mtype.lower(), SR=SR, fec=fec.replace('/', ''), vpid=vpid.strip(), apid=apid, pmt=pmt.strip())
                        s += '#EXTINF:0,{counter}. BISS: {channelName}\nrtsp://sat.ip/?{queries}\n'.format(channelName=chanName, queries=formattedchannel, counter=counter)
            except Exception as e:
                print (e)
        filename = '{}.m3u'.format(self.filename)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(s)


for key in dictinaryOfsatellites:
    print(key)
    filename = key
    url = dictinaryOfsatellites[filename][0]
    alisatID = dictinaryOfsatellites[filename][1]
    proba = kingofsat(url, filename, alisatID)
    proba.get()
