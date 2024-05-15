import logging

from collections import defaultdict
from dataclasses import dataclass
from itertools import groupby

from .html_cache import HtmlCache
from .html_parser import HtmlParser
from .url_utils import UrlUtils
from .video import Video


@dataclass
class Videofinder:
    html_cache: HtmlCache
    excluded_urls: list

    __WEEKS_IN_A_YEAR = 52

    @staticmethod
    def is_value_in_others(d, skip_key, value):
        for key, values in d.items():
            if key != skip_key:
                if value in values:
                    return True
        return False

    def __find_videos_and_links(
        self, url, domain, parent_url, visited_urls, video_urls_by_parent_url
    ):
        logging.info(f"Getting HTML for {url}")
        html = self.html_cache.get_html(url)
        videos = []
        if html is not None:
            html_parser = HtmlParser(self.excluded_urls, domain, html)
            video_url_and_titles = html_parser.find_video_urls_and_titles()
            logging.debug(f"Found {len(video_url_and_titles)} videos for {url}")
            for video_url, title in video_url_and_titles.items():
                if video_url not in visited_urls or not Videofinder.is_value_in_others(
                    video_urls_by_parent_url, parent_url, video_url
                ):
                    logging.info(f"Video found {video_url}")
                    videos.append(Video(title, url, video_url, parent_url))
                    visited_urls.add(video_url)
                    video_urls_by_parent_url[parent_url].add(video_url)
                else:
                    logging.warn(f"Video already found {video_url}")
            links = html_parser.find_urls(visited_urls)
            logging.debug(
                f"Found {links} links for {url} with parent {parent_url}"
            )
        return videos, links

    def __find_videos(self, starting_url):
        visited_urls = set([starting_url])
        domain = UrlUtils.remove_path(starting_url)
        queue = [(starting_url, None)]
        total_videos = []
        video_urls_by_parent_url = defaultdict(set)
        while queue:
            url, parent_url = queue.pop(0)
            videos, links = self.__find_videos_and_links(
                url, domain, parent_url, visited_urls, video_urls_by_parent_url
            )
            total_videos.extend(videos)
            for link in links:
                link = domain + link
                if link not in visited_urls:
                    visited_urls.add(link)
                    queue.append((link, url))
        return total_videos

    def find_videos(self, starting_url):
        videos = self.__find_videos(starting_url)
        print(f"Videos found: {videos}")
        return videos
