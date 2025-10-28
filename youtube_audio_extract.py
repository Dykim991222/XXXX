import argparse
import os
import sys
from typing import Optional

try:
    import yt_dlp
except ImportError:
    print("yt-dlp가 설치되어 있지 않습니다. 먼저 'pip install yt-dlp'를 실행하세요.")
    sys.exit(1)


def ensure_output_directory(output_dir: str) -> None:
    if not output_dir:
        return
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)


def build_postprocessors(audio_format: str, audio_quality: str) -> list:
    # FFmpeg가 필요합니다. (시스템 PATH에 ffmpeg가 있어야 변환 가능)
    # audio_format: mp3 | m4a | wav | flac
    return [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": audio_format,
            "preferredquality": audio_quality,  # mp3일 때 0~320 kbps(예: "192"). wav/flac일 경우 무시됨
        }
    ]


def download_audio(
    url: str,
    output_dir: Optional[str] = None,
    filename: Optional[str] = None,
    audio_format: str = "mp3",
    audio_quality: str = "192",
) -> str:
    if audio_format not in {"mp3", "m4a", "wav", "flac"}:
        raise ValueError("audio_format은 mp3, m4a, wav, flac 중 하나여야 합니다.")

    ensure_output_directory(output_dir or "")

    # 출력 템플릿: 파일명 지정 시 그대로 사용, 아니면 기본 템플릿
    if filename:
        # 확장자는 yt-dlp 후처리 시점에 지정되므로, 여기서는 이름만 템플릿에 둠
        outtmpl = os.path.join(output_dir or "", filename + ".%(ext)s")
    else:
        outtmpl = os.path.join(output_dir or "", "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": outtmpl,
        "postprocessors": build_postprocessors(audio_format, audio_quality),
        "noplaylist": True,
        "quiet": False,
        "prefer_ffmpeg": True,
    }

    # 다운로드 실행
    final_path: Optional[str] = None
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

        # 후처리된 파일 경로 추정: yt-dlp의 prepare_filename은 원본 확장자 기준
        # postprocessor 결과 경로는 info["requested_downloads"][0]["filepath"] 또는 아래 로직으로 보정
        requested = info.get("requested_downloads") or []
        if requested and isinstance(requested, list):
            final_path = requested[0].get("filepath")
        if not final_path:
            # fallback: 확장자 교체 추정
            base = ydl.prepare_filename(info)
            base_root, _ = os.path.splitext(base)
            final_path = f"{base_root}.{audio_format}"

    return os.path.abspath(final_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="YouTube URL에서 오디오를 추출합니다.")
    parser.add_argument("url", help="유튜브 동영상 URL")
    parser.add_argument("--out", dest="output_dir", default="", help="출력 디렉토리 (기본: 현재 폴더)")
    parser.add_argument("--name", dest="filename", default="", help="출력 파일명(확장자 제외). 미지정시 제목 기반")
    parser.add_argument(
        "--format",
        dest="audio_format",
        default="mp3",
        choices=["mp3", "m4a", "wav", "flac"],
        help="오디오 포맷 (기본: mp3)",
    )
    parser.add_argument(
        "--quality",
        dest="audio_quality",
        default="192",
        help="오디오 품질 kbps (mp3/m4a에 적용, 기본: 192)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        result_path = download_audio(
            url=args.url,
            output_dir=args.output_dir or None,
            filename=args.filename or None,
            audio_format=args.audio_format,
            audio_quality=args.audio_quality,
        )
        print(f"완료: {result_path}")
    except yt_dlp.utils.DownloadError as e:
        print(f"다운로드 오류: {e}")
        sys.exit(2)
    except Exception as e:
        print(f"오류: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


