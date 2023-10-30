import torch
BATCH_SIZE = 32 # increase / decrease according to GPU memeory
RESIZE_TO = 512 # resize the image for training and transforms
NUM_EPOCHS = 100 # number of epochs to train for
NUM_WORKERS = 4
DEVICE = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
  
# Images and labels direcotry should be relative to train.py
TRAIN_DIR_IMAGES = 'dataset/images/train'
TRAIN_DIR_LABELS = 'dataset/images/train'
VALID_DIR_IMAGES = 'dataset/images/test'
VALID_DIR_LABELS = 'dataset/images/test'
# classes: 0 index is reserved for background
CLASSES = [
    'car', 'person', 'motorcycle', 'truck', 'animal'
]
NUM_CLASSES = len(CLASSES)
# whether to visualize images after creating the data loaders
VISUALIZE_TRANSFORMED_IMAGES = False
# location to save model and plots
OUT_DIR = 'outputs'