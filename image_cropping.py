# pip install opencv-python
import cv2
import os
from copy import copy
from pathlib import Path 
from constants import X, Y, BOTTOM_LEFT, BOTTOM_RIGHT, MAX_WORKERS
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed


class _ImageBase(ABC):
    @abstractmethod
    def __init__(self):
        pass

    def show(self):
        cv2.imshow(self.name, self._image)
        cv2.waitKey(0)

    def save(self, path):
        if self.name == '':
            raise Exception('File name not specified')
        try:
            os.makedirs(path, exist_ok=True)
            output_path = Path(path).joinpath(self.name)
            cv2.imwrite(str(output_path), self._image)
            return True
        except Exception:
            return False


class Image(_ImageBase):
    def __init__(self, filename):
        self._image = cv2.imread(filename)
        self._filepath = Path(filename)
        self._height, self._width = self._image.shape[:2]
        self.name = self._filepath.name


class ImageCropping(_ImageBase):
    def __init__(self, parent, P1, P2):
        self.parent = parent
        self.P1 = P1
        self.P2 = P2
        self._image = copy(self.parent._image)[self.P1[Y]:self.P2[Y], self.P1[X]:self.P2[X]]
        self.name = parent.name
    
    def show_in_parent(self):
        cv2.imshow(self.name, cv2.rectangle(copy(self.parent._image), pt1=self.P1, pt2=self.P2, color=(0,0,255), thickness=2))
        cv2.waitKey(0)


class CroppingGenerator:
    def __init__(self, input_directory, output_directory):
        self.input_directory = input_directory
        self.output_directory = output_directory 

    def generate_bottom_corners_croppings(self, height_percent, width_percent):
        os.makedirs(self.output_directory, exist_ok=True)

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            tasks = {executor.submit(self._generate_bottom_corners_croppings, filename, height_percent, width_percent): filename for filename in os.listdir(self.input_directory)}
        
            for task in as_completed(tasks):
                print(task)

    def _generate_bottom_corners_croppings(self, filename, height_percent, width_percent):
        img = Image(os.path.join(self.input_directory, filename))

        p1 = (0, int(img._height*(1-height_percent)))
        p2 = (int(img._width*width_percent), img._height)
        bottom_left = ImageCropping(img, p1, p2)

        p1 = (int(img._width*(1-width_percent)), int(img._height*(1-height_percent)))
        p2 = (img._width, img._height)
        bottom_right = ImageCropping(img, p1, p2)

        bottom_left_path = os.path.join(self.output_directory, BOTTOM_LEFT)
        bottom_right_path = os.path.join(self.output_directory, BOTTOM_RIGHT)

        bottom_left.save(bottom_left_path)
        bottom_right.save(bottom_right_path)


if __name__ == '__main__':
    from constants import FRAMES_PATH, CROPPED_IMGS_PATH
    img = Image(f'{FRAMES_PATH}/6W3EPytK7aM=1.jpg')
    # p1 = (0, 400)
    # p2 = (500, img._height)

    # bottom_left = ImageCropping(img, p1, p2) 
    # bottom_left.show()

    # p3 = (650, 200)
    # p4 = (700, 250)

    # square = ImageCropping(bottom_left, p3, p4)
    # square.show()

    # print(square.is_contained(bottom_left))

    # p5 = (200, 450)
    # p6 = (250, 500)
    # square2 = ImageCropping(bottom_left, p5, p6)
    # square2.show()
    # print(square2.is_contained(bottom_left))

    #img.save('test')

    # Testar as porcentagens para definir os cantos inferiores
    # height_percent = 0.54
    # width_percent = 0.3

    # p1 = (0, int(img._height*(1-height_percent)))
    # p2 = (int(img._width*width_percent), img._height)
    # # bottom_left = ImageCropping(img, p1, p2)

    # p1 = (int(img._width*(1-width_percent)), int(img._height*(1-height_percent)))
    # p2 = (img._width, img._height)
    # bottom_right = ImageCropping(bottom_left, p1, p2)

    # ibase = _ImageBase()

    # bottom_right.show()
    # bottom_right.save()
    # img.show()
    # img.save('ztest')

    # img2 = ImageCropping(img, p1, p2)
    # img2.show()
    # img2.show_in_parent()
    # img2.save('ztest')

    cg = CroppingGenerator(FRAMES_PATH, CROPPED_IMGS_PATH)
    cg.generate_bottom_corners_croppings(0.55, 0.3)