use access_control_db;

-- Tạo Database
CREATE DATABASE IF NOT EXISTS `access_control_db`
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- Sử dụng Database
USE `access_control_db`;

-- 1. Bảng: `users`
CREATE TABLE `users` (
    `user_id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(100) NOT NULL UNIQUE,
    `full_name` VARCHAR(255),
    `email` VARCHAR(255) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Dummy Data cho `users`
INSERT INTO `users` (username, full_name, email, password_hash, is_active) VALUES
('nguyenvana', 'Nguyễn Văn A', 'ana.nguyen@example.com', 'hashed_pass_A', TRUE),
('tranvanb', 'Trần Văn B', 'vanb.tran@example.com', 'hashed_pass_B', TRUE),
('lethic', 'Lê Thị C', 'thic.le@example.com', 'hashed_pass_C', TRUE),
('phamvand', 'Phạm Văn D', 'vand.pham@example.com', 'hashed_pass_D', TRUE),
('hoangthie', 'Hoàng Thị E', 'thie.hoang@example.com', 'hashed_pass_E', TRUE);

-- 2. Bảng: `roles`
CREATE TABLE `roles` (
    `role_id` INT AUTO_INCREMENT PRIMARY KEY,
    `role_name` VARCHAR(50) NOT NULL UNIQUE,
    `description` TEXT
) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Dummy Data cho `roles`
INSERT INTO `roles` (role_name, description) VALUES
('LEADER', 'Người dùng cấp lãnh đạo, truy cập dữ liệu tổng hợp.'),
('FINANCE_SPECIALIST', 'Chuyên gia tài chính, truy cập chi tiết dữ liệu tài chính.'),
('HR_SPECIALIST', 'Chuyên gia nhân sự, truy cập chi tiết dữ liệu nhân sự.'),
('NORMAL_USER', 'Người dùng thông thường, truy cập thông tin chung.'),
('SALES_SPECIALIST', 'Chuyên gia bán hàng, truy cập chi tiết dữ liệu bán hàng.'),
('IT_ADMIN', 'Quản trị viên hệ thống.');

-- 3. Bảng: `user_roles`
CREATE TABLE `user_roles` (
    `user_role_id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `role_id` INT NOT NULL,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
    FOREIGN KEY (`role_id`) REFERENCES `roles`(`role_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
    UNIQUE (`user_id`, `role_id`)
) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Dummy Data cho `user_roles`
-- Lấy user_id và role_id từ bảng `users` và `roles` (có thể cần SELECT để đảm bảo đúng ID)
INSERT INTO `user_roles` (user_id, role_id) VALUES
((SELECT user_id FROM users WHERE username = 'nguyenvana'), (SELECT role_id FROM roles WHERE role_name = 'LEADER')),
((SELECT user_id FROM users WHERE username = 'tranvanb'), (SELECT role_id FROM roles WHERE role_name = 'FINANCE_SPECIALIST')),
((SELECT user_id FROM users WHERE username = 'tranvanb'), (SELECT role_id FROM roles WHERE role_name = 'NORMAL_USER')),
((SELECT user_id FROM users WHERE username = 'lethic'), (SELECT role_id FROM roles WHERE role_name = 'HR_SPECIALIST')),
((SELECT user_id FROM users WHERE username = 'phamvand'), (SELECT role_id FROM roles WHERE role_name = 'NORMAL_USER')),
((SELECT user_id FROM users WHERE username = 'hoangthie'), (SELECT role_id FROM roles WHERE role_name = 'SALES_SPECIALIST'));


-- 4. Bảng: `branches`
CREATE TABLE `branches` (
    `branch_id` INT AUTO_INCREMENT PRIMARY KEY,
    `branch_name` VARCHAR(100) NOT NULL UNIQUE,
    `region` VARCHAR(50)
) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Dummy Data cho `branches`
INSERT INTO `branches` (branch_name, region) VALUES
('Hanoi Branch', 'North'),
('Ho Chi Minh Branch', 'South'),
('Da Nang Branch', 'Central');

-- 5. Bảng: `user_branches`
CREATE TABLE `user_branches` (
    `user_branch_id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `branch_id` INT NOT NULL,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
    FOREIGN KEY (`branch_id`) REFERENCES `branches`(`branch_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
    UNIQUE (`user_id`, `branch_id`)
) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Dummy Data cho `user_branches`
INSERT INTO `user_branches` (user_id, branch_id) VALUES
((SELECT user_id FROM users WHERE username = 'nguyenvana'), (SELECT branch_id FROM branches WHERE branch_name = 'Hanoi Branch')),
((SELECT user_id FROM users WHERE username = 'nguyenvana'), (SELECT branch_id FROM branches WHERE branch_name = 'Ho Chi Minh Branch')),
((SELECT user_id FROM users WHERE username = 'tranvanb'), (SELECT branch_id FROM branches WHERE branch_name = 'Ho Chi Minh Branch')),
((SELECT user_id FROM users WHERE username = 'lethic'), (SELECT branch_id FROM branches WHERE branch_name = 'Hanoi Branch')),
((SELECT user_id FROM users WHERE username = 'phamvand'), (SELECT branch_id FROM branches WHERE branch_name = 'Hanoi Branch')),
((SELECT user_id FROM users WHERE username = 'phamvand'), (SELECT branch_id FROM branches WHERE branch_name = 'Da Nang Branch')),
((SELECT user_id FROM users WHERE username = 'hoangthie'), (SELECT branch_id FROM branches WHERE branch_name = 'Ho Chi Minh Branch'));


-- 6. Bảng: `resources`
CREATE TABLE `resources` (
    `resource_id` INT AUTO_INCREMENT PRIMARY KEY,
    `resource_name` VARCHAR(255) NOT NULL UNIQUE,
    `resource_type` VARCHAR(50) NOT NULL, -- Ví dụ: 'API', 'TABLE', 'COLUMN', 'KNOWLEDGE_SOURCE', 'AI_AGENT', 'DASHBOARD'
    `description` TEXT
) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Dummy Data cho `resources`
INSERT INTO `resources` (resource_name, resource_type, description) VALUES
('API_GET_SALES_SUMMARY', 'API', 'API để lấy tổng quan doanh thu.'),
('API_GET_HR_DETAILS', 'API', 'API để lấy chi tiết thông tin nhân sự.'),
('TABLE_SALES_TRANSACTIONS', 'TABLE', 'Bảng chứa các giao dịch bán hàng chi tiết.'),
('TABLE_EMPLOYEE_DATA', 'TABLE', 'Bảng chứa dữ liệu nhân viên.'),
('COLUMN_EMPLOYEE_SALARY', 'COLUMN', 'Cột lương trong bảng nhân viên.'),
('KS_FINANCE_REPORTS', 'KNOWLEDGE_SOURCE', 'Knowledge Source về các báo cáo tài chính.'),
('KS_HR_POLICIES', 'KNOWLEDGE_SOURCE', 'Knowledge Source về các chính sách nhân sự.'),
('AI_AGENT_FINANCE_QUERY', 'AI_AGENT', 'AI Agent chuyên xử lý truy vấn tài chính.'),
('AI_AGENT_HR_ANALYTICS', 'AI_AGENT', 'AI Agent chuyên xử lý phân tích nhân sự.'),
('DASHBOARD_SALES_OVERVIEW', 'DASHBOARD', 'Dashboard tổng quan về doanh số.'),
('DASHBOARD_HR_COMPENSATION', 'DASHBOARD', 'Dashboard về chính sách lương thưởng.');


-- 7. Bảng: `permissions`
CREATE TABLE `permissions` (
    `permission_id` INT AUTO_INCREMENT PRIMARY KEY,
    `role_id` INT NOT NULL,
    `resource_id` INT NOT NULL,
    `access_level` VARCHAR(50) NOT NULL, -- Ví dụ: 'READ', 'WRITE', 'EXECUTE', 'DENY'
    `applies_to_branches` JSON, -- Lưu trữ mảng các BranchID, ví dụ: [1, 2] hoặc NULL cho tất cả
    `condition_expression` JSON, -- Biểu thức điều kiện cho RLS/CLS
    `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (`role_id`) REFERENCES `roles`(`role_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
    FOREIGN KEY (`resource_id`) REFERENCES `resources`(`resource_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Dummy Data cho `permissions`
INSERT INTO `permissions` (role_id, resource_id, access_level, applies_to_branches, condition_expression, is_active) VALUES
-- LEADER có thể READ tổng quan doanh thu (API, DASHBOARD)
((SELECT role_id FROM roles WHERE role_name = 'LEADER'), (SELECT resource_id FROM resources WHERE resource_name = 'API_GET_SALES_SUMMARY'), 'READ', NULL, NULL, TRUE),
((SELECT role_id FROM roles WHERE role_name = 'LEADER'), (SELECT resource_id FROM resources WHERE resource_name = 'DASHBOARD_SALES_OVERVIEW'), 'READ', NULL, NULL, TRUE),
-- LEADER có thể READ bảng sales transactions của các chi nhánh mà họ được gán (RLS)
((SELECT role_id FROM roles WHERE role_name = 'LEADER'), (SELECT resource_id FROM resources WHERE resource_name = 'TABLE_SALES_TRANSACTIONS'), 'READ', NULL, '{"table": "fact_sales_transactions", "filter_column": "branch_id", "filter_value_source": "user_branch_ids", "operator": "IN"}', TRUE),

-- FINANCE_SPECIALIST có thể READ API/TABLE/KS/AI_AGENT tài chính
((SELECT role_id FROM roles WHERE role_name = 'FINANCE_SPECIALIST'), (SELECT resource_id FROM resources WHERE resource_name = 'API_GET_SALES_SUMMARY'), 'READ', NULL, NULL, TRUE),
((SELECT role_id FROM roles WHERE role_name = 'FINANCE_SPECIALIST'), (SELECT resource_id FROM resources WHERE resource_name = 'TABLE_SALES_TRANSACTIONS'), 'READ', NULL, '{"table": "fact_sales_transactions", "filter_column": "branch_id", "filter_value_source": "user_branch_ids", "operator": "IN"}', TRUE),
((SELECT role_id FROM roles WHERE role_name = 'FINANCE_SPECIALIST'), (SELECT resource_id FROM resources WHERE resource_name = 'KS_FINANCE_REPORTS'), 'READ', NULL, NULL, TRUE),
((SELECT role_id FROM roles WHERE role_name = 'FINANCE_SPECIALIST'), (SELECT resource_id FROM resources WHERE resource_name = 'AI_AGENT_FINANCE_QUERY'), 'EXECUTE', NULL, NULL, TRUE),
-- FINANCE_SPECIALIST không được truy cập cột lương (DENY rule)
((SELECT role_id FROM roles WHERE role_name = 'FINANCE_SPECIALIST'), (SELECT resource_id FROM resources WHERE resource_name = 'COLUMN_EMPLOYEE_SALARY'), 'DENY', NULL, NULL, TRUE),

-- HR_SPECIALIST có thể READ API/TABLE/KS/AI_AGENT nhân sự
((SELECT role_id FROM roles WHERE role_name = 'HR_SPECIALIST'), (SELECT resource_id FROM resources WHERE resource_name = 'API_GET_HR_DETAILS'), 'READ', NULL, NULL, TRUE),
((SELECT role_id FROM roles WHERE role_name = 'HR_SPECIALIST'), (SELECT resource_id FROM resources WHERE resource_name = 'TABLE_EMPLOYEE_DATA'), 'READ', NULL, '{"table": "dim_employees", "filter_column": "branch_id", "filter_value_source": "user_branch_ids", "operator": "IN"}', TRUE),
((SELECT role_id FROM roles WHERE role_name = 'HR_SPECIALIST'), (SELECT resource_id FROM resources WHERE resource_name = 'COLUMN_EMPLOYEE_SALARY'), 'READ', NULL, NULL, TRUE), -- HR Specialist CAN see salary
((SELECT role_id FROM roles WHERE role_name = 'HR_SPECIALIST'), (SELECT resource_id FROM resources WHERE resource_name = 'KS_HR_POLICIES'), 'READ', NULL, NULL, TRUE),
((SELECT role_id FROM roles WHERE role_name = 'HR_SPECIALIST'), (SELECT resource_id FROM resources WHERE resource_name = 'AI_AGENT_HR_ANALYTICS'), 'EXECUTE', NULL, NULL, TRUE),
((SELECT role_id FROM roles WHERE role_name = 'HR_SPECIALIST'), (SELECT resource_id FROM resources WHERE resource_name = 'DASHBOARD_HR_COMPENSATION'), 'READ', NULL, NULL, TRUE),

-- NORMAL_USER chỉ có thể xem báo cáo tổng quan và Q&A chung
((SELECT role_id FROM roles WHERE role_name = 'NORMAL_USER'), (SELECT resource_id FROM resources WHERE resource_name = 'API_GET_SALES_SUMMARY'), 'READ', NULL, NULL, TRUE),
((SELECT role_id FROM roles WHERE role_name = 'NORMAL_USER'), (SELECT resource_id FROM resources WHERE resource_name = 'DASHBOARD_SALES_OVERVIEW'), 'READ', NULL, NULL, TRUE);