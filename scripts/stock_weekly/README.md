# CNN Fear & Greed Index 이미지 캡처 도구

CNN Markets의 Fear & Greed Index 게이지 차트를 자동으로 캡처하여 이미지로 저장하는 Python 스크립트입니다.

## 특징

- 웹 브라우저 자동화를 통한 자동 캡처
- 다양한 캡처 방식 제공 (요소 단위, 영역 단위, 전체 페이지)
- 오류 처리 및 대체 캡처 방법 내장

## 제공되는 스크립트

1. **main.py**: 기본 Selenium 버전
2. **capture_improved.py**: webdriver-manager를 사용한 개선된 버전
3. **capture_playwright.py**: Playwright를 사용한 현대적인 버전

## 설치 방법

### 1. 필수 패키지 설치

```bash
# 프로젝트 의존성 설치
pip install -e .

# 또는 개별 패키지 설치
pip install selenium pillow webdriver-manager
```

### 2. 선택적 패키지 설치

#### Playwright 설치 (capture_playwright.py 사용 시)
```bash
pip install -e ".[playwright]"
# 브라우저 설치
playwright install chromium
```

#### 개발 도구 설치
```bash
pip install -e ".[dev]"
```

### 3. ChromeDriver 설정

#### 옵션 A: 수동 설치 (main.py 사용 시)
- [ChromeDriver 다운로드](https://chromedriver.chromium.org/)
- 시스템 PATH에 추가하거나 스크립트와 같은 디렉토리에 배치

#### 옵션 B: 자동 설치 (capture_improved.py 사용 시)
- webdriver-manager가 자동으로 처리합니다

## 사용 방법

### 기본 버전 실행
```bash
python main.py
# 또는 (pip install -e . 실행 후)
capture-basic
```

### 개선된 버전 실행 (권장)
```bash
python capture_improved.py
# 또는 (pip install -e . 실행 후)
capture-improved
```

### Playwright 버전 실행
```bash
python capture_playwright.py
# 또는 (pip install -e . 실행 후)
capture-playwright
```

## 출력 파일

스크립트는 다음과 같은 이미지 파일들을 생성합니다:

- `fear_greed_gauge.png`: Fear & Greed 게이지만 캡처
- `fear_greed_with_context.png`: 게이지와 주변 영역 포함
- `fear_greed_center_area.png`: 페이지 중앙 영역 캡처
- `full_page.png`: 전체 페이지 스크린샷 (Playwright 버전)

모든 이미지는 `captured_images/` 또는 `captured_images_playwright/` 디렉토리에 저장됩니다.

## 문제 해결

### Chrome 브라우저가 없는 경우
- Google Chrome을 설치하세요: https://www.google.com/chrome/

### "chromedriver not found" 오류
- `capture_improved.py`를 사용하거나
- ChromeDriver를 수동으로 다운로드하여 PATH에 추가

### 페이지 로딩이 느린 경우
- 스크립트 내 `time.sleep()` 값을 증가시키세요

### 게이지를 찾을 수 없는 경우
- CNN 웹사이트의 구조가 변경되었을 수 있습니다
- 전체 페이지 스크린샷이 대체 방법으로 저장됩니다

### 패키지 설치 오류
- Python 3.8 이상이 설치되어 있는지 확인하세요
- pip를 최신 버전으로 업데이트: `pip install --upgrade pip`

## 프로젝트 구조

```
.
├── README.md              # 이 파일
├── pyproject.toml         # 프로젝트 설정 및 의존성
├── main.py               # 기본 Selenium 스크립트
├── capture_improved.py    # 개선된 Selenium 스크립트
├── capture_playwright.py  # Playwright 버전 스크립트
└── captured_images/       # 캡처된 이미지 저장 디렉토리
```

## 주의사항

- 이 도구는 교육 및 개인 사용 목적입니다
- 웹사이트의 이용 약관을 준수하세요
- 과도한 요청은 피하세요

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 