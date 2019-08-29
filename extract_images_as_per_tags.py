import os
import re
import wget
import tarfile
import requests
import pandas as pd
from tqdm import tqdm
import urllib.request as anchor
from urllib.error import URLError, HTTPError


if __name__ == "__main__":

    path_to_annotations = "/Users/sanjyotzade/Documents/youplus_projects/brand_safety/data_preparation/imageNet/Annotation"
    path_to_final_dataset = "/Users/sanjyotzade/Documents/youplus_projects/brand_safety/data_preparation/imageNet/dataset"

    codes_data_path = "/Users/sanjyotzade/Documents/youplus_projects/brand_safety/data_preparation/imageNet/ncodes_.csv"
    ncodes_data = pd.read_csv(codes_data_path)

    #subset required categories
    temp_data = ncodes_data[ncodes_data["nsfw"] == True]
    print ("\nRequested codes to download")
    print (temp_data.head())
    print ()

    print ("Reading url data..")
    #load image url data
    url_data_path = "/Users/sanjyotzade/Documents/youplus_projects/brand_safety/data_preparation/imageNet/imageNet_urls.csv"
    url_data = pd.read_csv(url_data_path)


    #download image from urls
    path_to_api = "http://www.image-net.org/api/download/imagenet.bbox.synset?wnid="
    for row_num, code in enumerate(temp_data["code"]):

        category_name = temp_data.loc[row_num,"name"]
        category_name = re.sub(r"\s+", "", category_name, flags=re.UNICODE)
        folder_path = os.path.join(path_to_final_dataset,category_name)

        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

        print("\nDownloading category : {} ({})".format(category_name,code))
        # extract annotations for a category
        annotated_file = os.path.join(path_to_annotations,code+".tar.gz")
        extract_annotation_path = os.path.join(folder_path)
        command = "tar xf {} -C {}".format(annotated_file,extract_annotation_path)
        os.system(command)

        # starting to download images from urls
        http_error = 0
        url_error = 0
        total = 0
        image_urls = url_data[url_data["code"]==code]
        image_urls = image_urls.reset_index(drop=True)

        for image_num, url in enumerate(tqdm(image_urls["img_url"])):
            _, ext = os.path.splitext(url)
            tail = image_urls.loc[image_num,"img_code"]

            if os.path.exists(os.path.join(folder_path,tail+ext)):
                continue
            try:
                anchor.urlretrieve(url,os.path.join(folder_path,tail+ext))
            except HTTPError as e:
                http_error += 1
            except URLError as e:
                url_error += 1
            total += 1

        print("\nFor category {}".format(category_name))
        print("No-file errors : {}/{}l".format(http_error, total))
        print("download errors : {}/{}\n".format(url_error, total))
        print("download complete for {}\n".format(category_name))
