--liquibase formatted sql
--changeset ipo-blog:#003

-- 증권사 목록 테이블 생성 (추가)
CREATE TABLE IF NOT EXISTS `underwriter_list` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `underwriter_name` VARCHAR(100) NOT NULL COMMENT '증권사명',
    `is_active` BOOLEAN DEFAULT TRUE COMMENT '활성화 여부',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='주관증권사 목록';

-- 증권사 목록 초기 데이터
INSERT INTO `underwriter_list` (`underwriter_name`) VALUES
('미래에셋증권'),
('한국투자증권'),
('신한투자증권'),
('KB증권'),
('NH투자증권'),
('삼성증권');

--rollback DELETE FROM `underwriter_list` WHERE `underwriter_name` IN ('미래에셋증권', '한국투자증권', '신한투자증권', 'KB증권', 'NH투자증권', '삼성증권');
--rollback DROP TABLE IF EXISTS `underwriter_list`; 