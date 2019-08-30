import re
import os
import pandas as pd
import urllib.request
from tqdm import tqdm
from bs4 import BeautifulSoup
import urllib.request as anchor
from urllib.error import URLError
from urllib.error import HTTPError


class utils:
    """
    This class contains all the utility code required to download partial codes and mapping it to relevant image annotations.
    """
    def __init__(self):
        self.partial_ncodes_data = None

    def download_ncodes_image_net(self, path_to_save=None):
        """
        This function is used to download ncodes for image-net dataset and restructuring of the same in an csv file.
        :param path_to_save: folder path where the ncodes csv is to be saved.
        :return: absolute path to ncodes csv.
        """
        url = "http://image-net.org/api/text/imagenet.bbox.obtain_synset_wordlist"
        ncodes = pd.DataFrame([])

        path_to_save = os.path.realpath(os.path.dirname(__file__)) if path_to_save==None else path_to_save
        ncodes_path = os.path.join(path_to_save, "ncodes.csv")

        if not os.path.exists(ncodes_path):
            print("\nStarting to download imagenet ncodes...")
            with urllib.request.urlopen(url) as response:
                html = response.read()
                soup = BeautifulSoup(html, features="lxml")
                for code_num, link in enumerate(soup.findAll('a')):
                    code = (link.get('href').split("wnid=")[-1])
                    values = link.contents[0]
                    ncodes.loc[code_num, "code"] = code
                    ncodes.loc[code_num, "name"] = values
            ncodes["to_download"] = False
            ncodes.to_csv(ncodes_path, index=False)
            print("Download complete !\n")
        else:
            print("\n ncodes data already present in the  mentioned folder")
        return ncodes_path

    def subset_ncodes_to_download(self, path_to_ncodes_data):
        """
        This function is used to get ncodes sepcified for downloads.
        :param path_to_ncodes_data: absolute path to updated ncodes file.
        :return: pandas datafram comprising of ncodes to download
        """
        ncodes_data = pd.read_csv(path_to_ncodes_data)
        # subset required categories
        self.partial_ncodes_data = ncodes_data[ncodes_data["nsfw"] == True]
        return self.partial_ncodes_data

    def download_partial_imagenet_dataset(self, path_to_url_dataset, path_to_annotations, path_to_save_dataset, verbose=True):
        """
        This function is used to download imagenet images as per the sepcified subset of ncodes dataset.
        This function will also restructure the dataset as per images and corresponding annoatations
        :param path_to_url_dataset:
        :param path_to_annotations:
        :param path_to_save_dataset:
        :param verbose:
        :return:
        """
        url_data = pd.read_csv(path_to_url_dataset)

        # download image from urls
        path_to_api = "http://www.image-net.org/api/download/imagenet.bbox.synset?wnid="

        report = {"total": [], "http_error": [], "url_error": []}
        for row_num, code in enumerate(self.partial_ncodes_data["code"]):

            category_name = self.partial_ncodes_data.loc[row_num, "name"]
            category_name = re.sub(r"\s+", "", category_name, flags=re.UNICODE)
            folder_path = os.path.join(path_to_save_dataset, category_name)

            if not os.path.exists(folder_path):
                os.mkdir(folder_path)

            print("\nDownloading images for category : {} ({})".format(category_name, code))
            # extract annotations for a category
            annotated_file = os.path.join(path_to_annotations, code + ".tar.gz")
            extract_annotation_path = folder_path
            command = "tar xf {} -C {}".format(annotated_file, extract_annotation_path)
            os.system(command)

            # starting to download images from urls
            http_error = 0
            url_error = 0
            total = 0
            image_urls = url_data[url_data["code"] == code]
            image_urls = image_urls.reset_index(drop=True)

            for image_num, url in enumerate(tqdm(image_urls["img_url"])):
                _, ext = os.path.splitext(url)
                tail = image_urls.loc[image_num, "img_code"]

                if os.path.exists(os.path.join(folder_path, tail + ext)):
                    continue
                try:
                    anchor.urlretrieve(url, os.path.join(folder_path, tail + ext))
                except HTTPError as e:
                    http_error += 1
                except URLError as e:
                    url_error += 1
                total += 1
            if verbose:
                print("\nFor category {}".format(category_name))
                print("No-file errors : {}/{}".format(http_error, total))
                print("download errors : {}/{}\n".format(url_error, total))
            print("download complete for {}\n".format(category_name))

            report['total'].append(total)
            report['http_error'].append(http_error)
            report['url_error'].append(url_error)

        n_total = sum(report['total'])
        n_http_error = sum(report['http_error'])
        n_url_error = sum(report['url_error'])
        n_downloaded = n_total - (n_http_error+n_url_error)

        print("\n Final download report")
        print("total downloaded images {}/{}".format(n_downloaded, n_total))
        print("total absent-file errors {}/{}".format(n_url_error,n_total))
        print("total download errors {}/{}\n".format(n_http_error,n_total))


        print("\nDownload complete..")
        print("partial dataset are saved to: {}".format(path_to_save_dataset))
        return path_to_save_dataset
