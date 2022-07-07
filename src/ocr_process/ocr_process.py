import time
import cv2
import re
import numpy
import pytesseract

from src.ocr_process.ktp_information import KTPInformation

class OcrProcess:
    def __init__(self, image: numpy.ndarray):
        self.image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # For documentation purpose
        # timestamp = time.strftime("%d-%b-%Y-%H_%M_%S")
        # file_name = f"./{timestamp}.jpg"
        # cv2.imwrite(file_name, self.image)
        # self.th, self.threshed = cv2.threshold(self.image, 127, 255, cv2.THRESH_TRUNC)

        # Image blurring
        self.image = cv2.GaussianBlur(self.image, (5, 5), sigmaX=0, sigmaY=0)
        
        # Image
        # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(12, 12))
        # processed_image = clahe.apply(self.image)
        self.threshed = cv2.resize(self.image, (640, 360), interpolation=cv2.INTER_LINEAR)

        _, self.threshed = cv2.threshold(self.image, 0, 255, cv2.THRESH_TRUNC + cv2.THRESH_OTSU)
        self.threshed = cv2.adaptiveThreshold(self.threshed, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            
        # timestamp = time.strftime("%d-%b-%Y-%H_%M_%S")
        # file_name = f"./{timestamp} 2.jpg"
        # cv2.imwrite(file_name, self.threshed)
        # print(f"file saved at {file_name}")

        print("[INFO] OCR'ing input image...")
        start = time.time()

        # # loop over the results
        # for (bbox, text, prob) in results:
        #     # display the OCR'd text and associated probability
        #     print("[INFO] {:.4f}: {}".format(prob, text))
        #     # # unpack the bounding box
        #     # (tl, tr, br, bl) = bbox
        #     # tl = (int(tl[0]), int(tl[1]))
        #     # tr = (int(tr[0]), int(tr[1]))
        #     # br = (int(br[0]), int(br[1]))
        #     # bl = (int(bl[0]), int(bl[1]))
        #     # # cleanup the text and draw the box surrounding the text along
        #     # # with the OCR'd text itself
        #     # text = cleanup_text(text)
        #     # cv2.rectangle(image, tl, br, (0, 255, 0), 2)
        #     # cv2.putText(image, text, (tl[0], tl[1] - 10),
        #     # 	cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        self.result = KTPInformation()
        raw_text = self.process()
        self.extract(raw_text)

        print("execution time: %.2f seconds" % (time.time() - start))

    def process(self):
        raw_extracted_text: str = pytesseract.image_to_string((self.threshed), lang="eng+ind")
        return raw_extracted_text

    def correct_wrong_character(self, word: str) -> str:
        correct_dict = {
            '0': 'O',
            '£': 'E'
        }

        res = ""

        for letter in word:
            if letter in correct_dict:
                res += correct_dict[letter]
            else:
                res += letter

        return res.strip()

    def word_to_number_converter(self, word: str) -> str:
        correct_dict = {
            'b': "6",
            'e': "2",
            '?': "7",
            "|": "1",
            "C": "0",
            "H": "4",
            "c": "2",
            "¢": "2",
            "u": "4"
        }

        res = ""

        for letter in word:
            if letter in correct_dict:
                res += correct_dict[letter]
            else:
                res += letter

        return res

    def extract(self, text: str):
        lines = text.split("\n")

        for i in range(len(lines)):
            print(lines[i])

            if "PRO" in lines[i] or "vinsi" in lines[i].casefold():
                lines[i] = lines[i].split()
                self.result.province = " ".join(lines[i][1:])
                continue

            if "KAB" in lines[i] or "KOT" in lines:
                lines[i] = lines[i].split()
                self.result.regency = " ".join(lines[i][1:])
                continue

            if "NIK" in lines[i] and len(self.result.id) < 1:
                lines[i] = lines[i].split(':')
                id = self.word_to_number_converter(lines[i][-1].replace(" ", ""))
                self.result.id = re.sub('[^0-9]+', '', id, 0, re.I).strip()
                continue

            if len(self.result.id) < 1:
                for j in lines[i].split():
                    if j.isdigit() and len(j) >= 5:
                        self.result.id = j
                
                continue

            if 'nam' in lines[i].casefold():
                name_line = lines[i].split(":")
                self.result.name = name_line[-1].replace('Nama ', '').strip()
                continue

            if len(self.result.name) < 5:
                if ":" in lines[i]:
                    name_line = lines[i].split(":")
                    self.result.name = name_line[-1].replace('Nama ', '').strip()
                else:
                    self.result.name = re.sub('[^A-Z]+', ' ', lines[i], 0, re.I).strip()

                    if "nam" in lines[i].casefold():
                        self.result.name = " ".join(self.result.name.split()[1:]).strip()

                continue

            if "Temp" in lines[i] or "Ten" in lines[i]:
                lines[i] = lines[i].replace(",", "")

                if ":" in lines[i]:
                    lines[i] = lines[i].split(':')
                    birth_date = re.sub('[^0-9\-]+', '', lines[i][-1], 0, re.I)

                    try:
                        self.result.birth_date = re.search("([0-9]{2}\-[0-9]{2}\-[0-9]{4})", birth_date)[0]
                    except:
                        self.result.birth_date = lines[i][-1]
                    
                    self.result.birth_place = lines[i][-1].replace(self.result.birth_date, '').strip()
                else:
                    lines[i] = lines[i].split()

                    for word in lines[i]:
                        if "temp" in word.casefold():
                            lines[i].remove(word)

                    try:
                        self.result.birth_date = re.search("([0-9]{2}\-[0-9]{2}\-[0-9]{4})", birth_date)[0]
                    except:
                        self.result.birth_date = lines[i][-1]

                    self.result.birth_place = lines[i][0].strip()

                if len(self.result.name) < 1:
                    j = i

                    while j > 0:
                        if len(lines[j - 1]) > 0:
                            self.result.name = lines[j - 1]
                            break

                        j -= 1

                continue

            if 'Dara' in lines[i] and len(self.result.blood_group) < 1:
                try:
                    self.result.gender = re.search("(LAKI-LAKI|LAKI|LELAKI|PEREMPUAN)", lines[i])[0]
                except:
                    self.result.birth_date = lines[i][-1]
                
                lines[i] = re.sub('[^A-Z]+', ' ', lines[i], 0, re.I)

                if ":" in lines[i]:
                    lines[i] = lines[i].split(':')

                    try:
                        blood_group = self.correct_wrong_character(lines[i][-1])
                        self.result.blood_group = re.search("(O|A|B|AB)", blood_group)[0]
                    except:
                        self.result.blood_group = '-'
                else:
                    blood_group_line = lines[i].split()

                    for word in blood_group_line:
                        if len(word) < 3:
                            self.result.blood_group = self.correct_wrong_character(word)

                continue
                            
            if 'Ala' in lines[i] and len(self.result.address) < 1:
                address_line = lines[i].split()

                for word in address_line:
                    if "Ala" in word:
                        address_line.remove(word)

                address = " ".join(address_line)
                address = self.correct_wrong_character(address)
                self.result.address = re.sub('[^A-Z\-^A-Z^0-9]+', ' ', address, 0, re.I).strip()

            if 'NO.' in lines[i]:
                self.result.address = (self.result.address + ' '+lines[i]).strip()
                continue

            if "Kecamatan" in lines[i]:
                if ':' in lines[i]:
                    self.result.district = lines[i].split(':')[1].strip()
                else:
                    district_line = lines[i].split()
                    district_line.remove(district_line[0])
                    self.result.district = ' '.join(district_line)
                
                continue

            if "Desa" in lines[i]:
                wrd = lines[i].split()
                desa = []

                for wr in wrd:
                    if not 'desa' in wr.lower():
                        desa.append(wr)
                
                self.result.village = ''.join(wr).strip()
                continue

            if 'Kewarganegaraan' in lines[i]:
                if ":" in lines[i]:
                    self.result.citizenship = lines[i].split(':')[1].strip()
                else:
                    citizenship = lines[i].casefold().replace("kewarganegaraan", "").strip().upper()
                    citizenship_line = citizenship.split()

                    for word in citizenship_line:
                        if len(word) < 2:
                            citizenship_line.remove(word)

                    self.result.citizenship = ''.join(citizenship_line)

                continue

            if 'Pekerjaan' in lines[i]:
                wrod = lines[i].split()
                pekerjaan = []
                
                for wr in wrod:
                    if not '-' in wr:
                        pekerjaan.append(wr)
                
                job = ' '.join(pekerjaan).replace('Pekerjaan', '')
                self.result.job = re.sub('[^A-Z\/]+', ' ', job, 0, re.I).strip()
                continue

            if 'Agama' in lines[i]:
                relligion = lines[i].replace('Agama', "").strip()
                self.result.relligion = re.sub('[^A-Z]+', '', relligion, 0, re.I).strip()
                continue

            if 'Perkawinan' in lines[i]:
                if ":" in lines[i]:
                    marriage_status = lines[i].split(':')[1].upper()
                    self.result.marriage_status = re.sub('[^A-Z\ ]+', '', marriage_status, 0, re.I).strip()
                else: 
                    self.result.marriage_status = lines[i].casefold().replace("status perkawinan", "").strip().upper()

                continue

            if "RT" in lines[i]:
                rtrw = lines[i].replace("RTRW", '').strip()
                rtrw_line = rtrw.split()

                for word in rtrw_line:
                    if len(word) > 3:
                        self.result.rtrw = word