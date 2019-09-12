import pandas as pd


#url_data_path
url_data = pd.DataFrame([])
url_data_path = "/Users/sanjyotzade/Documents/youplus_projects/brand_safety/data_preparation/imageNet/fall11_urls.txt"
# url_data = pd.read_csv(url_data_path,header=None,sep="\t",encoding="latin1")
url_txt_data = open(url_data_path, "r",encoding="latin1")
x = url_txt_data.readlines()
url_data_dict = { path.split("\t")[0] : (path.split("\t")[-1]).split("\n")[0] for path in x }
url_txt_data.close()
url_data["img_code"] = url_data_dict.keys()
url_data["img_url"] = url_data_dict.values()
url_data["code"] = url_data['img_code'].str.split('_').str[0]

print (url_data.head())
url_data.to_csv("imageNet_urls.csv",index=False)