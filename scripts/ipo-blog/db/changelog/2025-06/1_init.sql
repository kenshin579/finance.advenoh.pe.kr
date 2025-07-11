--liquibase formatted sql
--changeset ipo-blog:#001

-- IPO 정보 테이블
CREATE TABLE IF NOT EXISTS `ipo_info` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `stock_code` VARCHAR(10) UNIQUE NOT NULL COMMENT '종목코드',
    `company_name` VARCHAR(100) NOT NULL COMMENT '회사명',
    `market_type` VARCHAR(20) COMMENT '시장구분 (코스피/코스닥)',
    `company_type` VARCHAR(50) COMMENT '기업구분',
    `industry` VARCHAR(100) COMMENT '업종',
    `main_products` TEXT COMMENT '주요제품',
    `homepage` VARCHAR(255) COMMENT '홈페이지',
    `major_shareholder` VARCHAR(100) COMMENT '최대주주',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일시'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='IPO 기본정보';

-- 재무 정보 테이블
CREATE TABLE IF NOT EXISTS `financial_info` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `stock_code` VARCHAR(10) NOT NULL COMMENT '종목코드',
    `year` INT NOT NULL COMMENT '연도',
    `revenue` DECIMAL(15,2) COMMENT '매출액',
    `operating_profit` DECIMAL(15,2) COMMENT '영업이익',
    `net_profit` DECIMAL(15,2) COMMENT '당기순이익',
    `total_debt` DECIMAL(15,2) COMMENT '총부채',
    `capital` DECIMAL(15,2) COMMENT '자본금',
    FOREIGN KEY (`stock_code`) REFERENCES `ipo_info`(`stock_code`) ON DELETE CASCADE,
    UNIQUE KEY `unique_stock_year` (`stock_code`, `year`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='재무정보';

-- 공모 정보 테이블
CREATE TABLE IF NOT EXISTS `offering_info` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `stock_code` VARCHAR(10) NOT NULL COMMENT '종목코드',
    `desired_price_min` INT COMMENT '희망공모가 최소',
    `desired_price_max` INT COMMENT '희망공모가 최대',
    `fixed_price` INT COMMENT '확정공모가',
    `underwriters` TEXT COMMENT '주관사',
    `total_competition_rate` DECIMAL(10,2) COMMENT '전체경쟁률',
    `institutional_competition_rate` DECIMAL(10,2) COMMENT '기관경쟁률',
    `retail_allocation` INT COMMENT '일반청약비율',
    `institutional_allocation` INT COMMENT '기관청약비율',
    `demand_forecast_date` DATE COMMENT '수요예측일',
    `subscription_date` DATE COMMENT '청약일',
    `payment_date` DATE COMMENT '납입일',
    `refund_date` DATE COMMENT '환불일',
    `listing_date` DATE COMMENT '상장일',
    FOREIGN KEY (`stock_code`) REFERENCES `ipo_info`(`stock_code`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='공모정보';

-- 뉴스 정보 테이블
CREATE TABLE IF NOT EXISTS `news_info` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `stock_code` VARCHAR(10) NOT NULL COMMENT '종목코드',
    `title` VARCHAR(500) COMMENT '뉴스제목',
    `url` VARCHAR(500) COMMENT '뉴스URL',
    `source` VARCHAR(50) COMMENT '뉴스출처',
    `published_date` DATETIME COMMENT '발행일시',
    `summary` TEXT COMMENT '요약',
    `sentiment` VARCHAR(20) COMMENT '감성분석 (긍정/부정/중립)',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
    FOREIGN KEY (`stock_code`) REFERENCES `ipo_info`(`stock_code`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='뉴스정보';

-- 포스팅 이력 테이블
CREATE TABLE IF NOT EXISTS `posting_history` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `stock_code` VARCHAR(10) NOT NULL COMMENT '종목코드',
    `file_path` VARCHAR(500) COMMENT '파일경로',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
    `status` VARCHAR(20) DEFAULT 'completed' COMMENT '상태',
    FOREIGN KEY (`stock_code`) REFERENCES `ipo_info`(`stock_code`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='포스팅이력';

--rollback DROP TABLE IF EXISTS `posting_history`;
--rollback DROP TABLE IF EXISTS `news_info`;
--rollback DROP TABLE IF EXISTS `offering_info`;
--rollback DROP TABLE IF EXISTS `financial_info`;
--rollback DROP TABLE IF EXISTS `ipo_info`; 