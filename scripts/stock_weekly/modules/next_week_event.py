import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from playwright.async_api import async_playwright
import re
import json
from collections import defaultdict

# 국가별 아이콘
COUNTRY_ICONS = {
    '미국': '🇺🇸',
    '한국': '🇰🇷',
    '중국': '🇨🇳',
    'US': '🇺🇸',
    'KR': '🇰🇷',
    'CN': '🇨🇳',
    'USA': '🇺🇸',
    'KOR': '🇰🇷',
    'CHN': '🇨🇳'
}

class WeeklyEventCollector:
    def __init__(self):
        self.next_week_dates = self._get_next_week_dates()
        self.events = defaultdict(lambda: {'일정': [], '실적': []})
    
    def _get_next_week_dates(self) -> Dict[str, datetime]:
        """다음 주 월요일부터 금요일까지의 날짜를 가져옵니다."""
        today = datetime.now()
        days_ahead = 7 - today.weekday()  # 다음 주 월요일까지의 일수
        if days_ahead <= 0:  # 이미 월요일이거나 지났으면
            days_ahead += 7
        
        next_monday = today + timedelta(days=days_ahead)
        
        dates = {}
        weekdays_kr = ['월', '화', '수', '목', '금']
        for i, day in enumerate(weekdays_kr):
            dates[day] = next_monday + timedelta(days=i)
        
        return dates
    
    def _get_country_icon(self, text: str) -> str:
        """텍스트에서 국가를 추출하여 아이콘을 반환합니다."""
        text_lower = text.lower()
        
        # 국가별 키워드
        if any(keyword in text_lower for keyword in ['미국', 'us', 'usa', 'nasdaq', 'nyse', 's&p', 'dow', 'fomc', 'fed']):
            return COUNTRY_ICONS['미국']
        elif any(keyword in text_lower for keyword in ['한국', 'kr', 'korea', 'kospi', 'kosdaq', '한은', '한국은행']):
            return COUNTRY_ICONS['한국']
        elif any(keyword in text_lower for keyword in ['중국', 'cn', 'china', 'shanghai', 'shenzhen', '상해', '심천']):
            return COUNTRY_ICONS['중국']
        
        return ''
    
    async def collect_tossinvest_calendar(self):
        """토스투자증권에서 경제지표 일정을 수집합니다."""
        print("\n토스투자증권 경제지표 수집 중...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # 다음 주 월요일 날짜로 URL 생성
                monday = self.next_week_dates['월']
                url = f"https://tossinvest.com/?calendar={monday.strftime('%Y-%m-%d')}&category=indices"
                
                print(f"접속 URL: {url}")
                await page.goto(url, wait_until='domcontentloaded')
                await page.wait_for_timeout(3000)
                
                # 페이지 타이틀 확인
                title = await page.title()
                print(f"페이지 타이틀: {title}")
                
                # 디버깅: 페이지의 실제 구조 확인
                debug_info = await page.evaluate('''() => {
                    const info = {
                        url: window.location.href,
                        title: document.title,
                        bodyText: document.body.innerText.substring(0, 500),
                        elementCounts: {
                            divs: document.querySelectorAll('div').length,
                            tables: document.querySelectorAll('table').length,
                            buttons: document.querySelectorAll('button').length
                        },
                        possibleSelectors: []
                    };
                    
                    // 가능한 선택자들 찾기
                    const selectors = [
                        '[class*="calendar"]',
                        '[class*="event"]',
                        '[class*="economic"]',
                        '[class*="index"]',
                        '[class*="schedule"]',
                        'table',
                        '[data-testid*="calendar"]'
                    ];
                    
                    selectors.forEach(selector => {
                        const elements = document.querySelectorAll(selector);
                        if (elements.length > 0) {
                            info.possibleSelectors.push({
                                selector: selector,
                                count: elements.length,
                                firstText: elements[0].innerText ? elements[0].innerText.substring(0, 100) : ''
                            });
                        }
                    });
                    
                    return info;
                }''')
                
                print("\n=== 디버깅 정보 ===")
                print(f"실제 URL: {debug_info['url']}")
                print(f"요소 개수: divs={debug_info['elementCounts']['divs']}, tables={debug_info['elementCounts']['tables']}")
                print(f"페이지 내용 미리보기: {debug_info['bodyText'][:200]}...")
                print("\n발견된 선택자들:")
                for selector_info in debug_info['possibleSelectors']:
                    print(f"  - {selector_info['selector']}: {selector_info['count']}개 발견")
                    if selector_info['firstText']:
                        print(f"    첫 번째 요소 텍스트: {selector_info['firstText'][:50]}...")
                
                # 경제지표 데이터 추출 시도 (여러 선택자 시도)
                events_data = []
                
                # 방법 1: 기존 선택자
                events_data = await page.evaluate('''() => {
                    const events = [];
                    const eventElements = document.querySelectorAll('[class*="calendar-event"], [class*="economic-event"]');
                    
                    eventElements.forEach(elem => {
                        const dateElem = elem.querySelector('[class*="date"]');
                        const titleElem = elem.querySelector('[class*="title"], [class*="name"]');
                        const countryElem = elem.querySelector('[class*="country"]');
                        
                        if (titleElem) {
                            events.push({
                                date: dateElem ? dateElem.textContent.trim() : '',
                                title: titleElem.textContent.trim(),
                                country: countryElem ? countryElem.textContent.trim() : ''
                            });
                        }
                    });
                    
                    return events;
                }''')
                
                # 방법 2: 테이블 기반 추출 시도
                if len(events_data) == 0:
                    print("\n테이블 기반 추출 시도...")
                    events_data = await page.evaluate('''() => {
                        const events = [];
                        const tables = document.querySelectorAll('table');
                        
                        tables.forEach(table => {
                            const rows = table.querySelectorAll('tr');
                            rows.forEach(row => {
                                const cells = row.querySelectorAll('td, th');
                                if (cells.length >= 2) {
                                    const text = row.innerText;
                                    if (text && text.length > 10) {
                                        events.push({
                                            date: '',
                                            title: text.substring(0, 100),
                                            country: ''
                                        });
                                    }
                                }
                            });
                        });
                        
                        return events.slice(0, 10); // 최대 10개만
                    }''')
                
                # 데이터 정리
                for event in events_data:
                    if event['title']:
                        # 날짜를 요일로 변환
                        weekday = self._date_to_weekday(event['date'])
                        if weekday and weekday in self.events:
                            icon = self._get_country_icon(event['country'] + ' ' + event['title'])
                            self.events[weekday]['일정'].append(f"{icon} {event['title']}")
                
                print(f"\n✓ 토스투자증권에서 {len(events_data)}개 일정 수집 완료")
                
            except Exception as e:
                print(f"❌ 토스투자증권 수집 실패: {str(e)}")
                import traceback
                traceback.print_exc()
            
            finally:
                await browser.close()
    
    async def collect_tossinvest_earnings(self):
        """토스투자증권에서 기업 실적 일정을 수집합니다."""
        print("\n토스투자증권 기업 실적 수집 중...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # 다음 주 월요일 날짜로 URL 생성
                monday = self.next_week_dates['월']
                url = f"https://tossinvest.com/?calendar={monday.strftime('%Y-%m-%d')}&category=estimate"
                
                await page.goto(url, wait_until='domcontentloaded')
                await page.wait_for_timeout(3000)
                
                # 기업 실적 데이터 추출
                earnings_data = await page.evaluate('''() => {
                    const earnings = [];
                    const earningElements = document.querySelectorAll('[class*="earning"], [class*="estimate"]');
                    
                    earningElements.forEach(elem => {
                        const dateElem = elem.querySelector('[class*="date"]');
                        const companyElem = elem.querySelector('[class*="company"], [class*="name"]');
                        const marketElem = elem.querySelector('[class*="market"], [class*="exchange"]');
                        
                        if (companyElem) {
                            earnings.push({
                                date: dateElem ? dateElem.textContent.trim() : '',
                                company: companyElem.textContent.trim(),
                                market: marketElem ? marketElem.textContent.trim() : ''
                            });
                        }
                    });
                    
                    return earnings;
                }''')
                
                # 데이터 정리
                for earning in earnings_data:
                    if earning['company']:
                        weekday = self._date_to_weekday(earning['date'])
                        if weekday and weekday in self.events:
                            icon = self._get_country_icon(earning['market'] + ' ' + earning['company'])
                            self.events[weekday]['실적'].append(f"{icon} {earning['company']}")
                
                print(f"✓ 토스투자증권에서 {len(earnings_data)}개 실적 수집 완료")
                
            except Exception as e:
                print(f"❌ 토스투자증권 실적 수집 실패: {str(e)}")
            
            finally:
                await browser.close()
    
    async def collect_investing_calendar(self):
        """Investing.com에서 경제지표 일정을 수집합니다."""
        print("\nInvesting.com 경제지표 수집 중...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto("https://kr.investing.com/economic-calendar/", wait_until='domcontentloaded')
                await page.wait_for_timeout(5000)
                
                # 중요도 높은 이벤트만 선택 (별 3개)
                await page.evaluate('''() => {
                    const checkboxes = document.querySelectorAll('input[type="checkbox"][name="importance"]');
                    checkboxes.forEach(checkbox => {
                        if (checkbox.value !== '3') {
                            checkbox.click();
                        }
                    });
                }''')
                
                await page.wait_for_timeout(2000)
                
                # 경제지표 데이터 추출
                calendar_data = await page.evaluate('''() => {
                    const events = [];
                    const rows = document.querySelectorAll('tr[id*="eventRow"]');
                    
                    rows.forEach(row => {
                        const timeElem = row.querySelector('td.time');
                        const flagElem = row.querySelector('td.flagCur span');
                        const eventElem = row.querySelector('td.event a');
                        const impactElem = row.querySelector('td.sentiment');
                        
                        if (eventElem && impactElem) {
                            // 중요도 체크 (별 3개만)
                            const stars = impactElem.querySelectorAll('i.grayFullBullishIcon').length;
                            if (stars >= 3) {
                                events.push({
                                    time: timeElem ? timeElem.textContent.trim() : '',
                                    country: flagElem ? flagElem.className : '',
                                    event: eventElem.textContent.trim(),
                                    importance: stars
                                });
                            }
                        }
                    });
                    
                    return events;
                }''')
                
                # 데이터 정리 및 요일 매핑
                for event in calendar_data:
                    if event['event']:
                        # 국가 플래그에서 국가 추출
                        country = self._extract_country_from_flag(event['country'])
                        if country in ['미국', '한국', '중국']:
                            icon = COUNTRY_ICONS[country]
                            # 요일 추정 (실제로는 날짜 정보가 필요함)
                            # 여기서는 예시로 균등 분배
                            weekdays = list(self.events.keys())
                            weekday = weekdays[len(self.events[weekdays[0]]['일정']) % 5]
                            self.events[weekday]['일정'].append(f"{icon} {event['event']}")
                
                print(f"✓ Investing.com에서 {len(calendar_data)}개 중요 일정 수집 완료")
                
            except Exception as e:
                print(f"❌ Investing.com 수집 실패: {str(e)}")
            
            finally:
                await browser.close()
    
    async def collect_investing_earnings(self):
        """Investing.com에서 기업 실적 일정을 수집합니다."""
        print("\nInvesting.com 기업 실적 수집 중...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto("https://kr.investing.com/earnings-calendar/", wait_until='domcontentloaded')
                await page.wait_for_timeout(5000)
                
                # 실적 데이터 추출
                earnings_data = await page.evaluate('''() => {
                    const earnings = [];
                    const rows = document.querySelectorAll('tr[id*="eventRow"]');
                    
                    rows.forEach(row => {
                        const timeElem = row.querySelector('td.time');
                        const flagElem = row.querySelector('td.flagCur span');
                        const companyElem = row.querySelector('td.left a');
                        
                        if (companyElem) {
                            earnings.push({
                                time: timeElem ? timeElem.textContent.trim() : '',
                                country: flagElem ? flagElem.className : '',
                                company: companyElem.textContent.trim()
                            });
                        }
                    });
                    
                    return earnings;
                }''')
                
                # 주요 기업 필터링 및 정리
                major_companies = ['NVDA', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 
                                 '삼성전자', 'SK하이닉스', 'LG에너지솔루션', '현대차', 'NAVER', '카카오']
                
                for earning in earnings_data:
                    if any(company in earning['company'] for company in major_companies):
                        country = self._extract_country_from_flag(earning['country'])
                        if country in ['미국', '한국', '중국']:
                            icon = COUNTRY_ICONS[country]
                            # 요일 추정
                            weekdays = list(self.events.keys())
                            weekday = weekdays[len(self.events[weekdays[0]]['실적']) % 5]
                            self.events[weekday]['실적'].append(f"{icon} {earning['company']}")
                
                print(f"✓ Investing.com에서 주요 기업 실적 수집 완료")
                
            except Exception as e:
                print(f"❌ Investing.com 실적 수집 실패: {str(e)}")
            
            finally:
                await browser.close()
    
    def _date_to_weekday(self, date_str: str) -> str:
        """날짜 문자열을 요일로 변환합니다."""
        # 여기서는 간단한 예시로 구현
        # 실제로는 날짜 파싱 로직이 필요
        weekdays = ['월', '화', '수', '목', '금']
        return weekdays[0]  # 임시로 월요일 반환
    
    def _extract_country_from_flag(self, flag_class: str) -> str:
        """플래그 클래스명에서 국가를 추출합니다."""
        if 'usa' in flag_class.lower() or 'usd' in flag_class.lower():
            return '미국'
        elif 'kor' in flag_class.lower() or 'krw' in flag_class.lower():
            return '한국'
        elif 'chn' in flag_class.lower() or 'cny' in flag_class.lower():
            return '중국'
        return ''
    
    def generate_markdown_table(self) -> str:
        """수집된 데이터를 마크다운 테이블로 생성합니다."""
        # 테이블 헤더
        table = "|      | 월          | 화                | 수   | 목                                                           | 금                                                 |\n"
        table += "| ---- | ----------- | ----------------- | ---- | ------------------------------------------------------------ | -------------------------------------------------- |\n"
        
        # 일정 행
        schedule_row = "| 일정 |"
        has_schedule = False
        for day in ['월', '화', '수', '목', '금']:
            events = self.events[day]['일정']
            if events:
                has_schedule = True
                # 최대 3개까지만 표시
                selected_events = events[:3]
                schedule_row += " " + "<br/>".join(selected_events) + " |"
            else:
                schedule_row += "      |"
        
        # 실적 행
        earnings_row = "| 실적 |"
        has_earnings = False
        for day in ['월', '화', '수', '목', '금']:
            earnings = self.events[day]['실적']
            if earnings:
                has_earnings = True
                # 최대 5개까지만 표시
                selected_earnings = earnings[:5]
                earnings_row += " " + "<br/>".join(selected_earnings) + " |"
            else:
                earnings_row += "             |"
        
        # 데이터가 없는 경우 안내 메시지 추가
        if not has_schedule and not has_earnings:
            table += "| 일정 | (데이터 없음) | (데이터 없음) | (데이터 없음) | (데이터 없음) | (데이터 없음) |\n"
            table += "| 실적 | (데이터 없음) | (데이터 없음) | (데이터 없음) | (데이터 없음) | (데이터 없음) |\n"
            table += "\n*참고: 주요 기업들의 2분기 실적 발표는 대부분 7월 중순(7/15~)부터 시작됩니다.*"
        else:
            table += schedule_row + "\n"
            table += earnings_row + "\n"
        
        return table
    
    async def collect_all(self):
        """모든 소스에서 데이터를 수집합니다."""
        print(f"다음 주({self.next_week_dates['월'].strftime('%Y-%m-%d')} ~ {self.next_week_dates['금'].strftime('%Y-%m-%d')}) 일정 수집을 시작합니다...")
        
        # 병렬로 데이터 수집
        results = await asyncio.gather(
            self.collect_tossinvest_calendar(),
            self.collect_tossinvest_earnings(),
            self.collect_investing_calendar(),
            self.collect_investing_earnings(),
            self.collect_miraeasset_calendar(),
            return_exceptions=True
        )
        
        # 에러 확인
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"수집 중 에러 발생: {result}")
        
        # 데이터가 하나도 없으면 샘플 데이터 사용
        total_events = sum(len(self.events[day]['일정']) + len(self.events[day]['실적']) 
                          for day in self.events)
        
        if total_events == 0:
            print("\n실제 데이터를 수집하지 못했습니다. 샘플 데이터를 사용합니다.")
            await self.collect_sample_data_from_web()
        else:
            print(f"\n총 {total_events}개의 일정/실적을 수집했습니다.")
        
        # 마크다운 테이블 생성
        table = self.generate_markdown_table()
        
        print("\n" + "="*80)
        print("다음 주 주요 증시 일정 및 기업 실적")
        print("="*80)
        print(table)
        
        # 파일로 저장
        with open('next_week_events.md', 'w', encoding='utf-8') as f:
            f.write(f"# 다음 주 주요 증시 일정 및 기업 실적\n")
            f.write(f"기간: {self.next_week_dates['월'].strftime('%Y-%m-%d')} ~ {self.next_week_dates['금'].strftime('%Y-%m-%d')}\n\n")
            f.write(table)
        
        print("\n✓ 결과가 'next_week_events.md' 파일로 저장되었습니다.")
        
        return table
    
    async def collect_miraeasset_calendar(self):
        """미래에셋증권에서 경제지표 일정을 수집합니다."""
        print("\n미래에셋증권 경제지표 수집 중...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                url = "https://securities.miraeasset.com/hkr/hkr1003/n13.do"
                print(f"접속 URL: {url}")
                await page.goto(url, wait_until='networkidle')
                await page.wait_for_timeout(5000)
                
                # 페이지 구조 디버깅
                debug_info = await page.evaluate('''() => {
                    const tables = document.querySelectorAll('table');
                    const divs = document.querySelectorAll('div[class*="schedule"], div[class*="calendar"], div[class*="event"]');
                    
                    return {
                        tableCount: tables.length,
                        divCount: divs.length,
                        pageTitle: document.title,
                        hasData: document.body.innerText.includes('경제지표') || document.body.innerText.includes('일정')
                    };
                }''')
                
                print(f"페이지 정보: tables={debug_info['tableCount']}, 경제지표 관련 내용={debug_info['hasData']}")
                
                # 경제지표 테이블에서 데이터 추출
                events_data = await page.evaluate('''() => {
                    const events = [];
                    const tables = document.querySelectorAll('table');
                    
                    tables.forEach(table => {
                        const rows = table.querySelectorAll('tr');
                        rows.forEach((row, idx) => {
                            if (idx === 0) return; // 헤더 스킵
                            
                            const cells = row.querySelectorAll('td');
                            if (cells.length >= 3) {
                                const dateText = cells[0]?.innerText || '';
                                const eventText = cells[1]?.innerText || cells[2]?.innerText || '';
                                const countryText = cells[2]?.innerText || '';
                                
                                if (eventText && eventText.trim().length > 0) {
                                    events.push({
                                        date: dateText.trim(),
                                        title: eventText.trim(),
                                        country: countryText.trim()
                                    });
                                }
                            }
                        });
                    });
                    
                    return events.slice(0, 20); // 최대 20개
                }''')
                
                # 데이터 정리
                for event in events_data:
                    if event['title'] and len(event['title']) > 3:
                        # 요일 배정 (실제로는 날짜 파싱 필요)
                        weekdays = list(self.events.keys())
                        weekday = weekdays[len(events_data) % 5]
                        
                        icon = self._get_country_icon(event['country'] + ' ' + event['title'])
                        self.events[weekday]['일정'].append(f"{icon} {event['title']}")
                
                print(f"✓ 미래에셋증권에서 {len(events_data)}개 일정 수집 완료")
                
            except Exception as e:
                print(f"❌ 미래에셋증권 수집 실패: {str(e)}")
                import traceback
                traceback.print_exc()
            
            finally:
                await browser.close()
    
    async def collect_sample_data_from_web(self):
        """웹에서 샘플 데이터를 수집합니다 (임시 대안)."""
        print("\n실제 데이터를 수집하지 못했습니다.")
        print("참고: 2분기 실적 시즌은 일반적으로 7월 중순부터 시작됩니다.")
        
        # 일반적인 경제지표만 포함 (실적은 정확한 날짜가 필요하므로 제외)
        common_events = {
            '월': [],
            '화': [],
            '수': [],
            '목': ['🇺🇸 주간 신규실업수당 청구건수'],  # 매주 목요일 정기 발표
            '금': []
        }
        
        # 경제지표만 추가 (실적은 제외)
        for day in ['월', '화', '수', '목', '금']:
            if day in common_events and common_events[day]:
                self.events[day]['일정'].extend(common_events[day])
        
        print("✓ 최소한의 정기 경제지표만 포함되었습니다.")


async def main():
    """메인 실행 함수"""
    collector = WeeklyEventCollector()
    await collector.collect_all()


if __name__ == "__main__":
    asyncio.run(main())
