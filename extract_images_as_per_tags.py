import os
from utility import utils

if __name__ == "__main__":

    dir_path = os.path.realpath(os.path.dirname(__file__))


    path_to_annotations = os.path.join(dir_path, "annotation")
    path_to_final_dataset = os.path.join(dir_path, "dataset")
    ncodes_data_path = os.path.join(dir_path, "ncodes_.csv")
    url_data_path = os.path.join(dir_path, "imageNet_urls.csv")

    util_obj = utils()

    util_obj.subset_ncodes_to_download(ncodes_data_path)
    util_obj.download_partial_imagenet_dataset(
        path_to_url_dataset=url_data_path,
        path_to_annotations=path_to_annotations,
        path_to_save_dataset=path_to_final_dataset,
        verbose=True
    )
