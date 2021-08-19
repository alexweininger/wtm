import os

from git import Repo

def get_remote_name():
    try:
        repo = Repo('.')
        remote_url = repo.remotes[0].config_reader.get("url")  # e.g. 'https://github.com/abc123/MyRepo.git'
        return os.path.splitext(os.path.basename(remote_url))[0]  # 'MyRepo'
    except:
        return os.path.basename(os.path.abspath('.'))
