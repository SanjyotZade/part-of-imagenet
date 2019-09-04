
# part-of-imagenet 
- - - -

This repository an open source project that can help you download **portions of imagenet datasets** within minutes,
for your personal/profession custom object localization development. Most of the process is automated, all you need 
to do is **run a few scripts**, **wait for download to complete** and **train your custom model**.

## Imagenet dataset
- - - -
As well are aware imagenet is a huge dataset and is most popular in object localization benchmarking. However at
times, we only require a subset of annotations&images for a particular category. For example the problem at hand is 
*"boxes detection in wearhouse's camera feed"*. In this case, download images with annotation from the category 
**carton** in imagenet dataset and train !

## Getting started with download  
- - - -

Create a virtual environment and install all dependencies as *requirement.txt*. 

#### Download ncodes data (one time process)
**ncodes data** comprising of all the different categories available in imagenet-dataset along with their corresponding
category code. From the part-of-imagenet folder:
```
python download_ncodes_imagenet.py
``` 

Default ncodes data will be downloded to project folder. Alternately, you can also specify an folder where to download 
the ncodes data. 
```
python download_ncodes_imagenet.py --ncodes_dir <path-to-ncode-data-folder>
```

Note: 

ncode's data can also be downloaded manually from
```
http://sanjyot.info
```
#### Download imagenet imageNetURLs data (one time process)
**imagenet imageURL** is a csv file comprising of links to all the images in imagenet dataset as per their ncode's.

"imagenet imageURL.zip" is ~500 MB file(It will take some time to download this file). Download and extract the imagenet 
imageURL.zip file from the link below: 
```
http://sanjyot.info
```
or Alternately (code will take some time to download ~500MB), 
```
python download_ncodes_imagenet.py --with_url_data True
```

#### Marks the categories to download (as required)
The ncode dataset is a csv file comprising of *code, name, to_download* and *how_many* as columns. 

| code        |          name              |  to_download |  how_many |
|:-----------:|:--------------------------:|:------------:|:---------:|
| n02119789   | kit fox, Vulpes macrotis   |False         |    -1     |
| n02100735   | English setter	           |False         |    -1     |
| n02390258   | hinny	                   |False         |    -1     |
| n02110185   | Siberian husky	           |False         |    -1     |
| n02391617   | quagga, Equus quagga	   |False         |    -1     |
| n02129991   | liger	                   |False         |    -1     |

- **ncode**:  imagenet category codes
- **name**:  actual name of imagenet category
- **to_download**:  which categories to download
- **ncode**:  how many image-urls for an selected categories should be considered for download

1. Mark the category from *"False"* to *"True"* in "to_download" column in ncode data.
2. Default value in "how_many" column is "-1". Implies it will download from all the available urls.
3. If you want to consider only "x" number of urls for download, update that number for that particular category in "how_many" column. 
4. Save the ncode data.

#### Initiate the download process
Assumption,
- **"imageURL.csv"** is present in the same folder as "extract_images_as_per_tags.py" file.
- **Updated "ncode"** is present in the same folder as "extract_images_as_per_tags.py" file.
- **Annotation folder** comprising for imagenet xml's as per ncodes is present in the same folder as "extract_images_as_per_tags.py" file.  

Default result folder: Results will be saved to a folder called "partial_imagenet" in the same project folder. If not present,
the folder will be created.
```
python extract_images_as_per_tags.py
``` 

**A download report for each ncode(object categpry)** will be saved to the same folder where images and annotations are saved.

If you wish to download, only the images which has corresponding annotation. By default more images will be downloaded than
number of annotation for a particular ncode(object categpry). As imagenet, contains more image-urls than corresponding annotations.

```
python extract_images_as_per_tags.py --with_annotation True
``` 

##### Other parameters
There are several other parameters that can be changed as per user's requirement. The description of available parameters
is mentioned below. Use the parameters while initiating download process as mentioned in an example above.

**with_annotation**('--with_annotation', default: False): This parameter can used to specify if the user wish to download 
all the images using complete image-urls or only the images which has corresponding annotation(xml file).

**parallel**('--parallel', default: True): This parameter can used to initiate the download parallelly or sequentially.

**verbose**('--verbose', default: True): This parameter can used to specify whether to log ncode-level download statics 
while data download.

**batch_size**('--batch_size', default: calculated based on network speed and number of cpu cores): This parameter can used 
to set the number of files to be downloaded simultaneously. NOT RECOMMENDED changing this parameter, as the framework itself
calculate best batch size based on your internet speed and number of cpu core.

**annotations_dir**('--annotations_dir', default: path to "Annotation" folder in project folder): This parameter can be 
used to set the path for your annotation data folder (if changed).

**save_dir**('--save_dir', default: path to project folder): This parameter can be used to set directory where the 
downloaded images and corresponding xml's will be saved.

**url_data**('--url_data', default: path to imageNetURLs.csv in project folder): This parameter can be used to specify the 
path to "mageNetURLs.csv".

**ncode_data**('--ncode_data', default: path to ncodes.csv in project folder): This parameter can be used to specify the 
path to "ncodes.csv".


#### Structure of result directory
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

- - - -

#### Latency analysis  

| Network speed        |          Categories specified         |                 Download specifications                     |  total download time(mins) |
|:--------------------:|:-------------------------------------:|:-----------------------------------------------------------:|:--------------------------:|
|~ 400 MB/sec          | ["hinny", "Siberian husky", "liger"]  | with_annotation=True, parallel=True, downloading all images |                            |
|~ 100 MB/sec          | ["hinny", "Siberian husky", "liger"]  | with_annotation=True, parallel=True, downloading all images |                            |
|~ 10 MB/sec           | ["hinny", "Siberian husky", "liger"]  | with_annotation=True, parallel=True, downloading all images |                            |

Note:
- The network speed (download speed) was taken from "https://fast.com/"

[![Love](https://forthebadge.com/images/badges/built-with-love.svg)](https://github.com/Sanjyot22/CNN-classification-hub)

*Author:[Sanjyot Zade](http://www.sanjyot.info/)*
