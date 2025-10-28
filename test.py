import os
import re
import sys
import urllib.parse
from typing import Generator, List, Optional

import requests


YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"


def extract_video_id(youtube_url: str) -> Optional[str]:
    """Extracts a YouTube video ID from various URL formats.

    Supported examples:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/shorts/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    """
    try:
        parsed = urllib.parse.urlparse(youtube_url)
        if parsed.netloc.endswith("youtu.be"):
            candidate = parsed.path.lstrip("/")
            return candidate or None

        if parsed.netloc.endswith("youtube.com"):
            if parsed.path == "/watch":
                qs = urllib.parse.parse_qs(parsed.query)
                return (qs.get("v", [None])[0])
            # shorts or embed formats
            m = re.match(r"^/(shorts|embed)/([a-zA-Z0-9_-]{6,})", parsed.path)
            if m:
                return m.group(2)
        return None
    except Exception:
        return None


def iter_comment_threads(api_key: str, video_id: str, page_size: int = 100) -> Generator[dict, None, None]:
    params = {
        "part": "snippet,replies",
        "videoId": video_id,
        "maxResults": page_size,
        "order": "time",
        "textFormat": "plainText",
        "key": api_key,
    }
    next_page_token: Optional[str] = None
    while True:
        if next_page_token:
            params["pageToken"] = next_page_token
        resp = requests.get(f"{YOUTUBE_API_BASE}/commentThreads", params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        for item in data.get("items", []):
            yield item
        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break


def iter_all_replies_for_parent(api_key: str, parent_id: str, page_size: int = 100) -> Generator[dict, None, None]:
    params = {
        "part": "snippet",
        "parentId": parent_id,
        "maxResults": page_size,
        "textFormat": "plainText",
        "key": api_key,
    }
    next_page_token: Optional[str] = None
    while True:
        if next_page_token:
            params["pageToken"] = next_page_token
        resp = requests.get(f"{YOUTUBE_API_BASE}/comments", params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        for item in data.get("items", []):
            yield item
        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break


def collect_reply_texts_only(api_key: str, video_id: str) -> List[str]:
    reply_texts: List[str] = []
    for thread in iter_comment_threads(api_key, video_id):
        snippet = thread.get("snippet", {})
        total_reply_count = snippet.get("totalReplyCount", 0)
        if not total_reply_count:
            continue

        parent_id = thread.get("id")
        if not parent_id:
            continue

        for comment in iter_all_replies_for_parent(api_key, parent_id):
            comment_snippet = comment.get("snippet", {})
            text = comment_snippet.get("textOriginal") or comment_snippet.get("textDisplay")
            if not text:
                continue
            # Basic cleanup: strip extraneous whitespace
            cleaned = text.strip()
            if cleaned:
                reply_texts.append(cleaned)

    return reply_texts


def main() -> None:
    if len(sys.argv) >= 2:
        youtube_url = sys.argv[1]
    else:
        youtube_url = input("YouTube 링크를 입력하세요: ").strip()

    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        api_key = input("YouTube Data API 키를 입력하세요 (또는 환경변수 YOUTUBE_API_KEY 설정): ").strip()

    video_id = extract_video_id(youtube_url)
    if not video_id:
        print("유효한 유튜브 링크가 아닙니다.")
        sys.exit(1)

    try:
        replies = collect_reply_texts_only(api_key, video_id)
    except requests.HTTPError as http_err:
        print(f"API 요청 실패: {http_err}")
        sys.exit(1)
    except requests.RequestException as req_err:
        print(f"네트워크 오류: {req_err}")
        sys.exit(1)

    if not replies:
        print("답글이 없습니다.")
        return

    for idx, text in enumerate(replies, start=1):
        print(f"[{idx}] {text}")


if __name__ == "__main__":
    main()
