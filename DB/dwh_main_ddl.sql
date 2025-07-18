CREATE DATABASE IF NOT EXISTS `dwh_main` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `dwh_main`;

-- SALES & MARKETING DATAMART

CREATE TABLE dim_customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(30),
    address TEXT,
    created_date DATE
);

CREATE TABLE dim_products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    product_name VARCHAR(100),
    category VARCHAR(50),
    price DECIMAL(10, 2)
);

CREATE TABLE dim_sales_agents (
    agent_id INT PRIMARY KEY AUTO_INCREMENT,
    agent_name VARCHAR(100),
    region VARCHAR(50),
    hire_date DATE
);

CREATE TABLE fact_sales (
    sale_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    product_id INT,
    agent_id INT,
    sale_date DATE,
    quantity INT,
    total_amount DECIMAL(12, 2),
    FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES dim_products(product_id),
    FOREIGN KEY (agent_id) REFERENCES dim_sales_agents(agent_id)
);

-- FINANCE & HR DATAMART

CREATE TABLE dim_departments (
    department_id INT PRIMARY KEY AUTO_INCREMENT,
    department_name VARCHAR(100)
);

CREATE TABLE dim_employees (
    employee_id INT PRIMARY KEY AUTO_INCREMENT,
    employee_name VARCHAR(100),
    department_id INT,
    hire_date DATE,
    salary DECIMAL(12, 2),
    FOREIGN KEY (department_id) REFERENCES dim_departments(department_id)
);

CREATE TABLE fact_payroll (
    payroll_id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id INT,
    pay_month VARCHAR(7),
    base_salary DECIMAL(12, 2),
    bonus DECIMAL(12, 2),
    deductions DECIMAL(12, 2),
    FOREIGN KEY (employee_id) REFERENCES dim_employees(employee_id)
);

CREATE TABLE fact_expenses (
    expense_id INT PRIMARY KEY AUTO_INCREMENT,
    department_id INT,
    employee_id INT,
    expense_date DATE,
    category VARCHAR(50),
    amount DECIMAL(12, 2),
    FOREIGN KEY (department_id) REFERENCES dim_departments(department_id),
    FOREIGN KEY (employee_id) REFERENCES dim_employees(employee_id)
);
