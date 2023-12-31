import torch
import cv2
import numpy as np
import os
import glob as glob

from xml.etree import ElementTree as et
from config import (
    CLASSES, RESIZE_TO, 
    TRAIN_DIR_IMAGES, VALID_DIR_IMAGES, 
    TRAIN_DIR_LABELS, VALID_DIR_LABELS,
    BATCH_SIZE
)
from torch.utils.data import Dataset, DataLoader
from custom_utils import collate_fn, get_train_transform, get_valid_transform

# the dataset class
class CustomDataset(Dataset):
    def __init__(
        self, images_path, labels_path, 
        width, height, classes, transforms=None
    ):
        self.transforms = transforms
        self.images_path = images_path
        self.labels_path = labels_path
        self.height = height
        self.width = width
        self.classes = classes
        self.image_file_types = ['*.jpg', '*.jpeg', '*.png', '*.ppm']
        self.all_image_paths = []
        
        # get all the image paths in sorted order
        for file_type in self.image_file_types:
            self.all_image_paths.extend(glob.glob(f"{self.images_path}/{file_type}"))
        self.all_annot_paths = glob.glob(f"{self.labels_path}/*.xml")
        # Remove all annotations and images when no object is present.
        self.read_and_clean()
        self.all_images = [image_path.split(os.path.sep)[-1] for image_path in self.all_image_paths]
        self.all_images = sorted(self.all_images)
        print("Image files: "+"{}".format(self.all_image_paths))
        
    def read_and_clean(self):
        """
        This function will discard any images and labels when the XML 
        file does not contain any object.
        """
        for annot_path in self.all_annot_paths:
            tree = et.parse(annot_path)
            root = tree.getroot()
            object_present = False
            for member in root.findall('object'):
                object_present = True
            if object_present == False:
                print(f"Removing {annot_path} and corresponding image")
                self.all_annot_paths.remove(annot_path)
                self.all_image_paths.remove(annot_path.split('.xml')[0]+'.jpg')

    def __getitem__(self, idx):
        # capture the image name and the full image path
        image_name = self.all_images[idx]
        image_path = os.path.join(self.images_path, image_name)

        # read the image
        image = cv2.imread(image_path)

        # get the height and width of the image
        image_width = image.shape[1]
        image_height = image.shape[0]
        print("image hight: "+"{}".format(image_height))
        # convert BGR to RGB color format
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB).astype(np.float32)
        if image_width != self.width:
            print("Image:"+"{}".format(image_name)+" | Image width: "+"{}".format(image_width)+" | Desired width: "+"{}".format(self.width))
            image_resized = cv2.resize(image, (self.width, self.height))
            image_resized /= 255.0
            print(image_resized.shape[1])
        else:
            image_resized = image
        
        # capture the corresponding XML file for getting the annotations
        annot_filename = image_name[:-4] + '.xml'
        annot_file_path = os.path.join(self.labels_path, annot_filename)
        
        boxes = []
        labels = []
        tree = et.parse(annot_file_path)
        root = tree.getroot()
        
        # box coordinates for xml files are extracted and corrected for image size given
        for member in root.findall('object'):
            # map the current object name to `classes` list to get...
            # ... the label index and append to `labels` list
            labels.append(self.classes.index(member.find('name').text))
            
            # xmin = left corner x-coordinates
            xmin = int(member.find('bndbox').find('xmin').text)
            # xmax = right corner x-coordinates
            xmax = int(member.find('bndbox').find('xmax').text)
            # ymin = left corner y-coordinates
            ymin = int(member.find('bndbox').find('ymin').text)
            # ymax = right corner y-coordinates
            ymax = int(member.find('bndbox').find('ymax').text)
            
            # resize the bounding boxes according to the...
            # ... desired `width`, `height`
            # print("{}".format(image_name)+"Not the same width")
            xmin_final = xmin
            xmax_final = xmax
            ymin_final = ymin
            ymax_final = ymax


            if xmin_final<0 or xmax_final>640 or ymin_final<0 or ymax_final>512:
                print("Imagem: "+"{}".format(image_name)+" | xmin: "+"{}".format(xmin)+" | xmax: "+"{}".format(xmax)+" | ymin: "+"{}".format(ymin)+" | ymax: "+"{}".format(ymax))
                print("Imagem: "+"{}".format(image_name)+" | xmin: "+"{}".format(xmin_final)+" | xmax: "+"{}".format(xmax_final)+" | ymin: "+"{}".format(ymin_final)+" | ymax: "+"{}".format(ymax_final))
            
            boxes.append([xmin_final, ymin_final, xmax_final, ymax_final])

        if not np.array(boxes).size:
            boxes.append([0, 0, 0, 0])
        
        # bounding box to tensor
        boxes = torch.as_tensor(boxes, dtype=torch.float32)

        # if boxes.nelement() == 0:
        #     boxes.append([0, 0, 0, 0])
        # area of the bounding boxes
        area = (boxes[:, 3] - boxes[:, 1]) * (boxes[:, 2] - boxes[:, 0])
        # no crowd instances
        iscrowd = torch.zeros((boxes.shape[0],), dtype=torch.int64)
        # labels to tensor
        labels = torch.as_tensor(labels, dtype=torch.int64)

        # prepare the final `target` dictionary
        target = {}
        target["boxes"] = boxes
        target["labels"] = labels
        target["area"] = area
        target["iscrowd"] = iscrowd
        image_id = torch.tensor([idx])
        target["image_id"] = image_id
        # apply the image transforms
        if self.transforms:
            sample = self.transforms(image=image_resized,
                                     bboxes=target['boxes'],
                                     labels=labels)
            image_resized = sample['image']
            target['boxes'] = torch.Tensor(sample['bboxes'])
            
        return image_resized, target

    def __len__(self):
        return len(self.all_images)

# prepare the final datasets and data loaders
def create_train_dataset():
    train_dataset = CustomDataset(
        TRAIN_DIR_IMAGES, TRAIN_DIR_LABELS,
        640, 512, CLASSES, get_train_transform()
    )
    return train_dataset
def create_valid_dataset():
    valid_dataset = CustomDataset(
        VALID_DIR_IMAGES, VALID_DIR_LABELS, 
        640, 512, CLASSES, get_valid_transform()
    )
    return valid_dataset

def create_train_loader(train_dataset, num_workers=0):
    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=num_workers,
        collate_fn=collate_fn
    )
    return train_loader
def create_valid_loader(valid_dataset, num_workers=0):
    valid_loader = DataLoader(
        valid_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=num_workers,
        collate_fn=collate_fn
    )
    return valid_loader


# execute datasets.py using Python command from Terminal...
# ... to visualize sample images
# USAGE: python datasets.py
if __name__ == '__main__':
    # sanity check of the Dataset pipeline with sample visualization
    dataset = CustomDataset(
        TRAIN_DIR_IMAGES, 640, 512, CLASSES
    )
    print(f"Number of training images: {len(dataset)}")
    
    # function to visualize a single sample
    def visualize_sample(image, target):
        for box_num in range(len(target['boxes'])):
            box = target['boxes'][box_num]
            label = CLASSES[target['labels'][box_num]]
            cv2.rectangle(
                image, 
                (int(box[0]), int(box[1])), (int(box[2]), int(box[3])),
                (0, 255, 0), 2
            )
            cv2.putText(
                image, label, (int(box[0]), int(box[1]-5)), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2
            )
        cv2.imshow('Image', image)
        cv2.waitKey(0)
        
    NUM_SAMPLES_TO_VISUALIZE = 5
    for i in range(NUM_SAMPLES_TO_VISUALIZE):
        image, target = dataset[i]
        visualize_sample(image, target)