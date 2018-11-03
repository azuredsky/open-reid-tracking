from __future__ import print_function, absolute_import
import os.path as osp
import os
import glob

from ..utils.data import Dataset
from ..utils.osutils import mkdir_if_missing
from ..utils.serialization import write_json

from PIL import Image


class DetDuke(Dataset):
    def __init__(self, root, iCams=list(range(1, 9)), is_detection=True):
        super(DetDuke, self).__init__(root)

        self.download(iCams, is_detection)
        pass

    def __len__(self):
        return len(self.indexs)  # len(glob.glob1(self.root, "*.jpg"))

    def download(self, iCams, is_detection):
        import re
        import hashlib
        import shutil
        from glob import glob
        from zipfile import ZipFile

        # and more than 7000 ids from dukemtmc
        self.indexs = []

        def duke_register(pattern=re.compile(r'c(\d+)_f(\d+)')):
            if not is_detection:
                for iCam in iCams:
                    fpaths = sorted(glob(osp.join(self.root, 'camera' + str(iCam), '*.jpg')))
                    for fpath in fpaths:
                        fname = osp.join('camera' + str(iCam), osp.basename(fpath))
                        cam, frame = map(int, pattern.search(fname).groups())
                        assert cam == iCam
                        self.indexs.append(fname)
            else:
                fpaths = sorted(glob(osp.join(self.root, '*.jpg')))
                for fpath in fpaths:
                    fname = osp.basename(fpath)
                    if len(iCams) < 8:
                        cam, frame = map(int, pattern.search(fname).groups())
                        assert 1 <= cam <= 8
                        # cam -= 1  # from range[1,8]to range[0,7]
                        if cam not in iCams:
                            continue
                    self.indexs.append(fname)
                # shutil.copy(fpath, osp.join(images_dir, fname))

        duke_register()


class Preprocessor(object):
    def __init__(self, dataset, root=None, transform=None):
        super(Preprocessor, self).__init__()
        self.dataset = dataset
        self.root = root
        self.transform = transform

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, indices):
        if isinstance(indices, (tuple, list)):
            return [self._get_single_item(index) for index in indices]
        return self._get_single_item(indices)

    def _get_single_item(self, index):
        fname = self.dataset.indexs[index]
        fpath = fname
        if self.root is not None:
            fpath = osp.join(self.root, fname)
        img = Image.open(fpath).convert('RGB')
        if self.transform is not None:
            img = self.transform(img)
        return img, fname
