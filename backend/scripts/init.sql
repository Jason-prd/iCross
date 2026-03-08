-- iCross Database Initialization Script

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create basic indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_team_status ON users(id) INCLUDE (status);

CREATE INDEX IF NOT EXISTS idx_team_members_team_user ON team_members(team_id, user_id);
CREATE INDEX IF NOT EXISTS idx_team_members_status ON team_members(status);

CREATE INDEX IF NOT EXISTS idx_shops_team_platform ON shops(team_id, platform);
CREATE INDEX IF NOT EXISTS idx_shops_status ON shops(status);

CREATE INDEX IF NOT EXISTS idx_products_team ON products(team_id);
CREATE INDEX IF NOT EXISTS idx_products_status ON products(status);
CREATE INDEX IF NOT EXISTS idx_products_sku ON products(master_sku);

CREATE INDEX IF NOT EXISTS idx_orders_team ON orders(team_id);
CREATE INDEX IF NOT EXISTS idx_orders_shop ON orders(shop_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_created ON orders(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_inventory_team_product ON inventory(team_id, product_id);
CREATE INDEX IF NOT EXISTS idx_inventory_warehouse ON inventory(warehouse_id);

CREATE INDEX IF NOT EXISTS idx_customers_team ON customers(team_id);
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);

-- Insert default roles
INSERT INTO roles (name, description, permissions) VALUES
    ('super_admin', 'Super Administrator', '{"all": true}'),
    ('admin', 'Administrator', '{"users": ["read", "write"], "shops": ["read", "write"], "products": ["read", "write"], "orders": ["read", "write"], "inventory": ["read", "write"], "customers": ["read", "write"]}'),
    ('operator', 'Operator', '{"products": ["read", "write"], "orders": ["read", "write"], "inventory": ["read", "write"]}'),
    ('cs', 'Customer Service', '{"orders": ["read", "write"], "customers": ["read", "write"]}'),
    ('finance', 'Finance', '{"orders": ["read"], "customers": ["read"]}'),
    ('readonly', 'Read Only', '{}')
ON CONFLICT (name) DO NOTHING;
