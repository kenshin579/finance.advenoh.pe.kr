--liquibase formatted sql
--changeset ipo-blog:#002

-- ipo_info 인덱스
CREATE INDEX idx_ipo_info_company_name ON `ipo_info` (`company_name`);
CREATE INDEX idx_ipo_info_market_type ON `ipo_info` (`market_type`);
CREATE INDEX idx_ipo_info_created_at ON `ipo_info` (`created_at`);

-- financial_info 인덱스
CREATE INDEX idx_financial_info_stock_code ON `financial_info` (`stock_code`);
CREATE INDEX idx_financial_info_year ON `financial_info` (`year`);

-- offering_info 인덱스
CREATE INDEX idx_offering_info_stock_code ON `offering_info` (`stock_code`);
CREATE INDEX idx_offering_info_listing_date ON `offering_info` (`listing_date`);
CREATE INDEX idx_offering_info_underwriters ON `offering_info` (`underwriters`(100));

-- news_info 인덱스
CREATE INDEX idx_news_info_stock_code ON `news_info` (`stock_code`);
CREATE INDEX idx_news_info_published_date ON `news_info` (`published_date`);

-- posting_history 인덱스
CREATE INDEX idx_posting_history_stock_code ON `posting_history` (`stock_code`);
CREATE INDEX idx_posting_history_created_at ON `posting_history` (`created_at`);

--rollback DROP INDEX idx_posting_history_created_at ON `posting_history`;
--rollback DROP INDEX idx_posting_history_stock_code ON `posting_history`;
--rollback DROP INDEX idx_news_info_published_date ON `news_info`;
--rollback DROP INDEX idx_news_info_stock_code ON `news_info`;
--rollback DROP INDEX idx_offering_info_underwriters ON `offering_info`;
--rollback DROP INDEX idx_offering_info_listing_date ON `offering_info`;
--rollback DROP INDEX idx_offering_info_stock_code ON `offering_info`;
--rollback DROP INDEX idx_financial_info_year ON `financial_info`;
--rollback DROP INDEX idx_financial_info_stock_code ON `financial_info`;
--rollback DROP INDEX idx_ipo_info_created_at ON `ipo_info`;
--rollback DROP INDEX idx_ipo_info_market_type ON `ipo_info`;
--rollback DROP INDEX idx_ipo_info_company_name ON `ipo_info`; 