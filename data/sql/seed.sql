INSERT OR REPLACE INTO letter_batches (batch_id, template_code, status, error_code, created_at) VALUES
('B-1001', 'NOTICE_A', 'COMPLETED', NULL, '2026-05-17T09:02:10Z'),
('B-1002', 'LCD_XFER', 'FAILED', 'LCD_FILE_TIMEOUT', '2026-05-17T10:11:21Z'),
('B-1003', 'DISCLOSURE_B', 'FAILED', 'TEMPLATE_RULE_MISS', '2026-05-17T10:20:03Z');

INSERT OR REPLACE INTO mock_customers (customer_id, segment, communication_preference) VALUES
('CUST-MOCK-001', 'Retail', 'Paper'),
('CUST-MOCK-002', 'Small Business', 'Digital'),
('CUST-MOCK-003', 'Wealth', 'Paper');

INSERT OR REPLACE INTO user_preferences (user_id, response_style, preferred_agent, preferred_detail_level) VALUES
('demo-user', 'concise', '', 'medium');

