Rayan Salman 231200

Question 1:
uv init creates pyproject.toml (tracks project metadata and dependencies), .python-version (pins the Python version), hello.py (template entrypoint), and .gitignore (excludes temporary environments). 

Question 2:
dvc init creates the .dvc/ directory (stores DVC internal configurations, remote links, and cache settings) and .dvcignore. .dvcignore and .dvc/config should be pushed to Git so teammates share the same setup, but local cache files inside .dvc/cache must never be pushed to Git. 

Question 3:
Credentials added with --global are stored in your machine's global user config file (%LOCALAPPDATA%\dvc\config on Windows). Alternatives are --local (stores in .dvc/config.local inside the repo) and --system (system-wide). Credentials must never be pushed to GitHub. 

Question 4:
DVC automatically appended /data to your .gitignore file. This prevents Git from tracking large raw binary images, delegating data management entirely to DVC. 

Question 5:
Yes, data.dvc is created in the root directory. It is a small text pointer file containing the MD5 hash of the data directory, total byte size, file count, and relative path (data). 

Question 6:
On GitHub, only the code, .gitignore, configuration, and the lightweight data.dvc pointer file exist (the raw images are not on GitHub). On DagsHub, you can see both code and the actual image dataset because DagsHub integrates directly with DVC storage. 

Question 7:
No, cloning the repository in a new folder will only bring down data.dvc, not the images. To restore the data/ folder, run dvc pull. 

Question 8:
No, food11_processed and food11_processed_mini are no longer in your local folder. git checkout reverted data.dvc back to pointing only to food11_raw, and dvc checkout synced your filesystem to match that exact point in time. 
