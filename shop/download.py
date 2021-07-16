import tempfile
import requests


def get_download_link(link):
    API_ENDPOINT = "https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key="
    res = requests.get(f"{API_ENDPOINT}{link}")
    response = res.json().get("href")
    return response


def get_filename(download_link):
    for filename in download_link.strip().split("&"):
        if filename.startswith('filename='):
            return filename.split("=")[1]
    return False


def download_file(file_link):
    download = requests.get(file_link)
    if not download:
        return False
    file = tempfile.NamedTemporaryFile()
    file.write(download.content)
    return file
