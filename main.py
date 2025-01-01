import os
from ytm_dl import *

def main():
    try:
        plist_url, download_dir = readconfs()
        if os.path.isdir(download_dir):
            pass
        else:
            os.mkdir(download_dir)
        
        pl = playlist(plist_url, download_dir)
        pl.download_videos()
    except Exception as e:
        print(f"Exception occured: \n{e}. \nUpload this issue to the repository if unsolvable.")
if __name__ == "__main__":
    main()
