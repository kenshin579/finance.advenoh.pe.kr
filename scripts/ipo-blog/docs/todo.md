# IPO 블로그 자동화 시스템 TODO List

## 1. 프로젝트 초기 설정
- [x] Python 가상환경 생성 및 활성화
- [x] requirements.txt 파일 작성
  - [x] BeautifulSoup4
  - [x] requests
  - [x] mysql-connector-python
  - [x] openai
  - [x] plotly
  - [x] python-dotenv
  - [x] pandas
  - [x] lxml
- [x] .env 파일 생성 및 환경변수 설정 (OS 환경변수 사용)
  - [x] IPO_MYSQL_* 환경변수
  - [x] OPENAI_API_KEY
- [x] .gitignore 파일 생성

## 2. 데이터베이스 설정
- [ ] MySQL JDBC 드라이버 설치
- [ ] Liquibase 실행하여 DB 스키마 생성
  ```bash
  cd db
  liquibase update
  ```
- [ ] DB 연결 테스트

## 3. 기본 모듈 구조 생성
- [x] 디렉토리 구조 생성
  ```
  ├── config/
  ├── scrapers/
  ├── database/
  ├── processors/
  ├── generators/
  ├── utils/
  ├── output/
  └── logs/
  ```
- [x] 각 모듈의 __init__.py 파일 생성

## 4. 설정 관리 모듈 (config/)
- [ ] config.py 작성
  - [ ] 환경변수 로드
  - [ ] 데이터베이스 설정
  - [ ] API 키 관리
  - [ ] 증권사 리스트 정의 (미래에셋, 한국투자, 신한투자, KB, NH, 삼성)

## 5. 유틸리티 모듈 (utils/)
- [ ] logger.py 작성
  - [ ] 로깅 레벨 설정
  - [ ] 파일 및 콘솔 출력 설정

## 6. 데이터베이스 모듈 (database/)
- [ ] connection.py 작성
  - [ ] MySQL 연결 풀 구현
  - [ ] 연결 관리 함수
- [ ] models.py 작성
  - [ ] IPOInfo 클래스
  - [ ] FinancialInfo 클래스
  - [ ] OfferingInfo 클래스
  - [ ] NewsInfo 클래스
  - [ ] PostingHistory 클래스
  - [ ] CRUD 메서드 구현

## 7. 웹 스크래핑 모듈 (scrapers/)
- [x] base_scraper.py 작성
  - [x] BaseScraper 클래스 구현
  - [x] User-Agent 설정
  - [x] robots.txt 준수 로직
  - [x] 요청 간격 제어 (최소 1초)
  - [x] 재시도 로직 (3회)

- [x] naver_scraper.py 작성
  - [x] IPO 목록 수집 기능
  - [x] 증권사 필터링 로직
  - [x] 기본 IPO 정보 추출
    - [x] 종목명, 종목코드
    - [x] 시장구분, 기업구분
    - [x] 공모금액, 기관경쟁률

- [ ] comm38_scraper.py 작성
  - [ ] 기업 검색 기능
  - [ ] 상세 정보 수집
    - [ ] 재무 정보
    - [ ] 공모 상세 정보
    - [ ] 청약 일정

- [ ] news_scraper.py 작성
  - [ ] 구글 뉴스 검색
  - [ ] 네이버 뉴스 검색
  - [ ] 최대 4개 뉴스 수집
  - [ ] 뉴스 메타데이터 추출

## 8. 데이터 처리 모듈 (processors/)
- [ ] data_validator.py 작성
  - [ ] 필수 데이터 검증 (공모금액, 기관경쟁률)
  - [ ] 데이터 형식 검증
  - [ ] 중복 체크 (종목코드 기준)

- [ ] data_processor.py 작성
  - [ ] 수집된 데이터 정제
  - [ ] 누락 데이터 처리 ("Unknown")
  - [ ] 데이터 구조화

## 9. 콘텐츠 생성 모듈 (generators/)
- [ ] content_generator.py 작성
  - [ ] ChatGPT API 클라이언트 설정
  - [ ] 프롬프트 템플릿 작성
  - [ ] 블로그 콘텐츠 생성 함수
  - [ ] 뉴스 요약 및 감성 분석

- [ ] markdown_generator.py 작성
  - [ ] Markdown 템플릿 작성
  - [ ] 테이블 포맷팅
  - [ ] 파일 저장 로직
  - [ ] 디렉토리 생성 (output/종목코드-종목명/)

- [ ] chart_generator.py 작성
  - [ ] Plotly 차트 생성
    - [ ] 재무 데이터 차트 (매출액, 영업이익, 당기순이익)
    - [ ] 부채 관련 차트
  - [ ] 차트 이미지 저장
  - [ ] 데이터 부족시 테이블 생성

## 10. 메인 실행 파일
- [ ] main.py 작성
  - [ ] 전체 파이프라인 조율
  - [ ] 에러 핸들링
  - [ ] 실행 플로우:
    1. 설정 로드
    2. DB 연결
    3. IPO 목록 수집
    4. 증권사 필터링
    5. 각 IPO별 상세 정보 수집
    6. 중복 체크
    7. 뉴스 수집
    8. 데이터 검증 및 저장
    9. 블로그 콘텐츠 생성
    10. 파일 및 차트 생성
    11. 포스팅 이력 저장

## 11. 테스트
- [ ] 단위 테스트 작성
  - [ ] 스크래퍼 테스트
  - [ ] DB 연결 테스트
  - [ ] 데이터 검증 테스트
- [ ] 통합 테스트
  - [ ] 전체 파이프라인 테스트
  - [ ] 에러 시나리오 테스트

## 12. 문서화 및 배포
- [ ] README.md 작성
  - [ ] 설치 가이드
  - [ ] 실행 방법
  - [ ] 환경변수 설명
- [ ] 예제 실행 및 결과 확인
- [ ] 최종 테스트

## 우선순위
1. **높음**: 프로젝트 초기 설정, DB 설정, 기본 모듈 구조
2. **중간**: 스크래핑 모듈, 데이터 처리 모듈
3. **낮음**: 차트 생성, 문서화

## 예상 소요 시간
- 전체 개발: 약 3-5일
- 테스트 및 디버깅: 약 1-2일 