# Copyright (C) 31/08/19 sanjyotzade
import os
import argparse
from utility import Utils

if __name__ == '__main__':
    # arguments definitions
    parser = argparse.ArgumentParser(description='Downloading images & annotations for imagenet dataset')

    dir_path = os.path.realpath(os.path.dirname(__file__))
    path_to_annotations = os.path.join(dir_path, "annotation")
    path_to_final_dataset = os.path.join(dir_path, "partial_imagenet")
    ncodes_data_path = os.path.join(dir_path, "ncodes.csv")
    url_data_path = os.path.join(dir_path, "imageNetUrls.csv")

    optional = parser.add_argument_group('optional arguments')
    optional.add_argument('-a', '--annotations_dir', default=path_to_annotations, help='path to annotations data')
    optional.add_argument('-s', '--save_dir', default=path_to_final_dataset, help='path to the folder where downloaded data will be stored')
    optional.add_argument('-url', '--url_data', default=url_data_path, help='path to image-net urls data')
    optional.add_argument('-nc', '--ncode_data', default=ncodes_data_path, help='path to modified ncodes data')

    optional.add_argument('-anno', '--with_annotation', default=False, help='downloads images with annotations only')
    optional.add_argument('-p', '--parallel', default=True, help='downloaded parallelly or sequentially')
    optional.add_argument('-v', '--verbose', default=True , help='bool represent whether to display ncode level download stats')
    optional.add_argument('-b', '--batch_size', default=None, help='number of images to download paralelly, if parallel is TRUE')

    args = parser.parse_args()
    args.parallel = eval(str(args.parallel))
    args.with_annotation = eval(str(args.with_annotation))
    args.verbose = eval(str(args.verbose))
    args.batch_size = eval(str(args.batch_size))

    # starting the download process
    util_obj = Utils()
    util_obj.subset_ncodes_to_download(ncodes_data_path)
    util_obj.download_partial_imagenet_dataset(
        path_to_url_dataset=args.url_data,
        path_to_annotations=args.annotations_dir,
        path_to_save_dataset=args.save_dir,
        only_annotations=args.with_annotation,
        parallel=args.parallel,
        verbose=args.verbose,
        batch_size_=args.batch_size
    )

