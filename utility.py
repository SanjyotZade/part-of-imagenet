# Copyright (C) 31/08/19 sanjyotzade
import re
import os
import sys
import glob
import time
import shutil
import pandas as pd
from tqdm import tqdm
import multiprocessing
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from urllib.request import urlopen as anchor
from urllib.request import urlretrieve
import requests
import tarfile
import math


class Utils:
    """
    This class contains all the utility code required to download partial codes and mapping it to relevant image annotations.
    """
    IMAGE_FORMATS = [".jpg", "jpeg", "png", "gif", "tiff", "psd", "pdf", "eps", "ai", "indd"]
    NCODES_DATA_URL = "http://image-net.org/api/text/imagenet.bbox.obtain_synset_wordlist"
    NCODES_DATA_S3_URL = "https://model-specific-public-storage.s3.amazonaws.com/part-of-imagenet/ncodes.csv"
    IMAGE_NET_URL_DATA_LINK = "http://image-net.org/imagenet_data/urls/imagenet_fall11_urls.tgz"
    IMAGE_NET_URL_DATA_S3_LINK = "https://model-specific-public-storage.s3.amazonaws.com/part-of-imagenet/imageNetUrls.zip"

    def __init__(self):
        """
        Constructor for Utils class. This is used to initialize relevant class variables.
        """
        # initializing important class-level variables
        self.partial_ncodes_data = None
        self.report = {"total": [], "error": [], "save_error": []}

    def download_ncodes_image_net(self, path_to_save=None):
        """
        This function is used to download ncodes for image-net dataset and restructuring of the same in an csv file.
        Args:
            path_to_save {str}: folder path where the ncodes csv is to be saved.
        Returns {str}: absolute path to ncodes csv.
        """
        # parameter initialization
        ncodes = pd.DataFrame([])
        path_to_save = os.path.realpath(os.path.dirname(__file__)) if path_to_save==None else path_to_save
        ncodes_path = os.path.join(path_to_save, "ncodes.csv")

        if not os.path.exists(ncodes_path):
            print("\nDownloading imagenet ncodes...")
            try:
                self.download_file(self.NCODES_DATA_S3_URL, path_to_save)
                print("Download complete !\n")
            except:
                # download ncodes data
                with anchor(self.NCODES_DATA_URL) as response:
                    html = response.read()
                    soup = BeautifulSoup(html, features="lxml")
                    for code_num, link in enumerate(tqdm(soup.findAll('a'))):
                        code = (link.get('href').split("wnid=")[-1])
                        values = link.contents[0]
                        ncodes.loc[code_num, "code"] = code
                        ncodes.loc[code_num, "name"] = values
                # add relevant columns to ncode data
                ncodes["to_download"] = False
                ncodes["how_many"] = -1
                ncodes.to_csv(ncodes_path, index=False) # save ncode data
                print("Download complete !\n")
        else:
            print("\nncodes csv already present in the  mentioned folder")
        return ncodes_path

    def download_file(self, url, path_to_save):
        """
        This function is used to download a file from url with progress bar.
        Args:
            url {str}: http link to the file to download
            path_to_save {str}: folder path where the urls data is to be saved.
        Returns {str}: absolute path to image urls data.
        """
        local_filename = os.path.join(path_to_save, url.split('/')[-1])
        # NOTE the stream=True parameter below
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            block_size = 8192
            with open(local_filename, 'wb') as f:
                for chunk in tqdm(r.iter_content(chunk_size=block_size), total=math.ceil(total_size//block_size), unit='KB', unit_scale=True):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                        f.flush()
        return local_filename

    def download_image_net_urls(self, path_to_save=None):
        """
        This function is used to imagenet urls data and restructuring of the same in an csv file.
        Args:
            path_to_save {str}: folder path where the urls csv is to be saved.
        Returns {str}: absolute path to image urls csv.
        """
        # parameter initialization
        path_to_save = os.path.realpath(os.path.dirname(__file__)) if path_to_save == None else path_to_save
        image_urls_csv_path = os.path.join(path_to_save, "imageNetUrls.csv")
        image_urls_tgz_path = os.path.join(path_to_save, os.path.basename(self.IMAGE_NET_URL_DATA_LINK))

        if not os.path.exists(image_urls_csv_path):
            print("\nDownloading imagenet urls data...")
            try:
                zip_path = self.download_file(self.IMAGE_NET_URL_DATA_S3_LINK, path_to_save)
                try:
                    shutil.unpack_archive(zip_path, path_to_save)
                    os.remove(zip_path)
                    print("Imagenet url data csv saved !\n")
                except Exception as e:
                    print("Error while extracting imagenet urls from zip file\n")
                    print(e)
                    sys.exit()
            except:
                try:
                    # download imagenet urls data data
                    self.download_file(self.IMAGE_NET_URL_DATA_LINK, path_to_save)
                    print("Download complete\n")
                except Exception as e:
                    print("Error while downloading image net urls data.")
                    print(e)
                    sys.exit()
                downloaded_file_name = "fall11_urls.txt"
                url_data_path = os.path.join(path_to_save, downloaded_file_name)

                if not os.path.exists(url_data_path):
                    try:
                        shutil.unpack_archive(image_urls_tgz_path, path_to_save)
                        os.remove(image_urls_tgz_path)
                    except Exception as e:
                        print("Error while extracting imagenet urls from tar file\n")
                        print (e)
                        sys.exit()

                url_txt_data = open(url_data_path, "r", encoding="latin1")
                x = url_txt_data.readlines()
                url_data_dict = {path.split("\t")[0]: (path.split("\t")[-1]).split("\n")[0] for path in x}
                url_txt_data.close()
                os.remove(url_data_path)
                os.remove(image_urls_tgz_path)
                print("\nRestructuring & saving urls data..")
                url_data = pd.DataFrame(list(url_data_dict.items()), columns=['img_code', 'img_url'])
                url_data["code"] = url_data['img_code'].str.split('_').str[0]
                url_data.to_csv(image_urls_csv_path, index=False)
                print("Imagenet url data csv saved !\n")
        else:
            print ("Imagenet urls csv file already present\n")
        return image_urls_csv_path

    def subset_ncodes_to_download(self, path_to_ncodes_data):
        """
        This function is used to get ncodes sepcified for downloads.
        Args:
            path_to_ncodes_data {str}: absolute path to updated ncodes file.
        Returns {pandas-dataframe}: pandas dataframe comprising of ncodes to download
        """
        print("\nSubset ncodes data as per required ncodes...")
        # parameter initialization
        ncodes_data = pd.read_csv(path_to_ncodes_data)
        # subset required categories
        self.partial_ncodes_data = ncodes_data[ncodes_data["to_download"] == True]
        self.partial_ncodes_data = self.partial_ncodes_data.reset_index(drop=True)
        return self.partial_ncodes_data

    def download_speed(self):
        """
        This function is used to calculate network download speed
        Returns {float}: download speed of the connected internet network
        """
        try:
            # parameter initialization
            URL = "http://speedtest.ftp.otenet.gr/files/test1Mb.db"
            FILE_SIZE = 1048.576

            # downlaod a file to test download speed
            start = time.time()
            file = anchor(URL, timeout=7)
            file.read()
            end = time.time()
            time_difference = end - start
            return round(FILE_SIZE / time_difference)
        except:
            return False

    def create_report_json(self, url, image_code, status, spent_time, error_description):
        """
        This function is used to created json for image level download repoort.
        Args:
            url {str}: url of the input image path
            image_code {str}: image-code as per image-url data
            status {str}: status of the image download
            spent_time {int/str}: time required for image download
            error_description {exception/str}: description of the error, if any.

        Returns {dict}: json update with download information
        """
        download_json = {"url": url, "image_code": image_code}
        download_json["time-required"] = spent_time
        download_json["status"] = status
        download_json["description"] = str(error_description)
        return download_json

    def ncode_image_download_sequentially(self, ncode_data, folder_path, verbose=True, max_time=7):
        """
        This function is used to sequentially download images for a particular ncode(object category).
        Args:
            ncode_data {pandas-dataframe}: image-net image urls data for the particular ncode.
            folder_path {str}: absolute path where downloaded images are to be saved.
            verbose {bool}: bool represent wheather to show stats for this ncode(object category) data download.
            max_time {int}: maximum download time that is permitted for an image url.

        Returns:
            ncode_report {pandas-dataframe}: data containing comprehensive summary about every download.
        """
        # variable intialization
        stats_report = list()
        ncode_report = list()

        # initiating sequential image download
        for image_num, url in enumerate(tqdm(ncode_data["img_url"], file=sys.stdout)):
            image_code = ncode_data.loc[image_num, "img_code"]

            _, ext = os.path.splitext(url)
            ext = ".jpg" if ext.lower() not in self.IMAGE_FORMATS else ext

            # check if image already present
            if os.path.exists(os.path.join(folder_path, "Images", image_code + ext)):
                download_json = self.create_report_json(
                    url=url,
                    image_code=image_code + ext,
                    status="done",
                    spent_time="-",
                    error_description="Already present"
                )
                stats_report.append("done")
                ncode_report.append(download_json)
                continue

            # starting the image download
            download_start_time = time.time()
            try:
                # opening from the url
                with anchor(url, timeout=max_time) as request:
                    with open(os.path.join(folder_path, "Images", image_code + ext), 'wb') as f:
                        try:
                            # writing the image to the disk
                            f.write(request.read())
                        except Exception as e:
                            # saving error
                            req_time = round(time.time() - download_start_time, 1)
                            download_json = self.create_report_json(
                                url=url,
                                image_code=image_code + ext,
                                status="SaveError",
                                spent_time=req_time,
                                error_description=str(e)
                            )
                            stats_report.append(download_json["status"])
                            ncode_report.append(download_json)
                            continue

                # download success
                req_time = round(time.time() - download_start_time, 1)
                download_json = self.create_report_json(
                    url=url,
                    image_code=image_code + ext,
                    status="done",
                    spent_time=req_time,
                    error_description="Success"
                )
            except Exception as e:
                # save data if error during download process
                req_time = round(time.time() - download_start_time, 1)
                download_json = self.create_report_json(
                    url=url,
                    image_code=image_code + ext,
                    status="Error",
                    spent_time=req_time,
                    error_description=str(e)
                )

            stats_report.append(download_json["status"])
            ncode_report.append(download_json)


        # stats frequency distribution
        stats_report_json = {x: stats_report.count(x) for x in set(stats_report)}
        _, category_name = os.path.split(folder_path)

        # stats reporting
        print()
        total = sum(stats_report_json.values())
        if verbose:
            if "done" in stats_report_json.keys():
                print("Success/Present : {}/{}".format(stats_report_json["done"], total))
        self.report['total'].append(total)

        if "Error" in stats_report_json.keys():
            http_error = stats_report_json["Error"]
            if verbose:
                print("HTTP/URL/No-image errors : {}/{}".format(http_error, total))
            self.report['error'].append(http_error)

        if "SaveError" in stats_report_json.keys():
            save_error = stats_report_json["SaveError"]
            if verbose:
                print("Writing errors : {}/{}\n".format(save_error, total))
            self.report['save_error'].append(save_error)

        return ncode_report

    def update_image_net_xml(self, path_to_xml, image_name, category_name):
        """
        This function is used to update imagenet xmls as per labelmg xmls.
        Args:
            path_to_xml {str}: path to xml file to be updated
            image_name {str}: image of the image to be update in the xml
            category_name {str}: category name to be update in the xml
        Returns: None

        """
        if os.path.exists(path_to_xml):
            tree = ET.parse(path_to_xml)
            root = tree.getroot()
            for child in root.findall('filename'):
                child.text = image_name
            for child in root.findall('object'):
                if child.find("name").text in image_name:
                    child.find("name").text = category_name
            tree.write(path_to_xml)
        return

    def get_an_image(self, url_data, folder_path, queue_, max_time=7):
        """
        This function is used to download an image from its corresponding url.
        Args:
            url_data {http-link}: url for the image to be downloaded.
            folder_path {str}: folder where the downloded image will be saved.
            queue_{multiprocessing queue}: multiprocessing queue to push the result after asynchronous

        Returns: None
        """
        # initializing variables
        url = url_data[0]
        image_code = url_data[1]
        _, ext = os.path.splitext(url)
        ext = ".jpg" if ext.lower() not in self.IMAGE_FORMATS else ext

        # starting the image download
        download_start_time = time.time()
        try:
            # opening from the url
            with anchor(url, timeout=max_time) as request:
                with open(os.path.join(folder_path, "Images", image_code + ext), 'wb') as f:
                    try:
                        # writing the image to the disk
                        f.write(request.read())
                    except Exception as e:
                        #saving error
                        req_time = round(time.time() - download_start_time,1)
                        download_json = self.create_report_json(
                            url=url,
                            image_code=image_code + ext,
                            status="SaveError",
                            spent_time=req_time,
                            error_description=str(e)
                        )
                        queue_.put(download_json)
                        return
            # download success
            req_time = round(time.time() - download_start_time, 1)
            download_json = self.create_report_json(
                url=url,
                image_code=image_code + ext,
                status="done",
                spent_time=req_time,
                error_description="Success"
            )
            queue_.put(download_json)

        except Exception as e:
            # save data if error during download process
            req_time = round(time.time() - download_start_time, 1)
            download_json = self.create_report_json(
                url=url,
                image_code=image_code + ext,
                status="Error",
                spent_time=req_time,
                error_description=str(e)
            )
            queue_.put(download_json)

    def ncode_image_download_parallelly(self, ncode_data, folder_path, batch_size=None, verbose=True, max_time=7):
        """
        This function is used to parallely download images for a particular ncode(object category).
        Args:
            ncode_data {pandas-dataframe}: image-net image urls data for the particular ncode.
            folder_path {str}: absolute path where downloaded images are to be saved.
            batch_size {int}: number of images to be downloaded simultaneously.
            verbose {bool}: bool represent wheather to show stats for this ncode(object category) data download.
            max_time {int}: maximum download time that is permitted for an image url.

        Returns:
            ncode_report {pandas-dataframe}: data containing comprehensive summary about every download.

        """
        # variable iniialization
        image_urls_batches = list()
        image_urls_complete = list()

        # create (url, imag_code) tuple
        for image_num, url in enumerate((ncode_data["img_url"])):
            image_code = ncode_data.loc[image_num, "img_code"]
            image_urls_complete.append((url, image_code))

        # creating batches of urls
        batch_start = 0
        for i in range(batch_size, len(image_urls_complete), batch_size + 1):
            batch_end = i
            image_urls_batches.append(image_urls_complete[batch_start:batch_end])
            batch_start = i
        image_urls_batches.append(image_urls_complete[batch_start:len(image_urls_complete)])

        ncode_report = []
        stats_report = []
        # starting to create asynchronous download processes

        for batch_data in tqdm(image_urls_batches, file=sys.stdout):
            # initialize variables
            batch_result = []
            report_stats = []
            queue_ = multiprocessing.Queue()
            processes = []
            # create subprocess to initiate simultaneous download process
            for count, url_data in enumerate(batch_data):

                url = url_data[0]
                image_code = url_data[1]
                _, ext = os.path.splitext(url)
                ext = ".jpg" if ext.lower() not in self.IMAGE_FORMATS else ext

                # check if image already present
                if os.path.exists(os.path.join(folder_path, "Images", image_code + ext)):
                    download_json = self.create_report_json(
                        url=url,
                        image_code=image_code + ext,
                        status="done",
                        spent_time="-",
                        error_description="Already present"
                    )
                    report_stats.append("done")
                    batch_result.append(download_json)
                    continue
                process = multiprocessing.Process(target=self.get_an_image, args=(url_data, folder_path, queue_, max_time))
                processes.append(process)
                process.start()

            # waiting for all processes to complete
            for pro in processes:
                pro.join()

            # collecting results from the asynchronous queue
            for pro in processes:
                pro.terminate()
                x = queue_.get()
                if x:
                    batch_result.append(x)
                    report_stats.append(x["status"])
            stats_report.extend(report_stats)
            ncode_report.extend(batch_result)

        # stats frequency distribution
        stats_report_json = {x: stats_report.count(x) for x in set(stats_report)}
        _, category_name = os.path.split(folder_path)

        # stats reporting
        print()
        total = sum(stats_report_json.values())
        if verbose:
            if "done" in stats_report_json.keys():
                print("Success/Present : {}/{}".format(stats_report_json["done"], total))
        self.report['total'].append(total)

        if "Error" in stats_report_json.keys():
            http_error = stats_report_json["Error"]
            if verbose:
                print("HTTP/URL/No-image errors : {}/{}".format(http_error, total))
            self.report['error'].append(http_error)

        if "SaveError" in stats_report_json.keys():
            save_error = stats_report_json["SaveError"]
            if verbose:
                print("Writing errors : {}/{}\n".format(save_error, total))
            self.report['save_error'].append(save_error)

        return ncode_report

    def check_annotations(self, urls_data, annotations_path):
        """
        This function is used find how many images-url have their corresponding annotation.
        Args:
            urls_data {panda-datafram}: imagenet url data comprising of image-code level url
            annotations_path {str}: absolute path to annotation folder

        Returns {panda-datafram}: updated (subset) image url data

        """
        xml_names = os.listdir(annotations_path)
        xml_image_codes = [xml_name.split(".")[0] for xml_name in xml_names]

        url_image_codes = urls_data['img_code'].tolist()

        overlap_image_code_rows = [row_num for row_num, url_image_code in enumerate(url_image_codes) if url_image_code in xml_image_codes]
        trash_xml_no_url = [(xml_name, os.remove(os.path.join(annotations_path, xml_name+".xml"))) for row_num, xml_name in enumerate(xml_image_codes) if xml_name not in url_image_codes]
        num_trash_xml = len(trash_xml_no_url)

        print("{}/{} image urls have annotations available".format(len(overlap_image_code_rows), len(url_image_codes)))
        if num_trash_xml:
            print("{}/{} xml have no image url, deleting.".format(num_trash_xml, len(xml_image_codes)))
        urls_data_required = urls_data.loc[overlap_image_code_rows]
        urls_data_required = urls_data_required.reset_index(drop=True)
        return urls_data_required

    def calculate_parameters(self):
        """
        This functions is used to calculate batch_size and timeoout duration for downaloading.
        Returns:
            batch_size {int}: number of images to be downlaoded simultaneously based on network speed and number of cores.
            max_time {int}: number of max seconds to spend on doownload of an image.
        """
        # calculate download speed
        d_speed = self.download_speed()

        # select batch size and max-time out based on # cores and download speed
        if d_speed:
            d_speed_constant = d_speed / 100
            if d_speed_constant > 4:
                batch_size = multiprocessing.cpu_count() * 4
                max_time = 3
            elif 2.5 < d_speed_constant <= 4:
                batch_size = multiprocessing.cpu_count() * 3
                max_time = 5
            elif 1 <= d_speed_constant <= 2.5:
                batch_size = multiprocessing.cpu_count() * 2
                max_time = 5
            elif 0.2 <= d_speed_constant < 1:
                batch_size = multiprocessing.cpu_count()
                max_time = 7
            else:
                batch_size = int(multiprocessing.cpu_count() / 2)
                max_time = 10
        else:
            batch_size = multiprocessing.cpu_count()
            max_time = 7
        return batch_size, max_time

    def download_partial_imagenet_dataset(self, path_to_url_dataset, path_to_annotations, path_to_save_dataset, only_annotations=False, verbose=True, parallel=True, batch_size_=None):
        """
        This function is used to download imagenet images as per the sepcified subset of ncodes dataset.
        This function will also restructure the dataset as per images and corresponding annoatations.
        Args:
            path_to_url_dataset {str}: absolute path to image-net url dataset.
            path_to_annotations {str}: absolute path to image-net annotations folder.
            path_to_save_dataset {str}: absolute path where the downloaded dataset should be saved.
            verbose {bool}: boolean representing if the ncode level stats should be displayed or not.
            parallel {bool}: boolean representing if the download should happen sequentially or parallelly.

        Returns {str}: absolute path to saved images and annotations.

        """
        # parameter check
        if not os.path.exists(path_to_url_dataset):
            print("Image-net url dataset not present in mentioned folder.\nPlease download from the link mentioned in Readme.\n")
            sys.exit()
        if not os.path.exists(path_to_annotations):
            print("Image-net annotation dataset not present in mentioned folder.\nPlease specify correct annotation path\n")
            sys.exit()
        os.mkdir(path_to_save_dataset) if not os.path.exists(path_to_save_dataset) else 1

        # reading url dataset
        url_data = pd.read_csv(path_to_url_dataset)

        # download image from url
        # "http://www.image-net.org/api/download/imagenet.bbox.synset?wnid="

        # calculating batch-size and time-out duration w.r.t to current network speed
        batch_size, max_time = self.calculate_parameters()
        batch_size = batch_size_ if batch_size_ != None else batch_size

        #logging
        if parallel:
            print("\nDownloading {} images simultaneously".format(batch_size))
        else:
            print("\nDownloading images sequentially")
        print("{} secs is the timeout duration of an image download".format(max_time))

        # initiating download for specified ncodes
        for row_num, code in enumerate(self.partial_ncodes_data["code"]):

            # get object category name as per the ncode and create necessary folder
            category_name = self.partial_ncodes_data.loc[row_num, "name"]
            category_name = re.sub(r"\s+", "", category_name, flags=re.UNICODE)
            folder_path = os.path.join(path_to_save_dataset, category_name)
            if not os.path.exists(folder_path):
                os.mkdir(folder_path)

            # get number of urls to be utilized for download
            how_many = self.partial_ncodes_data.loc[row_num, "how_many"]

            # extract annotation from tar file for this particular ncode(object category)
            print("\nCategory : {} ({})".format(category_name, code))
            annotated_file = os.path.join(path_to_annotations, code + ".tar.gz")
            try:
                shutil.unpack_archive(annotated_file, folder_path)
            except:
                print("Error while extracting annotation from tar file")
                sys.exit()
            files = glob.glob(os.path.join(folder_path, "Annotation", code)+"/*xml")
            for f in files:
                _, xml_name = os.path.split(f)
                if not os.path.exists(os.path.join(folder_path, "Annotation", xml_name)):
                    shutil.move(f, os.path.join(folder_path, "Annotation", xml_name))
            shutil.rmtree(os.path.join(folder_path, "Annotation", code))

            # create image dir, subset imagenet-url data for a particular ncode
            if not os.path.exists(os.path.join(folder_path, "Images")):
                os.mkdir(os.path.join(folder_path, "Images"))
            image_urls = url_data[url_data["code"] == code]
            image_urls = image_urls.reset_index(drop=True)
            total_urls = image_urls.shape[0]

            # subset further if only annotated images required
            if only_annotations:
                image_urls = self.check_annotations(image_urls, os.path.join(folder_path, "Annotation"))
                # if lesser number of images required
                image_urls = image_urls if how_many == -1 else image_urls[:how_many]
                how_many = image_urls.shape[0] if how_many == -1 else how_many
                print("Downloading {}/{} urls with annotation\n".format(how_many, total_urls))

            else:
                image_urls = image_urls if how_many == -1 else image_urls[:how_many]
                # if lesser number of images required
                how_many = "all" if how_many == -1 else how_many
                print("Downloading {}/{} urls\n".format(how_many, total_urls))

            # starting the image download process
            total_start_time = time.time()
            if parallel:
                # starting parallel download
                ncode_report = self.ncode_image_download_parallelly(
                    ncode_data=image_urls,
                    folder_path=folder_path,
                    verbose=verbose,
                    batch_size=batch_size,
                    max_time=max_time
                )
            else:
                # downloading sequentially
                ncode_report = self.ncode_image_download_sequentially(ncode_data=image_urls, folder_path=folder_path, verbose=verbose)

            # restructuring the download report for this ncode
            ncode_dataframe = pd.DataFrame([])
            for data_json in ncode_report:
                ncode_dataframe = ncode_dataframe.append(data_json, ignore_index=True)
            ncode_report_csv_path = os.path.join(folder_path, category_name + "_download_report.csv")
            ncode_dataframe.to_csv(ncode_report_csv_path, index=False)
            print("Download complete in {} secs\n\n".format(time.time() - total_start_time))

            #update xml data
            for image_code in ncode_dataframe["image_code"]:
                name = os.path.splitext(image_code)
                xml_path = os.path.join(folder_path, "Annotation", name[0]+".xml")
                self.update_image_net_xml(xml_path, image_code, category_name)

        # comprehensive download report
        n_total = sum(self.report['total'])
        n_http_error = sum(self.report['error'])
        n_save_error = sum(self.report['save_error'])
        n_downloaded = n_total - (n_http_error+n_save_error)

        # final download report display
        print("\n<<-- Final report -->>")
        print("Total downloaded images: {}/{}".format(n_downloaded, n_total))
        print("Total HTTP/URL/NO-file errors: {}/{}".format(n_http_error, n_total))
        print("Total writing errors: {}/{}\n".format(n_save_error, n_total))
        return path_to_save_dataset
