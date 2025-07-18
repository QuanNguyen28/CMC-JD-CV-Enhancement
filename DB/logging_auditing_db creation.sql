-- Tạo Database
CREATE DATABASE IF NOT EXISTS `logging_auditing_db`
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- Sử dụng Database
USE `logging_auditing_db`;

-- 1. Bảng: `user_queries`
CREATE TABLE `user_queries` (
    `query_log_id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT, -- Ghi nhận user_id từ access_control_db.users
    `query_text` TEXT NOT NULL,
    `query_timestamp` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `user_role` VARCHAR(50),
    `user_branch_id` INT,
    `status` VARCHAR(50) NOT NULL, -- Ví dụ: 'PENDING', 'SUCCESS', 'FAILED', 'DENIED_PERMISSION'
    `error_message` TEXT,
    `response_summary` TEXT
    -- FK tới access_control_db.users.user_id KHÔNG được thiết lập trực tiếp ở đây
    -- vì các database độc lập. Việc liên kết sẽ được thực hiện ở tầng ứng dụng hoặc BI/Analytics.
    -- Nếu bạn muốn liên kết chặt chẽ hơn, bạn cần tạo FK sau khi tất cả các DB đã tồn tại
    -- và có thể truy cập lẫn nhau, ví dụ: FOREIGN KEY (`user_id`) REFERENCES `access_control_db`.`users`(`user_id`)
) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 2. Bảng: `ai_agent_executions`
CREATE TABLE `ai_agent_executions` (
    `execution_id` INT AUTO_INCREMENT PRIMARY KEY,
    `query_log_id` INT NOT NULL,
    `agent_id` INT, -- Ghi nhận agent_id từ metadata_management_db.ai_agents
    `execution_timestamp` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `input_parameters_json` JSON,
    `generated_sql` TEXT,
    `applied_rls_filters_json` JSON,
    `status` VARCHAR(50) NOT NULL, -- Ví dụ: 'SUCCESS', 'FAILED'
    `duration_ms` INT,
    `error_details` TEXT,
    `returned_data_sample` JSON,
    FOREIGN KEY (`query_log_id`) REFERENCES `user_queries`(`query_log_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
    -- FK tới metadata_management_db.ai_agents.agent_id cũng cần được quản lý ở tầng ứng dụng/BI
) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;


-- 3. Bảng: `access_control_audits`
CREATE TABLE `access_control_audits` (
    `audit_id` INT AUTO_INCREMENT PRIMARY KEY,
    `request_timestamp` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `requester_user_id` INT,
    `requester_service` VARCHAR(100) NOT NULL, -- Ví dụ: 'N8n', 'AI_Agent_Finance_Query', 'LLM_Brain', 'AccessControlAPI'
    `resource_id` INT, -- Ghi nhận resource_id từ access_control_db.resources
    `requested_access_level` VARCHAR(50) NOT NULL, -- Ví dụ: 'READ', 'WRITE', 'EXECUTE', 'DENY' (là yêu cầu ban đầu)
    `context_json` JSON, -- Ngữ cảnh của yêu cầu
    `decision` VARCHAR(50) NOT NULL, -- 'GRANTED' hoặc 'DENIED'
    `denial_reason` TEXT,
    `applied_filters_json` JSON -- Các bộ lọc RLS/CLS đã được cấp (nếu granted)
    -- FK tới access_control_db.resources.resource_id cũng cần được quản lý ở tầng ứng dụng/BI
) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- --------------------------------------------------------------------------------

-- Dummy Data cho `user_queries`
-- (Giả sử các user_id này tồn tại trong access_control_db.users)
INSERT INTO `user_queries` (user_id, query_text, query_timestamp, user_role, user_branch_id, status, response_summary) VALUES
(1, 'Doanh thu tổng hợp theo quý của toàn công ty là bao nhiêu?', NOW(), 'LEADER', NULL, 'SUCCESS', 'Doanh thu quý 2 năm 2025 là X tỷ VND.'),
(2, 'Cho tôi doanh số quý 1 năm 2025 tại chi nhánh Hồ Chí Minh', NOW(), 'FINANCE_SPECIALIST', (SELECT branch_id FROM access_control_db.branches WHERE branch_name = 'Ho Chi Minh Branch'), 'SUCCESS', 'Doanh số quý 1/2025 tại HCM là 500 tỷ VND.'),
(3, 'Danh sách nhân viên phòng Marketing tại Hà Nội kèm mức lương', NOW(), 'HR_SPECIALIST', (SELECT branch_id FROM access_control_db.branches WHERE branch_name = 'Hanoi Branch'), 'SUCCESS', 'Đã cung cấp danh sách nhân viên Marketing và mức lương tại chi nhánh Hà Nội.'),
(4, 'Báo cáo tổng quan về sản phẩm bán chạy nhất tháng trước', NOW(), 'NORMAL_USER', (SELECT branch_id FROM access_control_db.branches WHERE branch_name = 'Hanoi Branch'), 'SUCCESS', 'Sản phẩm X là bán chạy nhất trong tháng 6/2025.'),
(2, 'Truy vấn chi tiết lương của giám đốc chi nhánh Đà Nẵng', NOW(), 'FINANCE_SPECIALIST', (SELECT branch_id FROM access_control_db.branches WHERE branch_name = 'Ho Chi Minh Branch'), 'DENIED_PERMISSION', 'Không có quyền truy cập thông tin này do quy tắc bảo mật.');


-- Dummy Data cho `ai_agent_executions`
-- (Giả sử các query_log_id từ bảng `user_queries` và agent_id từ `metadata_management_db.ai_agents` đã tồn tại)
INSERT INTO `ai_agent_executions` (query_log_id, agent_id, execution_timestamp, input_parameters_json, generated_sql, applied_rls_filters_json, status, duration_ms, returned_data_sample) VALUES
((SELECT query_log_id FROM user_queries WHERE query_text LIKE 'Doanh thu tổng hợp%'), (SELECT agent_id FROM metadata_management_db.ai_agents WHERE agent_name = 'Sales_Report_Generator'), NOW(), '{"time_period": "Q2 2025", "granularity": "company_wide"}', 'SELECT SUM(sales_amount) FROM dwh_main.public.fact_sales_transactions WHERE transaction_date BETWEEN ''2025-04-01'' AND ''2025-06-30'';', NULL, 'SUCCESS', 2500, '{"total_sales_q2_2025": 1200000000000}'),
((SELECT query_log_id FROM user_queries WHERE query_text LIKE 'Cho tôi doanh số quý 1 năm 2025 tại chi nhánh Hồ Chí Minh'), (SELECT agent_id FROM metadata_management_db.ai_agents WHERE agent_name = 'Sales_Report_Generator'), NOW(), '{"time_period": "Q1 2025", "branch_name": "Ho Chi Minh Branch"}', 'SELECT SUM(sales_amount) FROM dwh_main.public.fact_sales_transactions WHERE transaction_date BETWEEN ''2025-01-01'' AND ''2025-03-31'' AND branch_id = (SELECT branch_id FROM access_control_db.branches WHERE branch_name = ''Ho Chi Minh Branch'');', '{"table": "fact_sales_transactions", "filter_column": "branch_id", "filter_value": 2}', 'SUCCESS', 1800, '{"total_sales_q1_2025_hcm": 500000000000}'),
((SELECT query_log_id FROM user_queries WHERE query_text LIKE 'Danh sách nhân viên phòng Marketing tại Hà Nội%'), (SELECT agent_id FROM metadata_management_db.ai_agents WHERE agent_name = 'HR_Compensation_Analyzer'), NOW(), '{"department": "Marketing", "branch_name": "Hanoi Branch", "include_salary": true}', 'SELECT employee_name, salary FROM dwh_main.public.dim_employees WHERE department = ''Marketing'' AND branch_id = (SELECT branch_id FROM access_control_db.branches WHERE branch_name = ''Hanoi Branch'');', '{"table": "dim_employees", "filter_column": "branch_id", "filter_value": 1}', 'SUCCESS', 900, '[{"employee_name": "Nguyen Van X", "salary": 18000000}, {"employee_name": "Le Thi Y", "salary": 16500000}]'),
((SELECT query_log_id FROM user_queries WHERE query_text LIKE 'Truy vấn chi tiết lương của giám đốc chi nhánh Đà Nẵng'), (SELECT agent_id FROM metadata_management_db.ai_agents WHERE agent_name = 'HR_Compensation_Analyzer'), NOW(), '{"employee_position": "Director", "branch_name": "Da Nang Branch", "include_salary": true}', NULL, NULL, 'FAILED', 100, 'Error: Access Denied for salary details of Director in Da Nang Branch.');


-- Dummy Data cho `access_control_audits`
-- (Giả sử các user_id từ `access_control_db.users` và resource_id từ `access_control_db.resources` đã tồn tại)
INSERT INTO `access_control_audits` (request_timestamp, requester_user_id, requester_service, resource_id, requested_access_level, context_json, decision, denial_reason, applied_filters_json) VALUES
(NOW(), (SELECT user_id FROM access_control_db.users WHERE username = 'tranvanb'), 'N8n', (SELECT resource_id FROM access_control_db.resources WHERE resource_name = 'AI_AGENT_FINANCE_QUERY'), 'EXECUTE', '{"user_role": "FINANCE_SPECIALIST", "user_branch_id": 2}', 'GRANTED', NULL, NULL),
(NOW(), (SELECT user_id FROM access_control_db.users WHERE username = 'tranvanb'), 'AI_Agent_Finance_Query', (SELECT resource_id FROM access_control_db.resources WHERE resource_name = 'TABLE_SALES_TRANSACTIONS'), 'READ', '{"user_role": "FINANCE_SPECIALIST", "user_branch_id": 2}', 'GRANTED', NULL, '{"table": "fact_sales_transactions", "filter_column": "branch_id", "filter_value": 2}'),
(NOW(), (SELECT user_id FROM access_control_db.users WHERE username = 'lethic'), 'N8n', (SELECT resource_id FROM access_control_db.resources WHERE resource_name = 'AI_AGENT_HR_ANALYTICS'), 'EXECUTE', '{"user_role": "HR_SPECIALIST", "user_branch_id": 1}', 'GRANTED', NULL, NULL),
(NOW(), (SELECT user_id FROM access_control_db.users WHERE username = 'tranvanb'), 'LLM_Brain', (SELECT resource_id FROM access_control_db.resources WHERE resource_name = 'COLUMN_EMPLOYEE_SALARY'), 'READ', '{"user_role": "FINANCE_SPECIALIST", "user_branch_id": 2}', 'DENIED', 'Role does not have permission to access COLUMN_EMPLOYEE_SALARY', NULL),
(NOW(), (SELECT user_id FROM access_control_db.users WHERE username = 'phamvand'), 'N8n', (SELECT resource_id FROM access_control_db.resources WHERE resource_name = 'API_GET_HR_DETAILS'), 'READ', '{"user_role": "NORMAL_USER", "user_branch_id": 1}', 'DENIED', 'Role NORMAL_USER does not have access to API_GET_HR_DETAILS', NULL);
