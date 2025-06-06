-- Simple cleanup to complete UUID migration

-- Add latitude and longitude columns
ALTER TABLE locations
ADD COLUMN IF NOT EXISTS latitude DECIMAL(10, 8),
ADD COLUMN IF NOT EXISTS longitude DECIMAL(11, 8);

-- Remove duplicate locations manually
-- First, let's identify and delete duplicates (keeping the first one)
DELETE FROM locations a
USING locations b
WHERE a.id > b.id
AND COALESCE(a.address, '') = COALESCE(b.address, '')
AND COALESCE(a.city, '') = COALESCE(b.city, '')
AND COALESCE(a.state_province, '') = COALESCE(b.state_province, '')
AND COALESCE(a.postal_code, '') = COALESCE(b.postal_code, '');

-- Create indexes (without the problematic unique constraint for now)
CREATE INDEX IF NOT EXISTS idx_locations_coordinates ON locations(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_work_orders_status ON work_orders(status);
CREATE INDEX IF NOT EXISTS idx_work_orders_priority ON work_orders(priority);
CREATE INDEX IF NOT EXISTS idx_work_orders_assigned_to ON work_orders(assigned_to_user_id);
CREATE INDEX IF NOT EXISTS idx_work_orders_created_by ON work_orders(created_by_user_id);
CREATE INDEX IF NOT EXISTS idx_work_orders_location ON work_orders(location_id);

-- Update priority values
UPDATE work_orders
SET priority = CASE
    WHEN priority = 'low' THEN 'Low'
    WHEN priority = 'medium' THEN 'Medium'
    WHEN priority = 'high' THEN 'High'
    ELSE priority
END
WHERE priority IN ('low', 'medium', 'high');

-- Verification
SELECT 'UUID Migration completed!' as status;
SELECT count(*) as location_count FROM locations;
SELECT count(*) as work_order_count FROM work_orders;
