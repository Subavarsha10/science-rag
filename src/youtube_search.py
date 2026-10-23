
import os

from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


def search_youtube_videos(topic, max_results=6):
    """Search YouTube for educational videos about a Science topic."""

    topic = topic.strip()

    if not topic:
        return {
            "videos": [],
            "error": "Please enter a Science topic."
        }

    if not YOUTUBE_API_KEY:
        return {
            "videos": [],
            "error": (
                "YouTube API key not found. "
                "Check YOUTUBE_API_KEY in your project's .env file."
            )
        }

    max_results = max(1, min(int(max_results), 10))

    try:
        youtube = build(
            "youtube",
            "v3",
            developerKey=YOUTUBE_API_KEY,
            cache_discovery=False
        )

        response = youtube.search().list(
            part="snippet",
            q=f"Class 10 CBSE Science {topic} educational explanation",
            type="video",
            maxResults=max_results,
            order="relevance",
            safeSearch="strict"
        ).execute()

        videos = []

        for item in response.get("items", []):
            snippet = item.get("snippet", {})
            video_id = item.get("id", {}).get("videoId")

            if not video_id:
                continue

            thumbnails = snippet.get("thumbnails", {})
            thumbnail = (
                thumbnails.get("high")
                or thumbnails.get("medium")
                or thumbnails.get("default")
                or {}
            )

            videos.append({
                "title": snippet.get("title", "Untitled video"),
                "channel": snippet.get("channelTitle", "Unknown channel"),
                "description": snippet.get("description", ""),
                "published_at": snippet.get("publishedAt", ""),
                "video_id": video_id,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail": thumbnail.get("url", "")
            })

        return {"videos": videos, "error": None}

    except HttpError as error:
        status = getattr(error.resp, "status", None)

        if status == 403:
            message = (
                "YouTube API access was denied. Check that YouTube Data "
                "API v3 is enabled, the API key is correct, and your "
                "project has available quota."
            )
        else:
            message = f"YouTube API request failed: {error}"

        return {"videos": [], "error": message}

    except Exception as error:
        return {
            "videos": [],
            "error": f"Could not search YouTube: {error}"
        }


if __name__ == "__main__":
    topic = input("Enter a Class 10 Science topic: ").strip()
    result = search_youtube_videos(topic)

    if result["error"]:
        print("\nError:", result["error"])
    elif not result["videos"]:
        print("\nNo videos found. Try another topic.")
    else:
        for number, video in enumerate(result["videos"], start=1):
            print(f"\n{number}. {video['title']}")
            print("Channel:", video["channel"])
            print("Link:", video["url"])
