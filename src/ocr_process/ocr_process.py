import time
import cv2
import json
import re
import numpy
import pytesseract

from src.ocr_process.ktp_information import KTPInformation
from PIL import Image
# from easyocr import Reader

class OcrProcess:
    def __init__(self, image: numpy.ndarray):
        self.image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        timestamp = time.strftime("%d-%b-%Y-%H_%M_%S")
        file_name = f"./{timestamp}.jpg"
        cv2.imwrite(file_name, self.image)
        # self.th, self.threshed = cv2.threshold(self.image, 127, 255, cv2.THRESH_TRUNC)

        # self.image = cv2.GaussianBlur(self.image, (5, 5), 0)
        self.image = cv2.GaussianBlur(self.image, (5, 5), sigmaX=0, sigmaY=0)
        # _, self.threshed = cv2.threshold(self.image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(12, 12))
        processed_image = clahe.apply(self.image)
        self.threshed = cv2.resize(processed_image, (640, 360), interpolation=cv2.INTER_LINEAR)

        _, self.threshed = cv2.threshold(processed_image, 0, 255, cv2.THRESH_TRUNC + cv2.THRESH_OTSU)
        self.threshed = cv2.adaptiveThreshold(self.threshed, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

        # image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # processed_image = cv2.GaussianBlur(src=self.threshed, ksize=(3, 3), sigmaX=0, sigmaY=0)

        # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(12, 12))
        # processed_image = clahe.apply(self.threshed)
            
        timestamp = time.strftime("%d-%b-%Y-%H_%M_%S")
        file_name = f"./{timestamp} 2.jpg"
        # cv2.imwrite(file_name, self.threshed)
        cv2.imwrite(file_name, self.threshed)
        print(f"file saved at {file_name}")

        print("[INFO] OCR'ing input image...")
        start = time.time()
        # reader = Reader(["en"])
        # results = reader.readtext(image)
        

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
        self.master_process()

        print("execution time: %.2f seconds" % (time.time() - start))

    def process(self):
        raw_extracted_text = pytesseract.image_to_string(
            (self.threshed), lang="nik")

        # image_to_box = pytesseract.image_to_boxes(self.threshed, lang="indbest")

        # for ()

        return raw_extracted_text

    def word_to_number_converter(self, word):
        word_dict = {
            '|': "1"
        }
        res = ""
        for letter in word:
            if letter in word_dict:
                res += word_dict[letter]
            else:
                res += letter
        return res

    def nik_extract(self, word):
        word_dict = {
            'b': "6",
            'e': "2",
        }
        res = ""
        for letter in word:
            if letter in word_dict:
                res += word_dict[letter]
            else:
                res += letter
        return res

    def extract(self, extracted_result):
        self.extracted_result = extracted_result
        print(extracted_result.replace('\n', ' -- '))
        for word in extracted_result.split("\n"):
            if "NIK" in word:
                word = word.split(':')
                self.result.id = self.nik_extract(word[-1].replace(" ", ""))
                continue

            if "Nama" in word:
                word = word.split(':')
                self.result.name = word[-1].replace('Nama ', '')
                continue

            if "Tempat" in word:
                word = word.split(':')
                self.result.birth_date = re.search(
                    "([0-9]{2}\-[0-9]{2}\-[0-9]{4})", word[-1])[0]
                self.result.birth_place = word[-1].replace(
                    self.result.birth_date, '')
                continue

            if 'Darah' in word:
                self.result.gender = re.search(
                    "(LAKI-LAKI|LAKI|LELAKI|PEREMPUAN)", word)[0]
                word = word.split(':')
                try:
                    self.result.blood_group = re.search(
                        "(O|A|B|AB)", word[-1])[0]
                except:
                    self.result.blood_group = '-'
            if 'Alamat' in word:
                self.result.address = self.word_to_number_converter(
                    word).replace("Alamat ", "")
            if 'NO.' in word:
                self.result.address = self.result.address + ' '+word
            if "Kecamatan" in word:
                self.result.district = word.split(':')[1].strip()
            if "Desa" in word:
                wrd = word.split()
                desa = []
                for wr in wrd:
                    if not 'desa' in wr.lower():
                        desa.append(wr)
                self.result.village = ''.join(wr)
            if 'Kewarganegaraan' in word:
                self.result.citizenship = word.split(':')[1].strip()
            if 'Pekerjaan' in word:
                wrod = word.split()
                pekerjaan = []
                for wr in wrod:
                    if not '-' in wr:
                        pekerjaan.append(wr)
                self.result.job = ' '.join(pekerjaan).replace(
                    'Pekerjaan', '').strip()
            if 'Agama' in word:
                self.result.relligion = word.replace('Agama', "").strip()
            if 'Perkawinan' in word:
                self.result.marriage_status = word.split(':')[1]
            if "RTRW" in word:
                word = word.replace("RTRW", '')
                self.result.rt = word.split('/')[0].strip()

    def master_process(self):
        raw_text = self.process()
        self.extract(raw_text)

    def to_json(self):
        return json.dumps(self.result.__dict__, indent=4)
