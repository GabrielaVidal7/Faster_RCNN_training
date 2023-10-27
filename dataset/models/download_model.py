import os
import shutil
import glob
import urllib.request
import tarfile

MODEL = 'faster_rcnn_resnet152_v1_640x640_coco17_tpu-8'
MODEL_FILE = MODEL + '.tar.gz'
DOWNLOAD_BASE = 'http://download.tensorflow.org/models/object_detection/tf2/20200711/'
DEST_DIR = 'faster_rcnn_inception_v2'

# #if not (os.path.exists(MODEL_FILE)):
# #  opener = urllib.request.URLopener()
# #  opener.retrieve(DOWNLOAD_BASE + MODEL_FILE, MODEL_FILE)

with urllib.request.urlopen(DOWNLOAD_BASE+MODEL_FILE) as response, open(MODEL_FILE, 'wb') as out_file:
  shutil.copyfileobj(response, out_file)

tar = tarfile.open(MODEL_FILE)
tar.extractall()
tar.close()

os.remove(MODEL_FILE)
if (os.path.exists(DEST_DIR)):
  shutil.rmtree(DEST_DIR)
os.rename(MODEL, DEST_DIR)