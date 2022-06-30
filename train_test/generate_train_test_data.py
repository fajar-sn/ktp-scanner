import os
import cv2
import numpy as np

from tqdm import tqdm
from RandomWordGenerator import RandomWord

from trdg.generators import (
    GeneratorFromRandom,
    GeneratorFromStrings,
)

ROOT_DIR = "."

class NIKRandomGenerator(GeneratorFromRandom):
    def __init__(self, count):
        super ( ).__init__(length=1,
                        use_letters=False,
                        use_symbols=False)
        
        self.count = count
        self.generator = GeneratorFromStrings(strings=self.pick_random_name(), 
                                              fonts=[os.path.join(ROOT_DIR, 'train_test', 'fonts', 'arial.ttf')],
                                              skewing_angle=5,
                                              random_blur=False,
                                              random_skew=True,
                                              distorsion_type=0,
                                              count=self.count,
                                              size=64,
                                              character_spacing=0,
                                              fit=True)

    def pick_random_name(self):
        random_word = RandomWord(include_digits=True, include_special_chars=True, special_chars=r"-")
        words: list[str] = []

        for i in range(count):
            generated_words = random_word.getList(5)

            for j in range (len(generated_words)):
                new_word = generated_words[j].upper()
                generated_words[j] = new_word

            words.append(' '.join(generated_words))

        return words

count = 100
generator = NIKRandomGenerator(count=count)
prefix = os.path.join(ROOT_DIR, 'train_test', 'DATASET', 'address_dataset')
os.makedirs(prefix, exist_ok=True)
path = os.path.join(prefix, 'labels.csv')

write_header = not os.path.exists(path)

with open(path, "a", encoding="utf8") as f:
    if write_header:
        f.write("filename, words\n")

    for i, (image, label) in tqdm(enumerate(generator.generator), total=count) :
        file_name = os.path.join(prefix, f'{label}.png')

        # Pipeline similar to inference
        image = cv2.cvtColor (np.array(image), cv2.COLOR_BGR2GRAY)
        image = cv2.GaussianBlur(src=image, ksize=(3, 3), sigmaX=0, sigmaY=0)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(12, 12))
        image = clahe.apply(image)

        _, image = cv2.threshold(image, thresh=165, maxval=255, type=cv2.THRESH_TRUNC + cv2.THRESH_OTSU)

        # if 'test' in prefix:
        #     image = AUG_TRANSFORMATIONS (image=image)

        cv2.imwrite(filename=file_name, img=image)
        f.write(f"{file_name}, {label}\n" )

# file_path = os.path.join(ROOT_DIR, 'train_test', 'fonts', 'arial.ttf')
# file_exist = exists(file_path)
# print(f"file name {file_exist}")