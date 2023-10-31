from PIL import Image
import os

path = 'images/test'

images = [f for f in os.listdir(path) if '.jpg' in f.lower()]

if not os.path.exists("resized/"):
    os.mkdir("resized/")

for image in images:
    print(image)
    newpath = "resized/"+image
    image = Image.open(path+"/"+image)
    new_image = image.resize((640, 512))
    new_image.save(newpath)