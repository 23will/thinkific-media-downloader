import csv
import logging
import os
from dataclasses import dataclass
import subprocess

from .file_utils import FileUtils
from .video import Video


@dataclass
class VideoDownloader:
    download_path: str
    base_url: str = None

    def __get_videos_by_section(self, csv_filepath):
        with open(csv_filepath, "r") as stream:
            csv_reader = csv.reader(stream)
            next(csv_reader)
            videos_by_section = dict()
            for row in csv_reader:
                section, name, embedded_url, parent_url, url, _ = row
                video = Video(name, url, embedded_url, parent_url)
                if section in videos_by_section:
                    videos_by_section[section].append(video)
                else:
                    videos_by_section[section] = [video]
            return videos_by_section

    def download_video(self, embedded_url, url, title, output_path=""):
        video_path = self.__video_path(title, output_path)
        if os.path.exists(video_path):
            logging.debug(f"Video already exists {video_path}")
        else:
            logging.info(
                f"Downloading: {video_path}, embedded_url={embedded_url}, url={url}"
            )
            midquality_format = "bestvideo[height<400]+bestaudio/best[height<400]"
            # worst_format = "w"
            command = f'yt-dlp -f "{midquality_format}" -o "{video_path}" --referer "{url}" "{embedded_url }"'
            logging.info(f"Running command: {command}")
            subprocess.call(
                command,
                shell=True,
            )

    def __video_path(self, title, output_path=""):
        path = self.download_path if output_path == "" else output_path
        video_path = os.path.join(path, f"{title}.mp4")
        if not os.path.exists(video_path):
            print(video_path)
        return video_path

    def filter_videos(self, videos):
        return {
            k: v
            for k, v in videos.items()
            if not os.path.exists(
                self.__video_path(k[1], os.path.join(self.download_path, k[0]))
            )
        }

    def download_videos(self, csv_filepath):
        videos_by_section = self.__get_videos_by_section(csv_filepath)
        for section, videos in videos_by_section.items():
            output_path = FileUtils.create_dir_if_not_exists(
                self.download_path, section
            )
            for video in videos:
                self.download_video(
                    video.embedded_url, video.url, video.title, output_path
                )
