"""
-- 全自动发货系统数据库
CREATE TABLE auto_deliver_orders (
    order_id VARCHAR(64) PRIMARY KEY,
    platform ENUM('xianyu','gumroad','fiverr') NOT NULL,
    product_type ENUM('photo_restore','pdf_pack','prompt_pack') NOT NULL,
    buyer_email VARCHAR(128),
    delivery_link TEXT,
    status ENUM('pending','sent','refunded') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_status ON auto_deliver_orders(status);
"""
