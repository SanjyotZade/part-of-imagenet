# Copyright (C) 31/08/19 sanjyotzade
import os
import argparse
from utility import Utils

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Downloading ncodes for imagenet dataset')

    dir_path = os.path.realpath(os.path.dirname(__file__))
    path_to_save = os.path.realpath(os.path.dirname(__file__))

    optional = parser.add_argument_group('optional arguments')
    optional.add_argument('-nc_dir', '--ncodes_dir', default=path_to_save, help='path to saved ncodes data')
    optional.add_argument('-url_data', '--with_url_data', default=False, help='tag whether to download url data')

    args = parser.parse_args()
    util_obj = Utils()

    # download ncodes data csv
    util_obj.download_ncodes_image_net(path_to_save=args.ncodes_dir)

    # download imagenet urls csv
    args.url_data = eval(str(args.with_url_data))
    util_obj.download_image_net_urls(path_to_save=args.ncodes_dir)
