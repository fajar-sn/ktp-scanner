import re

# text = "J ns TT bi 7\n\nPROVINSI JAWA TIMUR\nKABUPATEN SIDOARJO\n\nNIK : 3515084807720005\n\nNama :SITIBADRIYAH\n\nTempat/Tgl Lahir : KEDIRI, 08-07-1972\n\nJenis kelamin : PEREMPUAN Gol. Darah :O\n\nAlamat : CITRA FAJAR GOLF E-7229\nRTRW 1 002/008\nKevDesa : GEBANG\nKecamatan : SIDOARJO\n\nAgama : ISLAM =\nStatus Perkawinan: KAWIN\nPekerjaan : BELUM/TIDAK BEKERJA\n\nKewarganegaraan: WNI\nBertaku Hingga  : SEUMUR HIDUP\n\n"
# text = '“mr oo\nPROVINSI JAWA TIMUR\nKABUPATEN SIDOARJO\n\n: 3515081309990004\n\nTFAJAR SEPTIAN NUGRAHA\nTemp="¥TalLahy :KEDIHI, 13-09-1999\nJentz Lolpmin ILAKI-LAKI Gol. Darah :O .-\nAlarst a. CITRA FAJAR GOLF E E-a7a2a29\nRTRW 1 002/008 -\nKeDesa : GEBANG\nKecamatan : SIDOARJO SDA\nAgama ISLAM\nStatus Perkawinan: BELUM KAWIN\nPekerjaan BELUM/TIDAK BEKE!\nA Kewarganegaraan: Wel\n4 Bertakur-ngga SE MURHIDUM™ Re\n\n'
# text = 'NIK : 35150813099900014\n\nNama -FAJAP SEPTIAN HUGRAHA |\nTalang KENA 130O-199A .\n| Jeng Sena AK ARI Gol. arah :0\n4? Alan STIRAFAJAR GOLF E 7229\nprRY : 1 202/308\n\n1\nU\n\n: Agama: ISLAMI |\n| Status Perkawnan: BELUT KAIN —\n. Pekerjaan BELUMTIDAK BEKERJA\n\nKewarganegaraan: 3 aa\n| Berlaku 19ga SE SAP HID -\n\nNE\n'
# text = text.replace(":", "")
text = 'PROVINSI JAWA TIMUR\nKABUPATEN SIDOARJO\n\nNIK : 3515084807?720005\nNama : SITI BADRIYAH\nTempar/Tgi Lahir : KEDIRI, 08-07-1972\n: Jenis kelamin : PEREMPUAN Gol. Darah :O\nEa Alamat : CITRA FAJAR GOLF £-7229\nrat RT/AAW : 002/008\n\nKeVvDesa : GEBANG\nKecamatan : SIDOARJO\n\nAgama : ISLAM\nStatus Perkawinan: KAWIN\nPekerjaan : BELUMWTIDAK BEKERJA\n\nKewarganegaraan: WNI\nBerlaku Hingga: SEUMUR HIDUP'

def word_to_number_converter(word) -> str:
    word_dict = {
        'b': "6",
        'e': "2",
        '?': "7",
        "|": "1"
    }

    res = ""

    for letter in word:
        if letter in word_dict:
            res += word_dict[letter]
        else:
            res += letter
    return res.strip()

def correct_wrong_character(number) -> str:
    number_dict = {
        '0': 'O',
        '£': 'E'
    }

    res = ""

    for letter in number:
        if letter in number_dict:
            res += number_dict[letter]
        else:
            res += letter
    return res.strip()


# text = 'Ea SANA em KN AA “NA an pda AE MPa 2\n\nNIK : 351508480? ?20005\n\nNama : SITI BADRIYAH\n\nTempat/Tgi Lahir : KEDIRI, 08-07-1972\n\nJenis kelamin : PEREMPUAN Gol. Darah :0\n\nAlamat : CITRA FAJAR GOLF E-7229\nRT/RW : 0692/0038\n\nAgama ISLAM\nStatus Perkawinan: KAWIN\nPekerjaan : BELUMTIDAK BEKERJA\n\nKewarganegaraan: WNI\nBerlaku Hingga — : SEUMUR HIDUP\n\n5\n'

id: str = ''
name: str = ''
birth_date: str = ''
birth_place: str = ''
gender: str = ''
blood_group: str = ''
address: str = ''
district: str = ''
village: str = ''
citizenship: str = ''
job: str = ''
relligion: str = ''
marriage_status: str = ''
rtrw: str = ''
province: str = ''
regency:str = ''

lines = text.split("\n")

for i in range(len(lines)):
    print(lines[i])

    for j in lines[i].split():
        if j.isdigit() and len(j) >= 5:
            id = j
            continue

    if "PRO" in lines[i]:
        lines[i] = lines[i].split()
        province = " ".join(lines[i][1:])

    if "KAB" in lines[i] or "KOT" in lines:
        lines[i] = lines[i].split()
        regency = " ".join(lines[i][1:])

    if "NIK" in lines[i] and len(id) < 1:
        lines[i] = lines[i].split(':')
        id = word_to_number_converter(lines[i][-1].replace(" ", "")).strip()
        continue

    if "Nama" in lines[i]:
        lines[i] = lines[i].split(':')
        name = lines[i][-1].replace('Nama ', '').strip()
        continue

    if "Temp" in lines[i]:
        lines[i] = lines[i].replace(",", "")

        if ":" in lines[i]:
            lines[i] = lines[i].split(':')
            birth_date = re.search("([0-9]{2}\-[0-9]{2}\-[0-9]{4})", lines[i][-1])[0]
            birth_place = lines[i][-1].replace(birth_date, '').strip()
        else:
            lines[i] = lines[i].split()

            for word in lines[i]:
                if "temp" in word.casefold():
                    lines[i].remove(word)

            birth_date = re.search("([0-9]{2}\-[0-9]{2}\-[0-9]{4})", lines[i][-1])[0]
            birth_place = lines[i][0].strip()

        if len(name) < 1:
            j = i

            while j > 0:
                if len(lines[j - 1]) > 0:
                    name = lines[j - 1]
                    break

                j -= 1

    if 'Darah' in lines[i]:
        gender = re.search("(LAKI-LAKI|LAKI|LELAKI|PEREMPUAN)", lines[i])[0]
        lines[i] = re.sub('[^A-Z]+', ' ', lines[i], 0, re.I)

        if ":" in lines[i]:
            lines[i] = lines[i].split(':')

            try:
                blood_group = correct_wrong_character(lines[i][-1])
                blood_group = re.search("(O|A|B|AB)", blood_group)[0]
            except:
                blood_group = '-'
        else:
            blood_group_line = lines[i].split()

            for word in blood_group_line:
                if len(word) < 3:
                    blood_group = correct_wrong_character(word)
                    
    if 'Ala' in lines[i] and len(address) < 1:
        address_line = word_to_number_converter(lines[i]).split()

        for word in address_line:
            if "Ala" in word:
                address_line.remove(word)

        address = " ".join(address_line)
        address = correct_wrong_character(address)
        address = re.sub('[^A-Z\-^A-Z^0-9]+', ' ', address, 0, re.I).strip()
    if 'NO.' in lines[i]:
        address = (address + ' '+lines[i]).strip()
    if "Kecamatan" in lines[i]:
        if ':' in lines[i]:
            district = lines[i].split(':')[1].strip()
        else:
            district_line = lines[i].split()
            district_line.remove(district_line[0])
            district = ' '.join(district_line)

    if "Desa" in lines[i]:
        wrd = lines[i].split()
        desa = []

        for wr in wrd:
            if not 'desa' in wr.lower():
                desa.append(wr)
        
        village = ''.join(wr).strip()
    if 'Kewarganegaraan' in lines[i]:
        if ":" in lines[i]:
            citizenship = lines[i].split(':')[1].strip()
        else:
            citizenship = lines[i].casefold().replace("kewarganegaraan", "").strip().upper()
            citizenship_line = citizenship.split()

            for word in citizenship_line:
                if len(word) < 2:
                    citizenship_line.remove(word)

            citizenship = ''.join(citizenship_line)

    if 'Pekerjaan' in lines[i]:
        wrod = lines[i].split()
        pekerjaan = []
        
        for wr in wrod:
            if not '-' in wr:
                pekerjaan.append(wr)
        
        job = ' '.join(pekerjaan).replace('Pekerjaan', '')
        job = re.sub('[^A-Z\/]+', ' ', job, 0, re.I).strip()
    if 'Agama' in lines[i]:
        relligion = lines[i].replace('Agama', "").strip()
        relligion = re.sub('[^A-Z]+', '', relligion, 0, re.I).strip()
    if 'Perkawinan' in lines[i]:
        if ":" in lines[i]:
            marriage_status = lines[i].split(':')[1].strip()
        else: 
            marriage_status = lines[i].casefold().replace("status perkawinan", "").strip().upper()
    if "RT" in lines[i]:
        rtrw = lines[i].replace("RTRW", '').strip()
        rtrw_line = rtrw.split()

        for word in rtrw_line:
            if len(word) > 3:
                rtrw = word


print(f"\nid: {id}")
print(f"name: {name}")
print(f"birth_date: {birth_date}")
print(f"birth_place: {birth_place}")
print(f"gender: {gender}")
print(f"blood_gropu: {blood_group}")
print(f"address: {address}")
print(f"district: {district}")
print(f"village: {village}")
print(f"citizenship: {citizenship}")
print(f"job: {job}")
print(f"relligion: {relligion}")
print(f"marriage_status: {marriage_status}")
print(f"rtrw: {rtrw}")
print(f"province: {province}")
print(f"regency: {regency}")