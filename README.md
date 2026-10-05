<div align="center">
 
# Satis-py
 
**AI-powered personal news briefing, delivered to Telegram every day at noon.**
 
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?style=flat-square&logo=openai&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=flat-square&logo=telegram&logoColor=white)
 
</div>
 
---
 
## Why I Built This
 
I live between two worlds — Korea and the US.
 
Every morning, I found myself jumping between six different tabs: Korean news, New York local news, New Jersey updates, Big Tech headlines, Apple-related news, and global top stories. It was fragmented, slow, and honestly exhausting.
 
So I built Satis-py. One bot. Six categories. Five stories each. Summarized by AI. In my Telegram. Every day at noon.
 
The name is simple: **Satisfy** + **Python** = **Satis-py**.
Because staying informed should feel good — not like a chore.
 
---
 
## What It Does
 
Every day at **12:00 PM**, Satis-py automatically:
 
1. Fetches the hottest headlines across 6 categories
2. Summarizes each story into one clean line using OpenAI — one request per category, merging stories that cover the same event
3. Delivers everything to Telegram — formatted and ready to read
 
```
📰 오늘의 뉴스 브리핑
 
1️⃣ Headline (tap to open the article)
→ One-line AI summary
 
2️⃣ Headline
→ One-line AI summary
 
3️⃣ Headline
→ One-line AI summary
 
4️⃣ Headline
→ One-line AI summary
 
5️⃣ Headline
→ One-line AI summary
```
 
**Categories covered:**
 
| World | Korea | New York | New Jersey | Big Tech | Apple |
|:---:|:---:|:---:|:---:|:---:|:---:|
| Top 5 | Top 5 | Top 5 | Top 5 | Top 5 | Top 5 (Tuesdays) |

Articles already sent in the last 7 days are skipped and replaced with the next-ranked stories.
If a source returns no articles or loses most article bodies (usually a site layout change), or most OpenAI summaries fail (e.g. exhausted credits), the bot also sends a "⚠️ 뉴스봇 점검 필요" alert.
 
---
 
## Tech Stack
 
| Layer | Tool |
|---|---|
| Language | Python 3.11+ |
| AI Summarization | OpenAI API (GPT-4o-mini) |
| Messaging | Telegram Bot API |
| Scheduling | GitHub Actions (cron) |
 
---
 
## Project Structure
 
```
satis-py/
├── main.py                   ← Entry point: collect → summarize → send
├── news_categories.py        ← Category/source definitions & unseen-article collection
├── google_rss_scraper.py     ← Shared Google News RSS scraper
├── korean_news_scraper.py    ← Naver / Nate / world news
├── us_news_scraper.py        ← New York / New Jersey news
├── bigtech_news_scraper.py   ← Big Tech news
├── news_scraper.py           ← Apple news (9to5Mac / MacRumors)
├── http_client.py            ← HTTP requests with retry
├── summarizer.py             ← OpenAI summarization
├── telegram_sender.py        ← Telegram delivery
├── message_splitter.py       ← Splits long messages to fit Telegram limits
├── seen_articles.py          ← 7-day sent history to skip duplicates
├── health_report.py          ← Detects silently broken scrapers and builds alerts
├── config.py                 ← Environment variable loading
├── check_bot.py              ← Bot connection / Chat ID diagnostic
├── test_*.py                 ← Unit tests
└── .github/workflows/
    ├── news_bot.yml          ← Daily run at noon New York time
    └── tests.yml             ← Runs tests on every push
```
 
---
 
## License
 
Copyright © 2026 David Song. All rights reserved.

This source code is proprietary and confidential. Unauthorized copying, distribution, or use of this software, in whole or in part, is strictly prohibited.
 
---
 
---
 
<div align="center">
 
# Satis-py
 
**AI가 요약한 오늘의 뉴스를, 매일 정오 텔레그램으로.**
 
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?style=flat-square&logo=openai&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=flat-square&logo=telegram&logoColor=white)
 
</div>
 
---
 
## 왜 만들었냐면
 
저는 한국과 미국, 두 세계를 오가며 살고 있습니다.
 
매일 아침마다 탭을 여섯 개씩 열었어요. 한국 뉴스, 뉴욕 로컬 뉴스, 뉴저지 소식, 빅테크 헤드라인, Apple 관련 뉴스, 그리고 세계 빅뉴스. 파편화되고, 느리고, 솔직히 피곤했습니다.
 
그래서 Satis-py를 만들었습니다. 봇 하나. 카테고리 여섯 개. 카테고리별 뉴스 다섯 개. AI 요약. 텔레그램으로. 매일 정오에.
 
이름은 간단합니다: **Satisfy**(만족) + **Python** = **Satis-py**.
정보를 얻는 게 즐거워야 하니까요 — 부담이 아니라.
 
---
 
## 어떻게 작동하냐면
 
매일 **오후 12시**, Satis-py가 자동으로:
 
1. 6개 카테고리에서 가장 핫한 헤드라인 수집
2. OpenAI로 각 뉴스를 한 줄로 요약 — 카테고리당 한 번에 요약하고, 같은 사건을 다룬 기사는 하나로 합침
3. 텔레그램으로 깔끔하게 포맷해서 전송
 
```
📰 오늘의 뉴스 브리핑
 
1️⃣ 뉴스 제목 (누르면 기사로 이동)
→ AI 한 줄 요약
 
2️⃣ 뉴스 제목
→ AI 한 줄 요약
 
3️⃣ 뉴스 제목
→ AI 한 줄 요약
 
4️⃣ 뉴스 제목
→ AI 한 줄 요약
 
5️⃣ 뉴스 제목
→ AI 한 줄 요약
```
 
**커버하는 카테고리:**
 
| 세계 | 한국 | 뉴욕 | 뉴저지 | 빅테크 | 애플 |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 상위 5개 | 상위 5개 | 상위 5개 | 상위 5개 | 상위 5개 | 상위 5개 (화요일) |

최근 7일 안에 이미 보낸 기사는 건너뛰고 다음 순위 기사로 채웁니다.
소스가 기사를 하나도 못 가져오거나 본문을 대부분 놓칠 때(대개 사이트 구조 변경), 또는 OpenAI 요약이 대부분 실패할 때(예: 크레딧 소진) "⚠️ 뉴스봇 점검 필요" 알림도 함께 보냅니다.
 
---
 
## 기술 스택
 
| 레이어 | 기술 |
|---|---|
| 언어 | Python 3.11+ |
| AI 요약 | OpenAI API (GPT-4o-mini) |
| 메시징 | Telegram Bot API |
| 스케줄링 | GitHub Actions (cron) |
 
---
 
## 프로젝트 구조
 
```
satis-py/
├── main.py                   ← 진입점: 수집 → 요약 → 전송
├── news_categories.py        ← 카테고리/소스 정의 & 미전송 기사 수집
├── google_rss_scraper.py     ← 구글 뉴스 RSS 공통 스크래퍼
├── korean_news_scraper.py    ← 네이버 / 네이트 / 세계 뉴스
├── us_news_scraper.py        ← 뉴욕 / 뉴저지 뉴스
├── bigtech_news_scraper.py   ← 빅테크 뉴스
├── news_scraper.py           ← 애플 뉴스 (9to5Mac / MacRumors)
├── http_client.py            ← 재시도 포함 HTTP 요청
├── summarizer.py             ← OpenAI 요약
├── telegram_sender.py        ← 텔레그램 전송
├── message_splitter.py       ← 텔레그램 길이 제한에 맞춰 메시지 분할
├── seen_articles.py          ← 7일 전송 이력으로 중복 기사 제외
├── health_report.py          ← 조용히 깨진 스크래퍼 감지 & 점검 알림 생성
├── config.py                 ← 환경변수 로드
├── check_bot.py              ← 봇 연결 / Chat ID 확인용 진단 스크립트
├── test_*.py                 ← 유닛 테스트
└── .github/workflows/
    ├── news_bot.yml          ← 매일 뉴욕 시간 정오 실행
    └── tests.yml             ← push마다 테스트 실행
```
 
---
 
## 라이선스
 
Copyright © 2026 David Song. All rights reserved.

This source code is proprietary and confidential. Unauthorized copying, distribution, or use of this software, in whole or in part, is strictly prohibited.
