use metadata_management_db;

-- Tạo Database
CREATE DATABASE IF NOT EXISTS `metadata_management_db`
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- Sử dụng Database
USE `metadata_management_db`;

-- 1. Bảng: `datamart_tables`
CREATE TABLE `datamart_tables` (
    `table_id` INT AUTO_INCREMENT PRIMARY KEY,
    `table_name` VARCHAR(100) NOT NULL,
    `database_name` VARCHAR(100) NOT NULL,
    `schema_name` VARCHAR(100) NOT NULL,
    `description` TEXT,
    `is_dimension` BOOLEAN NOT NULL,
    `last_updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE (`database_name`, `schema_name`, `table_name`)
) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Dummy Data cho `datamart_tables`
INSERT INTO `datamart_tables` (table_name, database_name, schema_name, description, is_dimension) VALUES
('fact_sales_transactions', 'dwh_main', 'public', 'Lưu trữ thông tin chi tiết về các giao dịch bán hàng, bao gồm doanh thu, số lượng, ngày.', FALSE),
('dim_customers', 'dwh_main', 'public', 'Lưu trữ thông tin chi tiết về khách hàng: tên, địa chỉ, loại khách hàng.', TRUE),
('dim_products', 'dwh_main', 'public', 'Lưu trữ thông tin chi tiết về sản phẩm: tên sản phẩm, danh mục, giá.', TRUE),
('fact_employee_compensation', 'dwh_main', 'public', 'Tổng hợp chi phí lương và thưởng của nhân viên theo tháng.', FALSE),
('dim_employees', 'dwh_main', 'public', 'Thông tin chi tiết về nhân viên: họ tên, phòng ban, chức danh, chi nhánh.', TRUE),
('fact_monthly_budget', 'dwh_main', 'finance', 'Dữ liệu ngân sách theo tháng và theo phòng ban.', FALSE);

-- 2. Bảng: `datamart_columns`
CREATE TABLE `datamart_columns` (
    `column_id` INT AUTO_INCREMENT PRIMARY KEY,
    `table_id` INT NOT NULL,
    `column_name` VARCHAR(100) NOT NULL,
    `data_type` VARCHAR(50) NOT NULL,
    `description` TEXT,
    `is_pk` BOOLEAN NOT NULL DEFAULT FALSE,
    `is_fk` BOOLEAN NOT NULL DEFAULT FALSE,
    `fk_references_table_id` INT,
    FOREIGN KEY (`table_id`) REFERENCES `datamart_tables`(`table_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
    FOREIGN KEY (`fk_references_table_id`) REFERENCES `datamart_tables`(`table_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
    UNIQUE (`table_id`, `column_name`)
) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Dummy Data cho `datamart_columns`
INSERT INTO `datamart_columns` (table_id, column_name, data_type, description, is_pk, is_fk, fk_references_table_id) VALUES
((SELECT table_id FROM datamart_tables WHERE table_name = 'fact_sales_transactions'), 'transaction_id', 'VARCHAR(50)', 'Mã giao dịch bán hàng duy nhất.', TRUE, FALSE, NULL),
((SELECT table_id FROM datamart_tables WHERE table_name = 'fact_sales_transactions'), 'customer_id', 'INT', 'Mã khách hàng.', FALSE, TRUE, (SELECT table_id FROM datamart_tables WHERE table_name = 'dim_customers')),
((SELECT table_id FROM datamart_tables WHERE table_name = 'fact_sales_transactions'), 'product_id', 'INT', 'Mã sản phẩm.', FALSE, TRUE, (SELECT table_id FROM datamart_tables WHERE table_name = 'dim_products')),
((SELECT table_id FROM datamart_tables WHERE table_name = 'fact_sales_transactions'), 'transaction_date', 'DATE', 'Ngày phát sinh giao dịch.', FALSE, FALSE, NULL),
((SELECT table_id FROM datamart_tables WHERE table_name = 'fact_sales_transactions'), 'sales_amount', 'NUMERIC(18,2)', 'Doanh thu từ giao dịch.', FALSE, FALSE, NULL),
((SELECT table_id FROM datamart_tables WHERE table_name = 'fact_sales_transactions'), 'quantity', 'INT', 'Số lượng sản phẩm bán ra.', FALSE, FALSE, NULL),
((SELECT table_id FROM datamart_tables WHERE table_name = 'fact_sales_transactions'), 'branch_id', 'INT', 'Mã chi nhánh phát sinh giao dịch.', FALSE, FALSE, NULL),

((SELECT table_id FROM datamart_tables WHERE table_name = 'dim_customers'), 'customer_id', 'INT', 'Mã khách hàng duy nhất.', TRUE, FALSE, NULL),
((SELECT table_id FROM datamart_tables WHERE table_name = 'dim_customers'), 'customer_name', 'VARCHAR(255)', 'Tên khách hàng.', FALSE, FALSE, NULL),
((SELECT table_id FROM datamart_tables WHERE table_name = 'dim_customers'), 'customer_type', 'VARCHAR(50)', 'Loại khách hàng (Cá nhân, Doanh nghiệp).', FALSE, FALSE, NULL),
((SELECT table_id FROM datamart_tables WHERE table_name = 'dim_customers'), 'city', 'VARCHAR(100)', 'Thành phố của khách hàng.', FALSE, FALSE, NULL),

((SELECT table_id FROM datamart_tables WHERE table_name = 'dim_products'), 'product_id', 'INT', 'Mã sản phẩm duy nhất.', TRUE, FALSE, NULL),
((SELECT table_id FROM datamart_tables WHERE table_name = 'dim_products'), 'product_name', 'VARCHAR(255)', 'Tên sản phẩm.', FALSE, FALSE, NULL),
((SELECT table_id FROM datamart_tables WHERE table_name = 'dim_products'), 'category', 'VARCHAR(100)', 'Danh mục sản phẩm.', FALSE, FALSE, NULL),

((SELECT table_id FROM datamart_tables WHERE table_name = 'fact_employee_compensation'), 'employee_id', 'INT', 'Mã nhân viên.', FALSE, TRUE, (SELECT table_id FROM datamart_tables WHERE table_name = 'dim_employees')),
((SELECT table_id FROM datamart_tables WHERE table_name = 'fact_employee_compensation'), 'pay_month', 'DATE', 'Tháng chi trả lương.', FALSE, FALSE, NULL),
((SELECT table_id FROM datamart_tables WHERE table_name = 'fact_employee_compensation'), 'total_salary', 'NUMERIC(18,2)', 'Tổng lương thực nhận của nhân viên.', FALSE, FALSE, NULL),

((SELECT table_id FROM datamart_tables WHERE table_name = 'dim_employees'), 'employee_id', 'INT', 'Mã nhân viên duy nhất.', TRUE, FALSE, NULL),
((SELECT table_id FROM datamart_tables WHERE table_name = 'dim_employees'), 'employee_name', 'VARCHAR(255)', 'Tên nhân viên.', FALSE, FALSE, NULL),
((SELECT table_id FROM datamart_tables WHERE table_name = 'dim_employees'), 'department', 'VARCHAR(100)', 'Phòng ban công tác.', FALSE, FALSE, NULL),
((SELECT table_id FROM datamart_tables WHERE table_name = 'dim_employees'), 'branch_id', 'INT', 'Mã chi nhánh nhân viên làm việc.', FALSE, FALSE, NULL),
((SELECT table_id FROM datamart_tables WHERE table_name = 'dim_employees'), 'position', 'VARCHAR(100)', 'Chức danh của nhân viên.', FALSE, FALSE, NULL),
((SELECT table_id FROM datamart_tables WHERE table_name = 'dim_employees'), 'salary', 'NUMERIC(18,2)', 'Mức lương cơ bản của nhân viên.', FALSE, FALSE, NULL),

((SELECT table_id FROM datamart_tables WHERE table_name = 'fact_monthly_budget'), 'budget_id', 'INT', 'Mã ngân sách duy nhất.', TRUE, FALSE, NULL),
((SELECT table_id FROM datamart_tables WHERE table_name = 'fact_monthly_budget'), 'month', 'DATE', 'Tháng áp dụng ngân sách.', FALSE, FALSE, NULL),
((SELECT table_id FROM datamart_tables WHERE table_name = 'fact_monthly_budget'), 'department', 'VARCHAR(100)', 'Phòng ban được cấp ngân sách.', FALSE, FALSE, NULL),
((SELECT table_id FROM datamart_tables WHERE table_name = 'fact_monthly_budget'), 'allocated_amount', 'NUMERIC(18,2)', 'Số tiền ngân sách được phân bổ.', FALSE, FALSE, NULL);

-- 3. Bảng: `ai_agents`
CREATE TABLE `ai_agents` (
    `agent_id` INT AUTO_INCREMENT PRIMARY KEY,
    `agent_name` VARCHAR(100) NOT NULL UNIQUE,
    `description` TEXT,
    `endpoint_url` VARCHAR(255) NOT NULL,
    `input_schema_json` JSON,
    `output_schema_json` JSON,
    `example_prompts` JSON,
    `is_active` BOOLEAN NOT NULL DEFAULT TRUE
) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Dummy Data cho `ai_agents`
INSERT INTO `ai_agents` (agent_name, description, endpoint_url, example_prompts, is_active) VALUES
('Sales_Report_Generator', 'Tạo báo cáo doanh thu, phân tích doanh số theo sản phẩm, khách hàng, chi nhánh.', 'http://ai-agents-service/api/sales_report', '["Cho tôi báo cáo doanh thu theo tháng của sản phẩm A tại chi nhánh Hà Nội", "Doanh số quý này theo từng chi nhánh là bao nhiêu?"]', TRUE),
('HR_Compensation_Analyzer', 'Phân tích chi phí lương thưởng, so sánh lương theo phòng ban, chức danh.', 'http://ai-agents-service/api/hr_compensation', '["Tổng chi phí lương tháng 5 của phòng Marketing?", "Mức lương trung bình của nhân viên phòng ban A so với phòng ban B?"]', TRUE),
('Dashboard_Creator', 'Tạo mới hoặc tùy chỉnh PowerBI Dashboard dựa trên yêu cầu ngôn ngữ tự nhiên.', 'http://ai-agents-service/api/dashboard_creator', '["Tạo dashboard hiển thị doanh thu theo khu vực và loại khách hàng", "Thêm biểu đồ cột cho doanh số sản phẩm hot nhất quý này."]', TRUE),
('Budget_Forecaster', 'Dự báo ngân sách cho các phòng ban dựa trên dữ liệu lịch sử.', 'http://ai-agents-service/api/budget_forecast', '["Dự báo ngân sách cho phòng IT quý tới", "Tổng ngân sách cần cho năm sau là bao nhiêu?"]', TRUE);


-- 4. Bảng: `api_microservices`
CREATE TABLE `api_microservices` (
    `api_id` INT AUTO_INCREMENT PRIMARY KEY,
    `api_name` VARCHAR(100) NOT NULL UNIQUE,
    `description` TEXT,
    `endpoint_url` VARCHAR(255) NOT NULL,
    `method` VARCHAR(10) NOT NULL, -- Ví dụ: 'GET', 'POST'
    `input_params_json` JSON,
    `output_schema_json` JSON,
    `is_active` BOOLEAN NOT NULL DEFAULT TRUE
) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Dummy Data cho `api_microservices`
INSERT INTO `api_microservices` (api_name, description, endpoint_url, method, is_active) VALUES
('CRM_Customer_Details', 'Lấy thông tin chi tiết của một khách hàng từ hệ thống CRM.', 'http://crm-service/api/customers/{customer_id}', 'GET', TRUE),
('SAP_Purchase_Order', 'Truy vấn chi tiết đơn đặt hàng từ SAP.', 'http://sap-service/api/purchase_orders/{order_id}', 'GET', TRUE),
('HRIS_Employee_Profile', 'Truy vấn hồ sơ nhân viên từ hệ thống HRIS.', 'http://hris-service/api/employees/{employee_id}', 'GET', TRUE);