import PIL
from PIL import Image
import os


STORAGE_PATH = os.path.join(os.getcwd(), f'PinterestScraper/images')


def rescale(folder_name):
    widths, heights = [], []

    storage_folder = os.path.join(STORAGE_PATH, folder_name)
    new_storage_folder = os.path.join(STORAGE_PATH, f'{folder_name}_rescaled')

    try:
        os.chdir(new_storage_folder)
    except FileNotFoundError:
        os.mkdir(new_storage_folder)
        os.chdir(new_storage_folder)

    for filename in os.listdir(storage_folder):
        if not filename.startswith('.'):
            file = os.path.join(storage_folder, filename)
            img = PIL.Image.open(file)

            wid, hgt = img.size
            widths.append(wid)
            heights.append(hgt)

            new_img = img.resize((234, 234))
            new_img.save(os.path.join(new_storage_folder, filename))

    print(folder_name, min(widths), min(heights))


for core in ['breakcore', 'glitchcore', 'draincore', 'weirdcore']:
    rescale(core)
