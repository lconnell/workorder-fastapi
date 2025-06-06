-- Minimal final migration - just add missing columns and indexes

-- Add latitude and longitude columns for geocoding cache
ALTER TABLE locations
ADD COLUMN IF NOT EXISTS latitude DECIMAL(10, 8),
ADD COLUMN IF NOT EXISTS longitude DECIMAL(11, 8);

-- Create performance indexes
CREATE INDEX IF NOT EXISTS idx_locations_coordinates ON locations(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_work_orders_status ON work_orders(status);
CREATE INDEX IF NOT EXISTS idx_work_orders_priority ON work_orders(priority);
CREATE INDEX IF NOT EXISTS idx_work_orders_assigned_to ON work_orders(assigned_to_user_id);
CREATE INDEX IF NOT EXISTS idx_work_orders_created_by ON work_orders(created_by_user_id);
CREATE INDEX IF NOT EXISTS idx_work_orders_location ON work_orders(location_id);

-- Success message
SELECT 'UUID Migration and enhancements completed successfully!' as status;
