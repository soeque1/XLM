import csv
import os
import logging
import random

logger = logging.getLogger(__name__)
SEED = 12345

class KoData:
    def __init__(self, path: str):
        file_list = os.listdir(path)
        self.file_list = [path + i for i in file_list if i.endswith(".csv")]
        self.save_path = path + './merged/'
        # Make Save Folder
        os.makedirs(self.save_path, exist_ok=True)
        self.ko_en_tot = []

    def load_and_merge(self):
        for i in self.file_list:
            ko_en = self.load_and_split(i)
            self.ko_en_tot.extend(ko_en)

    def load_and_split(self, filename):
        ko_en = []
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            for idx, row in enumerate(reader):
                assert len(row) == 3
                # Header
                if idx == 0:
                    continue
                ko_en.append([row[1], row[2]])
        return ko_en

    def save_files(self):
        self.en_tot = []
        self.ko_tot = []

        logger.debug(len(self.ko_en_tot))
        random.seed(SEED)
        random.shuffle(self.ko_en_tot)

        for ko_en in self.ko_en_tot:
            self.ko_tot.append(ko_en[0])
            self.en_tot.append(ko_en[1])

        assert len(self.ko_tot) == len(self.en_tot) == len(self.ko_en_tot)

        with open(self.save_path + 'all.en', 'w') as f:
            for i in self.en_tot:
                f.write(i + '\n')

        with open(self.save_path + 'all.ko', 'w') as f:
            for i in self.ko_tot:
                f.write(i + '\n')


if __name__ == '__main__':
    PreData = KoData('./preprocess_ko_mt/data/')
    PreData.load_and_merge()
    PreData.save_files()