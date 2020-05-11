import dropbox
import datetime
import pandas as pd
import os
import json

year = datetime.datetime.today().year
pd.options.mode.chained_assignment = None
config = json.loads(open("./config.json").read())
source_folder = config["sourceFolder"]
destination_folder = config["destinationFolder"]
dbx = dropbox.Dropbox(config["accessToken"])
# dbx.users_get_current_account()

class ClutterFree:
    def __init__(self):
        self.check_extention = ['.jpg', '.docx', '.png']

    def cleanDownloadsFolder(self):
        download_path = ''
        upload_path = ''
        for filename in os.listdir(source_folder):
            if any(ext in filename for ext in self.check_extention):
                print(filename)
                download_path = (os.path.join(source_folder,filename))
                upload_path = (os.path.join(destination_folder,filename))
            else:
                print("Downloads folder is empty..")
            with open(download_path, "rb") as file:
                dbx.files_upload(file.read(), upload_path, mute=True)
                os.remove(download_path)

if __name__ == '__main__':
    ct_free = ClutterFree()
    ct_free.cleanDownloadsFolder()
