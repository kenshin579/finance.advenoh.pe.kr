#!/usr/bin/env python3
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'  # macOS
plt.rcParams['axes.unicode_minus'] = False

# 수식들 (한글과 LaTeX 혼합)
formulas = [
    {
        'name': 'dividend_yield_formula',
        # 한글이 포함된 분수는 텍스트로 표현
        'text': '배당수익률 = 연간 배당금 / 현재 주가 × 100',
        'figsize': (3.5, 0.5),
        'fontsize': 11,
        'dpi': 200
    },
    {
        'name': 'dividend_yield_calculation',
        # 숫자만 있는 분수는 LaTeX로 표현
        'text': r'$= \frac{3,540}{55,200} \times 100 \approx 6.41\%$',
        'figsize': (2.8, 0.8),
        'fontsize': 11,
        'dpi': 200
    },
    {
        'name': 'stock_price_calculation',
        # 한글과 LaTeX 혼합
        'parts': [
            {'text': '주가 = ', 'type': 'text'},
            {'text': r'$\frac{3,540}{0.07}$', 'type': 'math'},
            {'text': ' ≈ 50,571원', 'type': 'text'}
        ],
        'figsize': (2.8, 0.8),
        'fontsize': 11,
        'dpi': 200
    }
]

# 이미지 생성
for formula in formulas:
    fig, ax = plt.subplots(figsize=formula['figsize'])
    
    if 'parts' in formula:
        # 여러 부분으로 구성된 경우
        x_pos = 0.5
        full_text = ''
        for part in formula['parts']:
            full_text += part['text']
        ax.text(x_pos, 0.5, full_text, 
                transform=ax.transAxes,
                fontsize=formula['fontsize'], 
                verticalalignment='center', 
                horizontalalignment='center',
                fontfamily='AppleGothic')
    else:
        # 단일 텍스트인 경우
        ax.text(0.5, 0.5, formula['text'], 
                transform=ax.transAxes,
                fontsize=formula['fontsize'], 
                verticalalignment='center', 
                horizontalalignment='center',
                fontfamily='AppleGothic')
    
    ax.axis('off')
    
    # 여백 최소화
    plt.tight_layout(pad=0)
    
    # 이미지 저장
    output_path = f'contents/posts/finance/SK텔레콤-주가-배당수익률로-방어선은-어디일까/{formula["name"]}.png'
    plt.savefig(output_path, 
                dpi=formula['dpi'], 
                bbox_inches='tight', 
                facecolor='white',
                pad_inches=0.01)
    plt.close()
    print(f"Generated: {output_path}")

print("\n모든 수식 이미지가 성공적으로 생성되었습니다!")