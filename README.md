# part-of-imagenet       <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/tensorhub.svg?style=flat">  


This repository an open source project that can help you download **portions of imagenet datasets** within minutes,
for your personal/profession custom object localization development. Most of the process is automated, all you need 
to do is **run a few scripts**, **wait for download to complete** and **train your custom model**.

## Imagenet dataset

As we are aware imagenet is a huge dataset and is most popular in object localization benchmarking. However at
times, we only require a subset of annotations&images for a particular category. For example the problem at hand is 
*"boxes detection in warehouse's camera feed"*. In this case, download images with annotation from the category 
**"carton"** in imagenet dataset and train !

## Quick Start
- Install all dependencies using "requirement.txt".
- Download ncode & imageNetURLs data(for manual download [ncodes_data](https://model-specific-public-storage.s3.amazonaws.com/part-of-imagenet/ncodes.csv), [imageNetURLs](https://model-specific-public-storage.s3.amazonaws.com/part-of-imagenet/imageNetUrls.zip)):
```
python download_imagenet_prerequisites.py
``` 
Note: 'imageNetURLs' is a ~338MB. It might take some time to download. If downloading manually extract csv from zip file.
- Update "to_download" column in ncode csv.
- Initiate the download for the categories updated in ncode csv.
```
python extract_images_as_per_tags.py
``` 

## Comprehensive walk-through and more..
   
Create a virtual environment and install all dependencies using *requirement.txt*. 

### 1. Download ncodes data (one time process)
**ncodes data** comprising of all the different categories available in imagenet-dataset along with their corresponding
category code. 

From the project folder, run:
```
python download_imagenet_prerequisites.py
``` 

Default ncodes data will be downloded to project folder. Alternately, you can also specify an folder where to download 
the ncodes data. 
```
python download_imagenet_prerequisites.py --ncodes_dir <path-to-ncode-data-folder>
```

Note: 
ncode's data can also be downloaded manually from [ncodes_data](https://model-specific-public-storage.s3.amazonaws.com/part-of-imagenet/ncodes.csv)

### 2. Download imageNetURLs data (one time process)
**imageNetURLs** is a csv file comprising of links to all the images in imagenet dataset as per their ncode's.

imageNetURLs data is ~338 MB file(It will take some time to download this file). Download and extract the imagenet 
imageNetURLs.zip file from the [imageNetURLs](https://model-specific-public-storage.s3.amazonaws.com/part-of-imagenet/imageNetUrls.zip).

or Alternately, you can also use:
```
python download_imagenet_prerequisites.py
```

### 3. Mark the categories to download (as required)
The ncode dataset is a csv file comprising of *code, name, to_download* and *how_many* as columns. 

| code        |          name              |  to_download |  how_many |
|:-----------:|:--------------------------:|:------------:|:---------:|
| n02119789   | kit fox, Vulpes macrotis   |False         |    -1     |
| n02100735   | English setter	           |False         |    -1     |
| n02390258   | hinny	                   |False         |    -1     |
| n02110185   | Siberian husky	           |False         |    -1     |
| n02391617   | quagga, Equus quagga	   |False         |    -1     |
| n02129991   | liger	                   |False         |    -1     |
|     :       | :	                       |:             |    :      |

- **ncode**:  imagenet category codes
- **name**:  actual name of imagenet category
- **to_download**:  which categories to download
- **how_many**:  how many image-urls for an selected categories should be considered for download

i. Mark the category from *"False"* to *"True"* in "to_download" column in ncode data.

ii. Default value in "how_many" column is "-1". Implies it will download from all the available urls.

iii. If you want to consider only "x" number of urls for download, update that number for that particular category in "how_many" column. 

iv. Save the ncode data.

### 4. Initiate the download process (as required)
Assumption,
- **"imageURL.csv"** is present in the same folder as "extract_images_as_per_tags.py" file.
- **Updated "ncode"** is present in the same folder as "extract_images_as_per_tags.py" file.
- **Annotation folder** comprising for imagenet xml's as per ncodes is present in the same folder as "extract_images_as_per_tags.py" file.  

Default result folder: Results will be saved to a folder called "partial_imagenet" in the project folder. If not present,
the folder will be created.
```
python extract_images_as_per_tags.py
``` 

**A download report for each ncode(object category)** will be saved to the same folder where images and annotations are saved.

If you wish to download, only the images which has corresponding annotation. By default more images will be downloaded than
number of annotation for a particular ncode(object category). As imagenet, contains more image-urls than corresponding annotations.

```
python extract_images_as_per_tags.py --with_annotation True
``` 

## Other parameters
There are several other parameters that can be changed as per user's requirement. The description of available parameters
is mentioned below. Use the parameters while initiating download process as mentioned in an example above.

**with_annotation**('--with_annotation', default: False): This parameter can used to specify if the user wish to download 
all the images using complete image-url's or only the images which has corresponding annotation(xml file).

**parallel**('--parallel', default: True): This parameter can used to initiate the download parallelly or sequentially.

**verbose**('--verbose', default: True): This parameter can used to specify whether to log ncode-level download statics 
while data download.

**batch_size**('--batch_size', default: calculated based on network speed and number of cpu cores): This parameter can used 
to set the number of files to be downloaded simultaneously. NOT RECOMMENDED changing this parameter, as the framework itself
calculate best batch size based on your internet speed and number of cpu core.

**save_dir**('--save_dir', default: path to project folder): This parameter can be used to set directory where the 
downloaded images and corresponding xml's will be saved.

**annotations_dir**('--annotations_dir', default: path to annotation" folder in project folder): This parameter can be 
used to set the path for your annotation data folder (if changed).

**url_data**('--url_data', default: path to imageNetURLs.csv in project folder): This parameter can be used to specify the 
path to "imageNetURLs.csv".

**ncode_data**('--ncode_data', default: path to ncodes.csv in project folder): This parameter can be used to specify the 
path to "ncodes.csv".


## Structure of result directory
The images, anntations and download_report are stored in an folder as below.

```
partial_imagenet
├── <name-of-category1>
│   ├── Annotation
│   |    ├── <xmls for category1>
│   ├── Images
│   |    ├── <images for category1>
│   ├── category1_download_report.csv
│   |    
├── <name-of-category2>
│   ├── Annotation
│   |    ├── <xmls for category2>
│   ├── Images
│   |    ├── <images for category2>
│   ├── category2_download_report.csv
│   |    
```


## Latency analysis  

| Network speed        |          Categories specified to be downloaded        |                                Download specifications                                 |  total download time(secs) |
|:--------------------:|:-----------------------------------------------------:|:--------------------------------------------------------------------------------------:|:--------------------------:|
|~ 400 MB/sec          |        ["hinny", "Siberian husky", "liger"]           | with_annotation=True, parallel=True, downloading all images(how_many=-1 in codes data) |                            |
|~ 75 MB/sec           |        ["hinny", "Siberian husky", "liger"]           | with_annotation=True, parallel=True, downloading all images(how_many=-1 in codes data) |           139              |
|~ 15 MB/sec           |        ["hinny", "Siberian husky", "liger"]           | with_annotation=True, parallel=True, downloading all images(how_many=-1 in codes data) |           289              |

Note:
- If "with_annotation" is True and "how_many" is "x" in "how_many" column in ncodes csv for a particular category then "x" number of annotated images will be downloaded for that category.
- The network speed (download speed) was taken from "https://fast.com/"

## Support

Feel free to open an issue on or send along a pull request.
If you like the work, show your appreciation by "FORK", "STAR", or "SHARE".

[![Love](https://forthebadge.com/images/badges/built-with-love.svg)](https://github.com/SanjyotZade/part-of-imagenet)

*Author:[Sanjyot Zade](http://www.sanjyot.info/)*
