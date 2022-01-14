import numpy as np
import matplotlib.pyplot as plt
import glob
from scipy.ndimage import rotate
from PIL import Image
import xmltodict
from random import randrange
import os

print('Processing started...')

RESULT_PATH = './results/'


if not os.path.exists(RESULT_PATH):
    os.makedirs(RESULT_PATH)

# image = np.asarray(Image.open('1.png'))
# fig, axes = plt.subplots(2, 2)
# axes[0, 0].imshow(image)
# axes[0, 0].set_title("original")

def process(image, angle, file):
    with open(file.replace('png', 'xml'), 'r') as myfile:
        document = xmltodict.parse(myfile.read())
        object = document['annotation']['object']

    rotated = rotate(image, angle)
    original_center = (np.array(image.shape[:2][::-1]) - 1) / 2.
    rotated_center = (np.array(rotated.shape[:2][::-1]) - 1) / 2.

    if isinstance(object, dict):
        xmin = float(object.get('bndbox').get('xmin'))
        ymin = float(object.get('bndbox').get('ymin'))
        xmax = float(object.get('bndbox').get('xmax'))
        ymax = float(object.get('bndbox').get('ymax'))
        # axes[0, 0].scatter(xmax, ymax, c="r")
        # axes[0, 0].scatter(xmin, ymin, c="r")

        new_data = process_pool([xmin, ymin, xmax, ymax], original_center, rotated_center, angle)
        object['bndbox']['xmin'] = new_data[0]
        object['bndbox']['ymin'] = new_data[1]
        object['bndbox']['xmax'] = new_data[2]
        object['bndbox']['ymax'] = new_data[3]
    else:
        pools = []
        for obj in object:
            xmin = float(obj.get('bndbox').get('xmin'))
            ymin = float(obj.get('bndbox').get('ymin'))
            xmax = float(obj.get('bndbox').get('xmax'))
            ymax = float(obj.get('bndbox').get('ymax'))
            # axes[0, 0].scatter(xmax, ymax, c="r")
            # axes[0, 0].scatter(xmin, ymin, c="r")
            pools.append([xmin, ymin, xmax, ymax])

            for pool in pools:
                new_data = process_pool(pool, original_center, rotated_center, angle)
                obj['bndbox']['xmin'] = new_data[0]
                obj['bndbox']['ymin'] = new_data[1]
                obj['bndbox']['xmax'] = new_data[2]
                obj['bndbox']['ymax'] = new_data[3]

    new_image = Image.fromarray(rotated)
    new_image.save(RESULT_PATH + file.replace('.png', '_') + str(angle) + '.png')
    out = xmltodict.unparse(document, pretty=True)
    with open(RESULT_PATH + file.replace('.png', '_') + str(angle) + '.xml', 'a') as file:
        file.write(out[39:])

    return rotated

def process_pool(pool, original_center, rotated_center, angle):
    xmin = pool[0]
    ymin = pool[1]
    xmax = pool[2]
    ymax = pool[3]

    org = np.array([xmin, ymin]) - original_center
    a = np.deg2rad(angle)
    new = np.array([org[0] * np.cos(a) + org[1] * np.sin(a),
                    -org[0] * np.sin(a) + org[1] * np.cos(a)])
    new_adjusted = new + rotated_center
    (xmin_new, ymin_new) = new_adjusted
    # axes.flatten()[1].scatter(xmin_new, ymin_new, c="r")

    org = np.array([xmax, ymax]) - original_center
    a = np.deg2rad(angle)
    new = np.array([org[0] * np.cos(a) + org[1] * np.sin(a),
                    -org[0] * np.sin(a) + org[1] * np.cos(a)])
    new_adjusted = new + rotated_center
    (xmax_new, ymax_new) = new_adjusted
    # axes.flatten()[1].scatter(xmax_new, ymax_new, c="r")

    return [xmin_new, ymin_new, xmax_new, ymax_new]

# fig, axes = plt.subplots(2, 2)
# axes[0, 0].imshow(image)
# axes[0, 0].set_title("original")

# angle = randrange(180)
# rotated = process(image, angle)
# axes.flatten()[1].imshow(rotated)
# plt.show()

for file in glob.glob('*.png'):
    image = np.asarray(Image.open('./' + file))
    process(image, randrange(180), file)

print('Processing ended.')