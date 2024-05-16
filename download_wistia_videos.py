import logging
import logging.config
import os
import subprocess
import time
from dataclasses import asdict, dataclass

import pycookiecheat
import requests

import local_settings
import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(settings.LOG_FILENAME), logging.StreamHandler()],
)


@dataclass
class Lesson:
    name: str
    position: int
    id: int
    content_type: str
    url: str


@dataclass
class Module:
    name: str
    position: int
    lessons: list


@dataclass
class Course:
    name: str
    modules: list


def run():
    # requires you to have logged in on chrome as the html retrieval and video download is done with cookies
    cookies = pycookiecheat.chrome_cookies(local_settings.WEBSITE_URL)

    for course_url in local_settings.COURSE_URLS:
        title_and_urls = get_title_and_urls(cookies, settings.HOME_DIR, course_url)

        for title, url in title_and_urls:
            download_lesson(settings.DOWNLOAD_DIR, title, url)


def get_title_and_urls(cookies, home_dir, course_url):
    full_course_url = f"{local_settings.WEBSITE_URL}{local_settings.COURSE_PLAYER_URL}courses/{course_url}"
    logging.info(f"Processing {full_course_url}")
    response = requests.get(full_course_url, cookies=cookies)
    validate_response(full_course_url, response)
    filename = os.path.join(home_dir, f"{course_url.replace('/', '_')}.csv")
    if not os.path.exists(filename):
        course = course_from_json(
            response.json(),
            cookies,
            local_settings.WEBSITE_URL + local_settings.COURSE_PLAYER_URL,
        )
        save_course_to_csv(course, filename)
    return load_title_and_urls_from_csv(filename)


def course_from_json(json, cookies, lesson_url):
    contents = dict()
    modules = []
    for content_json in json["contents"]:
        contents[content_json["id"]] = (
            content_json["name"],
            content_json["position"],
            content_json["contentable_id"],
            content_json["contentable_type"],
        )
    for module_json in json["chapters"]:
        lessons = []
        for content_id in module_json["content_ids"]:
            (name, position, id, content_type) = contents[content_id]
            time.sleep(1)
            download_url = get_lesson_url(lesson_url, id, content_type, cookies)
            lesson = Lesson(name, position, id, content_type, download_url)
            lessons.append(lesson)
        sorted_lessons = sorted(lessons, key=lambda x: x.position)
        module = Module(module_json["name"], module_json["position"], sorted_lessons)
        modules.append(module)
    sorted_modules = sorted(modules, key=lambda x: x.position)
    return Course(json["course"]["name"], sorted_modules)


def get_lesson_url(url, lesson_id, content_type, cookies):
    url_part = "audio" if content_type == "Audio" else "lessons"
    response = requests.get(f"{url}{url_part}/{lesson_id}", cookies=cookies)
    validate_response(url, response)
    if content_type == "Audio":
        return response.json()["audio"]["url"]
    else:
        return response.json()["lesson"]["video_url"]


def download_lesson(download_path, path, url):
    video_path = os.path.join(download_path, path).replace("!", "")
    if os.path.exists(video_path):
        logging.info(f"Video already exists {video_path}")
    else:
        logging.info(f"Downloading: {video_path}, url={url}")
        # midquality_format = "bestvideo[height<400]+bestaudio/best[height<400]"
        worst_format = "w"
        command = f'yt-dlp -f "{worst_format}" -o "{video_path}" "{url}"'
        logging.info(f"Running command: {command}")
        subprocess.call(
            command,
            shell=True,
        )


def validate_response(url, response):
    if response.status_code != 200:
        message = f"Failed to get HTML for {url}, response code {response.status_code}"
        logging.error(message)
        raise RuntimeError(message)


def save_course_to_csv(course, filename):
    with open(filename, "w") as file:
        for module in course.modules:
            for i, lesson in enumerate(module.lessons):
                extension = "mp3" if lesson.content_type == "Audio" else "mp4"
                filename = (
                    f"{course.name}/{module.name} - {i + 1}. {lesson.name}.{extension}"
                )
                filename = filename.replace(',', '')
                file.write(
                    f"{filename},{lesson.url},{course.name},{module.position},{module.name},{lesson.position}{lesson.name},{lesson.content_type}\n"
                )


def load_title_and_urls_from_csv(filename):
    title_and_urls = []
    with open(filename, "r") as file:
        for line in file:
            print(line)
            data = line.split(",")
            title_and_urls.append((data[0], data[1]))

        return title_and_urls


run()
