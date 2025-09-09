import os, traceback
from typing import Optional
from threading import Thread
from datetime import datetime
import instaloader

from utils import job_dir, write_status, save_results

def run_scrape(job_id: str, username: str, ig_user: Optional[str], ig_pass: Optional[str],
               max_posts: int = 50, only_videos: bool = True):
    """
    Worker: ambil postingan dari username Instagram dan unduh hanya VIDEO.
    Hasil + metadata disimpan ke data/<job_id>/
    """
    write_status(job_id, "running", {"message": "Memulai scraping..."})

    L = instaloader.Instaloader(
        dirname_pattern=os.path.join(job_dir(job_id), "{target}"),
        filename_pattern="{date_utc}_UTC_{shortcode}",
        save_metadata=True,
        download_pictures=not only_videos,
        download_videos=True,
        download_video_thumbnails=True,
        compress_json=False,
        post_metadata_txt_pattern=None
    )

    if ig_user and ig_pass:
        try:
            L.login(ig_user, ig_pass)
        except Exception as e:
            write_status(job_id, "error", {"message": f"Gagal login: {e}"})
            return

    try:
        profile = instaloader.Profile.from_username(L.context, username)
    except Exception as e:
        write_status(job_id, "error", {"message": f"Tidak bisa memuat profile @{username}: {e}"})
        return

    results = []
    count = 0

    try:
        for post in profile.get_posts():
            if max_posts and count >= max_posts:
                break

            if only_videos and not post.is_video:
                continue

            try:
                L.download_post(post, target=profile.username)
                count += 1
                results.append({
                    "shortcode": post.shortcode,
                    "url": f"https://www.instagram.com/p/{post.shortcode}/",
                    "date_utc": post.date_utc.isoformat(),
                    "is_video": post.is_video,
                    "video_url": getattr(post, "video_url", None),
                    "title": post.title or "",
                    "caption": post.caption or "",
                    "likes": getattr(post, "likes", None),
                    "comments": getattr(post, "comments", None),
                    "owner_username": profile.username
                })
                write_status(job_id, "running", {
                    "message": f"Mengunduh {count}/{max_posts}…",
                    "last_shortcode": post.shortcode
                })
            except Exception as e:
                write_status(job_id, "running", {
                    "message": f"Error unduh satu post: {e}"
                })
                continue

        save_results(job_id, results)
        write_status(job_id, "finished", {
            "message": f"Selesai. Terunduh {len(results)} video.",
            "total": len(results)
        })
    except Exception as e:
        write_status(job_id, "error", {
            "message": f"Worker exception: {e}",
            "trace": traceback.format_exc()
        })

def start_worker(*args, **kwargs) -> Thread:
    t = Thread(target=run_scrape, args=args, kwargs=kwargs, daemon=True)
    t.start()
    return t
