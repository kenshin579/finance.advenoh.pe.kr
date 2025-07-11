# IPO Blog 데이터베이스 관리

Liquibase를 사용하여 데이터베이스 스키마를 버전 관리합니다.

## 필요 사항

1. **Liquibase 설치**
   ```bash
   brew install liquibase  # macOS
   # 또는 https://www.liquibase.org/download 에서 다운로드
   ```

2. **MySQL Connector 설치**
   ```bash
   # lib 디렉토리에 MySQL Connector JAR 파일 다운로드
   cd db/lib
   wget https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-j-8.4.0.jar
   ```

3. **환경변수 설정**
   ```bash
   export IPO_MYSQL_HOST=stock-api.advenoh.pe.kr
   export IPO_MYSQL_PORT=10024
   export IPO_MYSQL_DATABASE=ipo
   export IPO_MYSQL_USER=ipo
   export IPO_MYSQL_PASSWORD=your_password
   ```

## 디렉토리 구조

```
db/
├── changelog.yaml                # 마스터 changelog 파일
├── liquibase.properties         # Liquibase 설정
├── liquibase.sh                 # 실행 스크립트
├── changelog/                   # SQL 변경사항
│   └── 2025-06/                # 날짜별 디렉토리
│       ├── 1_init.sql          # 초기 테이블 생성
│       ├── 2_add-indexes.sql   # 인덱스 추가
│       └── 3_insert-initial-data.sql  # 초기 데이터
├── lib/                        # 의존성 라이브러리
│   └── mysql-connector-j-8.4.0.jar
├── scripts/                    # 유틸리티 스크립트
│   └── mysql_backup.sh         # 백업 스크립트
└── README.md                   # 이 파일

```

## 사용 방법

### 1. DB 상태 확인
```bash
cd db
./liquibase.sh status
```

### 2. 변경사항 적용
```bash
# 모든 변경사항 적용
./liquibase.sh update-all

# 한 개씩 적용
./liquibase.sh update-one
```

### 3. 롤백
```bash
# 마지막 변경사항 1개 롤백
./liquibase.sh rollback-one

# 특정 태그로 롤백
./liquibase.sh rollback-tag <tag-name>
```

### 4. 히스토리 확인
```bash
./liquibase.sh history
```

### 5. 태그 생성
```bash
./liquibase.sh tag release-1.0
```

### 6. 백업
```bash
cd scripts
./mysql_backup.sh
```

## 새로운 변경사항 추가

1. `changelog/YYYY-MM/` 디렉토리에 새 SQL 파일 생성
2. 파일명은 순서를 나타내는 번호로 시작 (예: `4_add-column.sql`)
3. 파일 형식:
   ```sql
   --liquibase formatted sql
   --changeset ipo-blog:#004
   
   -- 변경사항 SQL
   ALTER TABLE ipo_info ADD COLUMN new_column VARCHAR(50);
   
   --rollback ALTER TABLE ipo_info DROP COLUMN new_column;
   ```

## 테이블 구조

### 1. ipo_info (IPO 기본정보)
- stock_code: 종목코드 (PK)
- company_name: 회사명
- market_type: 시장구분
- industry: 업종
- 기타 기본 정보

### 2. financial_info (재무정보)
- 연도별 재무 데이터
- stock_code로 ipo_info와 연결

### 3. offering_info (공모정보)
- 공모가, 청약일정 등
- stock_code로 ipo_info와 연결

### 4. news_info (뉴스정보)
- IPO 관련 뉴스
- sentiment 분석 포함

### 5. posting_history (포스팅이력)
- 블로그 포스팅 생성 이력

### 6. underwriter_list (증권사목록)
- 관심 증권사 목록 관리

## 주의사항

1. **프로덕션 적용 전 반드시 테스트 환경에서 검증**
2. **변경 전 백업 필수**
3. **rollback 스크립트 항상 포함**
4. **외래키 제약조건은 CASCADE 옵션 사용** 