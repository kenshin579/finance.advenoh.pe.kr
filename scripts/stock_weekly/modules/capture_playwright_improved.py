import asyncio
from playwright.async_api import async_playwright
from PIL import Image
import io
import os

async def capture_fear_greed_gauge():
    """개선된 Playwright를 사용한 CNN Fear & Greed Index 게이지 캡처"""
    
    # 결과 저장 디렉토리 생성
    output_dir = "captured_fear_greed"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    async with async_playwright() as p:
        # Chromium 브라우저 실행
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        # 새 페이지 생성
        page = await browser.new_page(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        
        try:
            # CNN Fear & Greed Index 페이지로 이동
            url = "https://edition.cnn.com/markets/fear-and-greed"
            print(f"페이지 로딩 중: {url}")
            await page.goto(url, wait_until='domcontentloaded', timeout=60000)
            
            # 페이지 완전 로딩 대기
            print("페이지 로딩 대기 중...")
            await page.wait_for_timeout(7000)
            
            # 팝업 닫기
            try:
                await page.click('button:has-text("Close")', timeout=2000)
            except:
                pass
            
            # 1. SVG 게이지를 직접 찾기
            print("\nFear & Greed 게이지를 찾는 중...")
            
            # 더 구체적인 선택자들
            gauge_selectors = [
                # SVG 기반 선택자
                'svg[aria-labelledby*="gauge"]',
                'svg[class*="gauge"]',
                'svg[id*="gauge"]',
                'svg[viewBox*="0 0"]',
                
                # 컨테이너 기반 선택자
                'div[class*="market-fng-gauge"]',
                'div[class*="fear-greed-gauge"]',
                'div[class*="gauge-container"]',
                '[data-component*="gauge"]',
                
                # aria-label 기반
                '[aria-label*="Fear & Greed"]',
                '[aria-label*="Fear and Greed"]',
                
                # 특정 클래스
                '.market-fng-gauge',
                '.fear-greed-index-gauge',
                '.gauge-widget',
            ]
            
            found_gauge = None
            
            for selector in gauge_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        box = await element.bounding_box()
                        if box and box['width'] > 200 and box['height'] > 150:
                            found_gauge = element
                            print(f"✓ 게이지를 찾았습니다: {selector}")
                            break
                    if found_gauge:
                        break
                except:
                    continue
            
            # 2. JavaScript로 게이지 찾기
            if not found_gauge:
                print("JavaScript로 게이지를 찾는 중...")
                
                gauge_info = await page.evaluate('''() => {
                    // SVG 게이지 찾기
                    const svgs = document.querySelectorAll('svg');
                    for (const svg of svgs) {
                        const rect = svg.getBoundingClientRect();
                        if (rect.width > 200 && rect.height > 150) {
                            // 게이지 관련 요소인지 확인
                            const parent = svg.closest('[class*="gauge"], [class*="fear-greed"]');
                            if (parent || svg.innerHTML.includes('path') || svg.innerHTML.includes('arc')) {
                                svg.setAttribute('data-target-gauge', 'true');
                                return {
                                    found: true,
                                    width: rect.width,
                                    height: rect.height,
                                    x: rect.x,
                                    y: rect.y
                                };
                            }
                        }
                    }
                    
                    // Canvas 게이지 찾기
                    const canvases = document.querySelectorAll('canvas');
                    for (const canvas of canvases) {
                        const rect = canvas.getBoundingClientRect();
                        if (rect.width > 200 && rect.height > 150) {
                            canvas.setAttribute('data-target-gauge', 'true');
                            return {
                                found: true,
                                width: rect.width,
                                height: rect.height,
                                x: rect.x,
                                y: rect.y
                            };
                        }
                    }
                    
                    return { found: false };
                }''')
                
                if gauge_info['found']:
                    found_gauge = await page.query_selector('[data-target-gauge="true"]')
                    print(f"✓ JavaScript로 게이지를 찾았습니다: {gauge_info['width']}x{gauge_info['height']}")
            
            # 3. 텍스트 기반으로 컨테이너 찾기
            if not found_gauge:
                print("텍스트 기반으로 게이지 영역을 찾는 중...")
                
                # "78" 또는 현재 값을 포함하는 영역 찾기
                container = await page.evaluate(r'''() => {
                    const elements = document.querySelectorAll('*');
                    for (const elem of elements) {
                        const text = elem.textContent || '';
                        // 큰 숫자를 포함하고 Fear & Greed 관련 텍스트가 있는 요소
                        if (text.match(/\b\d{2}\b/) && 
                            (text.includes('Fear & Greed') || text.includes('What emotion'))) {
                            const rect = elem.getBoundingClientRect();
                            if (rect.width > 300 && rect.height > 200 && rect.width < 1000) {
                                elem.setAttribute('data-gauge-container', 'true');
                                return true;
                            }
                        }
                    }
                    return false;
                }''')
                
                if container:
                    found_gauge = await page.query_selector('[data-gauge-container="true"]')
                    print("✓ 텍스트 기반으로 게이지 컨테이너를 찾았습니다")
            
            # 캡처 실행
            if found_gauge:
                # 요소로 스크롤
                await found_gauge.scroll_into_view_if_needed()
                await page.wait_for_timeout(1000)
                
                # 1. 요소만 캡처
                await found_gauge.screenshot(
                    path=os.path.join(output_dir, 'gauge_element.png')
                )
                print(f"\n✓ 게이지 요소를 '{output_dir}/gauge_element.png'로 저장했습니다.")
                
                # 2. 패딩 포함 캡처 (작은 패딩)
                box = await found_gauge.bounding_box()
                if box:
                    padding = 30
                    clip = {
                        'x': max(0, box['x'] - padding),
                        'y': max(0, box['y'] - padding),
                        'width': box['width'] + (padding * 2),
                        'height': box['height'] + (padding * 2)
                    }
                    
                    await page.screenshot(
                        path=os.path.join(output_dir, 'gauge_with_padding.png'),
                        clip=clip
                    )
                    print(f"✓ 패딩 포함 게이지를 '{output_dir}/gauge_with_padding.png'로 저장했습니다.")
                    
                    # 3. 위아래로 확장된 영역 캡처 (제목과 과거 데이터 포함)
                    extended_top = 250  # 위로 250px 추가
                    extended_bottom = 55  # 아래로 55px 추가 (75에서 55로)
                    extended_clip = {
                        'x': max(0, box['x'] - 50),
                        'y': max(0, box['y'] - extended_top),
                        'width': box['width'] + 475,  # 오른쪽 475px 추가 (500에서 475로)
                        'height': box['height'] + extended_top + extended_bottom
                    }
                    
                    # 디버깅 정보 출력
                    print(f"\n[디버깅] 게이지 원본 영역:")
                    print(f"  - 위치: ({box['x']}, {box['y']})")
                    print(f"  - 크기: {box['width']} x {box['height']}")
                    print(f"\n[디버깅] 확장된 영역:")
                    print(f"  - 위치: ({extended_clip['x']}, {extended_clip['y']})")
                    print(f"  - 크기: {extended_clip['width']} x {extended_clip['height']}")
                    print(f"  - 원본 높이: {box['height']}")
                    print(f"  - 최종 높이: {extended_clip['height']} (원본 + {extended_top} + {extended_bottom})")
                    
                    # 방법 1: clip을 사용한 캡처 시도
                    await page.screenshot(
                        path=os.path.join(output_dir, 'gauge_extended_clip.png'),
                        clip=extended_clip
                    )
                    print(f"✓ 확장된 게이지 영역 (clip)을 '{output_dir}/gauge_extended_clip.png'로 저장했습니다.")
                    
                    # 방법 2: 전체 페이지 캡처 후 잘라내기
                    # 전체 페이지 스크린샷 생성
                    full_page_screenshot = await page.screenshot(full_page=True)
                    
                    full_image = Image.open(io.BytesIO(full_page_screenshot))
                    print(f"\n[디버깅] 전체 페이지 크기: {full_image.size}")
                    
                    # 원하는 영역 잘라내기
                    crop_left = int(extended_clip['x'])
                    crop_top = int(extended_clip['y'])
                    crop_right = int(extended_clip['x'] + extended_clip['width'])
                    crop_bottom = int(extended_clip['y'] + extended_clip['height'])
                    
                    # 이미지 크기 확인
                    crop_bottom = min(crop_bottom, full_image.height)
                    crop_right = min(crop_right, full_image.width)
                    
                    print(f"[디버깅] 크롭 영역: ({crop_left}, {crop_top}) - ({crop_right}, {crop_bottom})")
                    
                    cropped_image = full_image.crop((crop_left, crop_top, crop_right, crop_bottom))
                    cropped_image.save(os.path.join(output_dir, 'gauge_extended.png'))
                    print(f"✓ 확장된 게이지 영역 (전체 페이지에서 크롭)을 '{output_dir}/gauge_extended.png'로 저장했습니다.")
                    print(f"  - 크롭된 이미지 크기: {cropped_image.size}")
                    
                    # 4. Fear & Greed 전체 컨테이너 캡처
                    # 게이지의 부모 컨테이너를 찾아서 전체 섹션 캡처
                    full_container = await page.evaluate('''(gaugeElement) => {
                        // 게이지의 상위 컨테이너 찾기
                        let parent = gaugeElement;
                        while (parent) {
                            const rect = parent.getBoundingClientRect();
                            // Fear & Greed Index 제목을 포함하는 컨테이너 찾기
                            if (parent.textContent.includes('Fear & Greed Index') && 
                                parent.textContent.includes('What emotion') &&
                                rect.width > 400 && rect.height > 500) {
                                parent.setAttribute('data-full-container', 'true');
                                return {
                                    found: true,
                                    x: rect.x,
                                    y: rect.y,
                                    width: rect.width,
                                    height: rect.height
                                };
                            }
                            parent = parent.parentElement;
                        }
                        return { found: false };
                    }''', found_gauge)
                    
                    if full_container['found']:
                        container_element = await page.query_selector('[data-full-container="true"]')
                        if container_element:
                            await container_element.screenshot(
                                path=os.path.join(output_dir, 'gauge_full_container.png')
                            )
                            print(f"✓ 전체 컨테이너를 '{output_dir}/gauge_full_container.png'로 저장했습니다.")
            
            # 4. 전체 게이지 섹션 캡처 (대안)
            print("\n전체 Fear & Greed 섹션을 캡처 중...")
            
            # 페이지 상단으로 스크롤
            await page.evaluate('window.scrollTo(0, 0)')
            await page.wait_for_timeout(1000)
            
            # Fear & Greed Index 제목 아래 영역 캡처
            await page.screenshot(
                path=os.path.join(output_dir, 'fear_greed_section.png'),
                clip={
                    'x': 0,
                    'y': 200,  # 헤더 아래부터
                    'width': 1920,
                    'height': 600
                }
            )
            print(f"✓ Fear & Greed 섹션을 '{output_dir}/fear_greed_section.png'로 저장했습니다.")
            
            # 5. 중앙 집중 캡처
            viewport_width = 1920
            viewport_height = 1080
            
            await page.screenshot(
                path=os.path.join(output_dir, 'center_focused.png'),
                clip={
                    'x': viewport_width // 2 - 400,
                    'y': 250,
                    'width': 800,
                    'height': 500
                }
            )
            print(f"✓ 중앙 집중 영역을 '{output_dir}/center_focused.png'로 저장했습니다.")
            
            # 6. 개발자 도구로 요소 정보 출력
            element_info = await page.evaluate('''() => {
                const result = [];
                
                // 모든 SVG 요소 정보
                document.querySelectorAll('svg').forEach((svg, i) => {
                    const rect = svg.getBoundingClientRect();
                    if (rect.width > 100 && rect.height > 100) {
                        result.push({
                            type: 'svg',
                            index: i,
                            class: svg.className.baseVal || svg.className,
                            id: svg.id,
                            width: rect.width,
                            height: rect.height,
                            x: rect.x,
                            y: rect.y
                        });
                    }
                });
                
                // 게이지 관련 div 정보
                document.querySelectorAll('[class*="gauge"], [class*="fear"], [class*="greed"]').forEach((elem, i) => {
                    const rect = elem.getBoundingClientRect();
                    if (rect.width > 200 && rect.height > 150 && rect.width < 1000) {
                        result.push({
                            type: elem.tagName.toLowerCase(),
                            index: i,
                            class: elem.className,
                            id: elem.id,
                            width: rect.width,
                            height: rect.height,
                            x: rect.x,
                            y: rect.y
                        });
                    }
                });
                
                return result;
            }''')
            
            print("\n찾은 요소들:")
            for info in element_info:
                print(f"- {info['type']} (#{info['index']}): "
                      f"class='{info['class']}', "
                      f"크기={info['width']}x{info['height']}, "
                      f"위치=({info['x']}, {info['y']})")
            
            print(f"\n✓ 모든 캡처가 '{output_dir}' 디렉토리에 저장되었습니다.")
            
        except Exception as e:
            print(f"\n❌ 오류 발생: {str(e)}")
            
            # 오류 시 스크린샷
            await page.screenshot(
                path=os.path.join(output_dir, 'error_screenshot.png')
            )
            print(f"오류 스크린샷을 '{output_dir}/error_screenshot.png'로 저장했습니다.")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    print("개선된 CNN Fear & Greed Index 게이지 캡처")
    print("=" * 50)
    
    # 실행
    asyncio.run(capture_fear_greed_gauge()) 