import argparse
import logging
import logging.config
import settings
import local_settings
from src.file_utils import FileUtils
from src.html_cache import HtmlCache
from src.url_utils import UrlUtils
from src.video_csv_writer import VideoCsvWriter
from src.video_downloader import VideoDownloader
from src.video_finder import Videofinder


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(settings.LOG_FILENAME), logging.StreamHandler()],
)


def run():
    # requires you to have logged in on chrome as the html retrieval and video download is done with cookies
    cookies = UrlUtils.get_cookies(local_settings.WEBSITE_URL)

    # Stores the html locally, useful for debugging
    html_cache = HtmlCache(settings.HTML_CACHE_DIR, cookies)

    FileUtils.create_dir_if_not_exists(settings.CSV_DIR)
    video_downloader = VideoDownloader(settings.DOWNLOAD_DIR)

    # Recursively (breadth first) searches HTML for urls and embedded videos and writes a CSV
    video_finder = Videofinder(
        html_cache, settings.URL_EXCLUDE_LIST
    )
    videos = video_finder.find_videos(local_settings.WEBSITE_URL + local_settings.LANDING)
    # filtered_videos = video_downloader.filter_videos(videos)
    # video_csv_writer = VideoCsvWriter(settings.CSV_FILEPATH)
    # video_csv_writer.write_videos_to_csv(filtered_videos)

run()
