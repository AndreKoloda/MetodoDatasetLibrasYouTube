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

    def generate_bottom_corner_croppings(self, side, height_percent, width_percent):
        os.makedirs(self.output_directory, exist_ok=True)

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            tasks = {executor.submit(self._generate_bottom_corner_croppings, side, filename, height_percent, width_percent): filename for filename in os.listdir(self.input_directory)}
        
            for task in as_completed(tasks):
                print(task)

    def _generate_bottom_corner_croppings(self, side, filename, height_percent, width_percent):
        img = Image(os.path.join(self.input_directory, filename))

        if side == BOTTOM_RIGHT:
            p1 = (int(img._width*(1-width_percent)), int(img._height*(1-height_percent)))
            p2 = (img._width, img._height)
            bottom_corner = ImageCropping(img, p1, p2)
        else:
            p1 = (0, int(img._height*(1-height_percent)))
            p2 = (int(img._width*width_percent), img._height)
            bottom_corner = ImageCropping(img, p1, p2)
            

        path = os.path.join(self.output_directory, side)
        bottom_corner.save(path)


if __name__ == '__main__':
    pass
