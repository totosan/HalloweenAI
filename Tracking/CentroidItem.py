class CentroidItem(object):
    def __init__(self, class_type, tracker=None, rect=(0,0,0,0), center=[0,0]):
        self.class_type = class_type
        self.tracker = tracker
        self.rect = rect
        self.center = center

