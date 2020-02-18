import zipfile
import os
import sys
from os.path import basename

sys.path.append('../')

COMPR_DATASET_DIR = ''
DATA_DIR = ''

def create_zip_archive_stage_one(filename:str):
    global DATA_DIR, COMPR_DATASET_DIR
    COMPR_DATASET_DIR = '../preprocessing/compressed_datasets/'
    DATA_DIR = '../preprocessing/data/'

    print('Zipping data')
    zipf = zipfile.ZipFile(COMPR_DATASET_DIR + filename + '_extracted.zip', 'w', zipfile.ZIP_DEFLATED)
    lenDirPath = len(DATA_DIR)
    for root, _ , files in os.walk(DATA_DIR):
        for file in files:
            filePath = os.path.join(root, file)
            zipf.write(filePath , filePath[lenDirPath :] )
    zipf.close()


