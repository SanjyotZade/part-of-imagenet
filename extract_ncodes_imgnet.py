import os
from utility import utils

if __name__ == "__main__":
    dir_path = os.path.realpath(os.path.dirname(__file__))
    util_obj = utils()
    util_obj.download_ncodes_image_net()
