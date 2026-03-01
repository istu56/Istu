import os
import re
import random
import aiofiles
import aiohttp

from PIL import Image, ImageEnhance, ImageOps
from unidecode import unidecode
from youtubesearchpython.__future__ import VideosSearch

from ISTKHAR_MUSIC import app
from config import YOUTUBE_IMG_URL

# Ensure cache folder exists
os.makedirs("cache", exist_ok=True)


def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    return image.resize((newWidth, newHeight))


def clear(text):
    words = text.split(" ")
    title = ""
    for word in words:
        if len(title) + len(word) < 60:
            title += " " + word
    return title.strip()


async def get_thumb(videoid):
    final_path = f"cache/{videoid}.png"

    if os.path.isfile(final_path):
        return final_path

    url = f"https://www.youtube.com/watch?v={videoid}"

    try:
        results = VideosSearch(url, limit=1)
        data = await results.next()

        if not data["result"]:
            return YOUTUBE_IMG_URL

        result = data["result"][0]

        # Safe title clean (Python 3.12 fix)
        try:
            title = result.get("title", "Unsupported Title")
            title = re.sub(r"\W+", " ", title)
            title = title.title()
        except:
            title = "Unsupported Title"

        duration = result.get("duration", "Unknown")
        thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        views = result.get("viewCount", {}).get("short", "Unknown Views")
        channel = result.get("channel", {}).get("name", "Unknown Channel")

        thumb_path = f"cache/thumb_{videoid}.png"

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    async with aiofiles.open(thumb_path, "wb") as f:
                        await f.write(await resp.read())
                else:
                    return YOUTUBE_IMG_URL

        youtube = Image.open(thumb_path)
        image1 = changeImageSize(1280, 720, youtube)

        # Enhance Image
        bg_bright = ImageEnhance.Brightness(image1).enhance(1.1)
        bg_contra = ImageEnhance.Contrast(bg_bright).enhance(1.1)

        colors = [
            "white", "red", "orange", "yellow",
            "green", "cyan", "blue", "violet", "pink"
        ]
        border_color = random.choice(colors)

        final_image = ImageOps.expand(bg_contra, border=7, fill=border_color)
        final_image = changeImageSize(1280, 720, final_image)

        # Remove temporary thumb
        try:
            os.remove(thumb_path)
        except:
            pass

        final_image.save(final_path)
        return final_path

    except Exception as e:
        print("Thumbnail Error:", e)
        return YOUTUBE_IMG_URL