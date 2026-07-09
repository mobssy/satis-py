from google_rss_scraper import fetch_google_rss_news


def get_nj_hot_news() -> list[dict]:
    return fetch_google_rss_news("new+jersey", "뉴저지")


def get_ny_hot_news() -> list[dict]:
    return fetch_google_rss_news("new+york", "뉴욕")
