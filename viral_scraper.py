import asyncio
import logging
import aiohttp
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
import requests
from pytrends.request import TrendReq
import praw
# import snscrape.modules.twitter as sntwitter  # 호환성 문제로 주석 처리

logger = logging.getLogger(__name__)

async def get_global_viral_trends():
    """전 세계에서 바이럴 되는 콘텐츠를 수집하는 함수"""
    viral_content = []
    
    try:
        # Reddit Popular에서 인기 콘텐츠 수집
        reddit_content = await get_reddit_popular()
        viral_content.extend(reddit_content[:5])
        
        # 추가 글로벌 소스들을 여기에 추가할 수 있음
        logger.info(f"전세계 바이럴 콘텐츠 {len(viral_content)}개 수집 완료")
        
    except Exception as e:
        logger.error(f"전세계 바이럴 콘텐츠 수집 중 오류 발생: {e}")
    
    return viral_content[:10]

async def get_us_viral_trends():
    """미국에서 바이럴 되는 콘텐츠를 수집하는 함수"""
    viral_content = []
    
    try:
        # Reddit US 관련 서브레딧에서 인기 콘텐츠 수집
        us_reddit_content = await get_reddit_us()
        viral_content.extend(us_reddit_content[:3])
        
        # Hacker News에서 인기 콘텐츠 수집
        hn_content = await get_hackernews_trending()
        viral_content.extend(hn_content[:2])
        
        logger.info(f"미국 바이럴 콘텐츠 {len(viral_content)}개 수집 완료")
        
    except Exception as e:
        logger.error(f"미국 바이럴 콘텐츠 수집 중 오류 발생: {e}")
    
    return viral_content[:5]

async def get_korea_viral_trends():
    """한국에서 바이럴 되는 콘텐츠를 수집하는 함수 (새로운 바이럴 소스 사용)"""
    viral_content = []
    
    try:
        # Google Trends 한국 트렌드
        google_trends = get_google_trends()
        viral_content.extend(google_trends[:3])
        
        # Reddit 밈/인기 콘텐츠
        reddit_content = get_reddit_trending()
        viral_content.extend(reddit_content[:2])
        
        # Twitter 트렌딩 트윗
        twitter_content = get_twitter_trending()
        viral_content.extend(twitter_content[:2])
        
        # TikTok 트렌드 (선택적)
        tiktok_content = get_tiktok_trending()
        viral_content.extend(tiktok_content[:1])
        
        logger.info(f"한국 바이럴 콘텐츠 {len(viral_content)}개 수집 완료 (새로운 소스)")
        
    except Exception as e:
        logger.error(f"한국 바이럴 콘텐츠 수집 중 오류 발생: {e}")
    
    return viral_content[:10]

async def get_reddit_popular():
    """Reddit r/popular에서 인기 콘텐츠 수집"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            url = 'https://www.reddit.com/r/popular.json?limit=10'
            
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    posts = []
                    
                    for post in data['data']['children'][:5]:
                        post_data = post['data']
                        posts.append({
                            'title': post_data.get('title', '제목 없음'),
                            'content': post_data.get('selftext', '')[:200] + '...' if post_data.get('selftext') else '이미지/링크 콘텐츠',
                            'url': f"https://reddit.com{post_data.get('permalink', '')}"
                        })
                    
                    return posts
    except Exception as e:
        logger.error(f"Reddit 인기 콘텐츠 수집 중 오류: {e}")
        return []

async def get_reddit_us():
    """Reddit 미국 관련 서브레딧에서 인기 콘텐츠 수집"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            url = 'https://www.reddit.com/r/UnitedStates.json?limit=5'
            
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    posts = []
                    
                    for post in data['data']['children'][:3]:
                        post_data = post['data']
                        posts.append({
                            'title': post_data.get('title', '제목 없음'),
                            'content': post_data.get('selftext', '')[:200] + '...' if post_data.get('selftext') else '미국 관련 화제',
                            'url': f"https://reddit.com{post_data.get('permalink', '')}"
                        })
                    
                    return posts
    except Exception as e:
        logger.error(f"Reddit 미국 콘텐츠 수집 중 오류: {e}")
        return []

async def get_hackernews_trending():
    """Hacker News에서 인기 콘텐츠 수집"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            url = 'https://hacker-news.firebaseio.com/v0/topstories.json'
            
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    story_ids = await response.json()
                    posts = []
                    
                    # 상위 5개 스토리만 가져오기
                    for story_id in story_ids[:5]:
                        story_url = f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json'
                        async with session.get(story_url, headers=headers, timeout=5) as story_response:
                            if story_response.status == 200:
                                story_data = await story_response.json()
                                posts.append({
                                    'title': story_data.get('title', '제목 없음'),
                                    'content': '해커뉴스에서 화제가 되고 있는 기술/스타트업 관련 콘텐츠',
                                    'url': story_data.get('url', f"https://news.ycombinator.com/item?id={story_id}")
                                })
                    
                    return posts[:2]
    except Exception as e:
        logger.error(f"Hacker News 콘텐츠 수집 중 오류: {e}")
        return []

async def get_naver_realtime_search():
    """네이버 실시간 검색어 관련 콘텐츠 수집"""
    try:
        # 실제 네이버 실시간 검색어 API는 제한적이므로, 
        # 여기서는 예시 데이터를 반환합니다.
        # 실제 구현시에는 네이버 검색 API나 뉴스 API를 사용해야 합니다.
        sample_trends = [
            {
                'title': '네이버 실시간 검색어 1위 관련 이슈',
                'content': '현재 네이버에서 가장 많이 검색되고 있는 키워드와 관련된 화제',
                'url': 'https://www.naver.com'
            },
            {
                'title': '한국 온라인 커뮤니티 화제',
                'content': '국내 주요 온라인 커뮤니티에서 논의되고 있는 핫한 이슈',
                'url': 'https://www.naver.com'
            }
        ]
        
        logger.info("네이버 실시간 검색어 관련 콘텐츠 수집 (샘플 데이터)")
        return sample_trends
        
    except Exception as e:
        logger.error(f"네이버 실시간 검색어 수집 중 오류: {e}")
        return []

async def get_ruliweb_hot():
    """루리웹 핫게에서 인기 콘텐츠 수집"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            url = 'https://bbs.ruliweb.com/community/board/300143'  # 루리웹 자유게시판
            
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    posts = []
                    
                    # 루리웹의 게시글 구조에 맞춰 파싱
                    # 실제 루리웹 구조에 따라 셀렉터를 조정해야 할 수 있습니다
                    articles = soup.select('.board_list_wrapper .subject_link')[:2]
                    
                    for article in articles:
                        title = article.get_text(strip=True)
                        link = article.get('href', '')
                        if link and not link.startswith('http'):
                            link = 'https://bbs.ruliweb.com' + link
                        
                        posts.append({
                            'title': title,
                            'content': '루리웹에서 화제가 되고 있는 게시글',
                            'url': link
                        })
                    
                    if not posts:  # 파싱이 실패했을 경우 샘플 데이터 반환
                        posts = [
                            {
                                'title': '루리웹 커뮤니티 화제글',
                                'content': '루리웹에서 현재 인기를 끌고 있는 게시글',
                                'url': 'https://bbs.ruliweb.com'
                            }
                        ]
                    
                    return posts
                    
    except Exception as e:
        logger.error(f"루리웹 콘텐츠 수집 중 오류: {e}")
        # 오류 발생시 샘플 데이터 반환
        return [{
            'title': '루리웹 핫게 샘플',
            'content': '루리웹 커뮤니티의 인기 게시글 (데이터 수집 중 오류 발생)',
            'url': 'https://bbs.ruliweb.com'
        }]

def get_google_trends():
    """Google Trends에서 실시간 트렌딩 키워드 수집"""
    try:
        pytrends = TrendReq(hl='ko-KR', tz=540)
        trending_searches = pytrends.trending_searches(pn='south_korea')
        
        results = []
        for i, keyword in enumerate(trending_searches[0][:10]):
            pytrends.build_payload([keyword], timeframe='now 1-d', geo='KR')
            interest_data = pytrends.interest_over_time()
            
            description = f"한국에서 급상승 검색어 #{i+1}"
            if not interest_data.empty:
                peak_value = interest_data[keyword].max()
                description += f" (검색량: {peak_value})"
            
            results.append({
                'title': keyword,
                'content': description,
                'url': f"https://trends.google.com/trends/explore?geo=KR&q={keyword}"
            })
        
        return results
        
    except Exception as e:
        logger.error(f"Google Trends 수집 중 오류: {e}")
        return [{
            'title': '샘플 트렌드',
            'content': 'Google Trends 데이터 수집 실패',
            'url': 'https://trends.google.com'
        }]

def get_reddit_trending():
    """Reddit에서 인기 글 수집 (PRAW 사용)"""
    try:
        reddit = praw.Reddit(
            client_id="YOUR_CLIENT_ID",
            client_secret="YOUR_CLIENT_SECRET", 
            user_agent="viral_scraper 1.0 by u/yourusername"
        )
        
        results = []
        
        # r/memes와 r/popular에서 hot 포스트 수집
        for subreddit_name in ['memes', 'popular']:
            subreddit = reddit.subreddit(subreddit_name)
            for post in subreddit.hot(limit=5):
                content = post.selftext[:200] if post.selftext else "이미지/링크 콘텐츠"
                if post.url and any(ext in post.url for ext in ['.jpg', '.png', '.gif', '.webp']):
                    content = f"이미지 콘텐츠: {post.url}"
                
                results.append({
                    'title': post.title,
                    'content': content,
                    'url': f"https://reddit.com{post.permalink}"
                })
        
        return results[:10]
        
    except Exception as e:
        logger.error(f"Reddit 데이터 수집 중 오류: {e}")
        # Reddit API 없이 웹 스크래핑으로 대체
        try:
            response = requests.get('https://www.reddit.com/r/memes.json', 
                                  headers={'User-Agent': 'viral_scraper'})
            if response.status_code == 200:
                data = response.json()
                results = []
                for post in data['data']['children'][:10]:
                    post_data = post['data']
                    results.append({
                        'title': post_data.get('title', '제목 없음'),
                        'content': post_data.get('selftext', '')[:200] or '이미지/링크 콘텐츠',
                        'url': f"https://reddit.com{post_data.get('permalink', '')}"
                    })
                return results
        except Exception as fallback_e:
            logger.error(f"Reddit 웹 스크래핑 대체 방법도 실패: {fallback_e}")
            
        return [{
            'title': '샘플 Reddit 포스트',
            'content': 'Reddit 데이터 수집 실패',
            'url': 'https://reddit.com/r/memes'
        }]

def get_twitter_trending():
    """Twitter에서 트렌딩 트윗 수집 (샘플 데이터)"""
    try:
        # snscrape 호환성 문제로 인해 샘플 데이터 반환
        # 실제 사용시에는 Twitter API v2 또는 다른 방법 사용 권장
        sample_tweets = [
            {
                'title': '@트위터유저1의 바이럴 트윗',
                'content': '요즘 핫한 밈과 짤이 담긴 트위터 트렌딩 콘텐츠',
                'url': 'https://twitter.com'
            },
            {
                'title': '@인플루언서의 화제 트윗',
                'content': '전 세계적으로 화제가 되고 있는 바이럴 트위터 콘텐츠',
                'url': 'https://twitter.com'
            }
        ]
        
        logger.info("Twitter 트렌드 데이터 (샘플)")
        return sample_tweets
        
    except Exception as e:
        logger.error(f"Twitter 데이터 수집 중 오류: {e}")
        return [{
            'title': '샘플 트윗',
            'content': 'Twitter 데이터 수집 실패 - API 제한 또는 연결 오류',
            'url': 'https://twitter.com'
        }]

def get_tiktok_trending():
    """TikTok 트렌딩 콘텐츠 수집 (제한적)"""
    try:
        # TikTok은 공식 API가 제한적이므로 샘플 데이터 반환
        # 실제로는 외부 API나 미러 사이트를 활용해야 함
        sample_trends = [
            {
                'title': '인기 챌린지 #1',
                'content': 'TikTok에서 현재 인기인 댄스 챌린지',
                'url': 'https://www.tiktok.com'
            },
            {
                'title': '바이럴 해시태그 #2',
                'content': 'TikTok 글로벌 트렌딩 해시태그',
                'url': 'https://www.tiktok.com'
            }
        ]
        
        logger.info("TikTok 트렌드 데이터 (샘플)")
        return sample_trends
        
    except Exception as e:
        logger.error(f"TikTok 데이터 수집 중 오류: {e}")
        return []