__author__ = 'vfedotov'

import paint_engine_core as pec

class Image(pec.Image):
    def __init__(self, width, height):
        super().__init__(width, height)

    def registerQImage(self, image: QImage):
        pass