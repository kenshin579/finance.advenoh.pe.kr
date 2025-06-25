# IPO Blog Database Management

Liquibase를 사용하여 데이터베이스 스키마를 관리합니다.

## 사전 요구사항

1. MySQL 8.0+ 설치
2. Liquibase 4.19+ 설치
3. MySQL JDBC Driver

## 환경변수 설정

```bash
export IPO_MYSQL_HOST=stock-api.advenoh.pe.kr
export IPO_MYSQL_PORT=10024
export IPO_MYSQL_DATABASE=ipo
export IPO_MYSQL_USER=ipo
export IPO_MYSQL_PASSWORD=your_password
```

## Liquibase 명령어

### 1. 데이터베이스 업데이트
```bash
cd db
liquibase update
```

### 2. 변경사항 미리보기
```bash
liquibase updateSQL
```

### 3. 현재 상태 확인
```bash
liquibase status
```

### 4. 변경 이력 확인
```bash
liquibase history
```

### 5. 롤백 (태그까지)
```bash
liquibase rollback <tag>
```

### 6. 롤백 (변경 횟수)
```bash
liquibase rollbackCount 1
```

## 디렉토리 구조

```
db/
├── changelog/
│   ├── db.changelog-master.xml      # 마스터 changelog
│   ├── changes/
│   │   ├── 001-create-tables.xml    # 테이블 생성
│   │   ├── 002-add-indexes.xml      # 인덱스 추가
│   │   └── 003-insert-initial-data.xml # 초기 데이터 (필요시)
│   └── rollback/                    # 수동 롤백 스크립트 (필요시)
├── liquibase.properties             # Liquibase 설정
└── README.md                        # 이 파일
```

## 새로운 변경사항 추가하기

1. `changelog/changes/` 디렉토리에 새 XML 파일 생성
   ```
   004-add-new-column.xml
   ```

2. 변경사항 작성
   ```xml
   <changeSet id="004-1" author="your-name">
       <comment>Add new column description</comment>
       <!-- 변경 내용 -->
       <rollback>
           <!-- 롤백 내용 -->
       </rollback>
   </changeSet>
   ```

3. `db.changelog-master.xml`에 include 추가
   ```xml
   <include file="changes/004-add-new-column.xml" relativeToChangelogFile="true"/>
   ```

4. 변경사항 적용
   ```bash
   liquibase update
   ```

## 주의사항

- 프로덕션 환경에 적용하기 전에 반드시 테스트 환경에서 검증
- 각 changeSet은 고유한 ID를 가져야 함
- 한번 적용된 changeSet은 수정하지 않고 새로운 changeSet 추가
- 롤백 스크립트는 항상 포함할 것을 권장 