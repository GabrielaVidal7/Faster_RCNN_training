import glob as glob
from xml.etree import ElementTree as et

images_path = 'images/test'
labels_path = 'images/test'
# get all the image paths in sorted order
image_file_types = ['*.jpg', '*.jpeg', '*.png', '*.ppm']
all_image_paths = []

for file_type in image_file_types:
    all_image_paths.extend(glob.glob(f"{images_path}/{file_type}"))
all_annot_paths = glob.glob(f"{labels_path}/*.xml")


for image_name in all_annot_paths:
    tree = et.parse(image_name)
    root = tree.getroot()
    # box coordinates for xml files are extracted and corrected for image size given
    for member in root.findall('object'):
        
        # xmin = left corner x-coordinates
        xmin = int(member.find('bndbox').find('xmin').text)
        # xmax = right corner x-coordinates
        xmax = int(member.find('bndbox').find('xmax').text)
        # ymin = left corner y-coordinates
        ymin = int(member.find('bndbox').find('ymin').text)
        # ymax = right corner y-coordinates
        ymax = int(member.find('bndbox').find('ymax').text)
        if xmin<0 or xmax>640 or ymin<0 or ymax>512:
            print("Imagem: "+"{}".format(image_name)+" | xmin: "+"{}".format(xmin)+" | xmax: "+"{}".format(xmax)+" | ymin: "+"{}".format(ymin)+" | ymax: "+"{}".format(ymax))