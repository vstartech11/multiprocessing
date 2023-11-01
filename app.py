# Bintang Villa Devara 11211024
import asyncio
import time
from random import randint

import httpx
import requests
from flask import Flask
from concurrent.futures import ProcessPoolExecutor

app = Flask(__name__)

img_list_count = 10


@app.route("/")
def hello_world():  # put application's code here
    return "Hello World!"


def get_xkcd_image():
    random = randint(0, 300)
    response = requests.get(f"https://xkcd.com/{random}/info.0.json")
    return response.json()["img"]


def get_multiple_images(number):
    return [get_xkcd_image() for _ in range(number)]


@app.get("/comic")
def hello():
    start = time.perf_counter()
    urls = get_multiple_images(img_list_count)
    end = time.perf_counter()

    markup = f"Time taken: {end-start}<br><br>"
    for url in urls:
        markup += f'<img src="{url}"></img><br><br>'

    return markup


# run in async here ...
# function converted to coroutine
async def get_xkcd_image_async(session):
    random = randint(0, 300)
    result = await session.get(
        f"https://xkcd.com/{random}/info.0.json"
    )  # don't wait for the response of API
    return result.json()["img"]


# function converted to coroutine
async def get_multiple_images_async(number):
    async with httpx.AsyncClient() as session:  # async client used for async functions
        tasks = [get_xkcd_image_async(session) for _ in range(number)]
        # gather used to collect all coroutines and run them using loop and get the ordered response
        result = await asyncio.gather(*tasks, return_exceptions=True)
    return result


def get_xkcd_image_wrapper(_):
    return get_xkcd_image()


def get_multiple_images_multiprocessing(number):
    with ProcessPoolExecutor() as executor:
        urls = executor.map(get_xkcd_image_wrapper, range(number))
    return urls


@app.get("/comic_multiprocessing")
def hello_multiprocessing():
    start = time.perf_counter()
    urls = get_multiple_images_multiprocessing(img_list_count)
    end = time.perf_counter()
    markup = f"Time taken: {end-start}<br><br>"
    for url in urls:
        markup += f'<img src="{url}"></img><br><br>'

    return markup


@app.get("/comic_async")
async def hello_async():
    start = time.perf_counter()
    urls = await get_multiple_images_async(img_list_count)
    end = time.perf_counter()
    markup = f"Time taken: {end-start}<br><br>"
    for url in urls:
        markup += f'<img src="{url}"></img><br><br>'

    return markup


if __name__ == "__main__":
    app.run(debug=True)
