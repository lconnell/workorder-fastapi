-- Complete UUID setup and add missing features
-- This migration adds latitude/longitude columns and ensures all indexes exist

-- Add latitude and longitude columns to locations table if they don't exist
ALTER TABLE locations
ADD COLUMN IF NOT EXISTS latitude DECIMAL(10, 8),
ADD COLUMN IF NOT EXISTS longitude DECIMAL(11, 8);

-- Ensure all necessary indexes exist (with IF NOT EXISTS)
CREATE INDEX IF NOT EXISTS idx_work_orders_status ON work_orders(status);
CREATE INDEX IF NOT EXISTS idx_work_orders_priority ON work_orders(priority);
CREATE INDEX IF NOT EXISTS idx_work_orders_assigned_to ON work_orders(assigned_to_user_id);
CREATE INDEX IF NOT EXISTS idx_work_orders_created_by ON work_orders(created_by_user_id);
CREATE INDEX IF NOT EXISTS idx_work_orders_location ON work_orders(location_id);

-- Create indexes for locations
CREATE INDEX IF NOT EXISTS idx_locations_coordinates ON locations(latitude, longitude);

-- Create unique index for duplicate prevention (only if columns have values)
CREATE UNIQUE INDEX IF NOT EXISTS idx_locations_unique_address ON locations(
    COALESCE(address, ''),
    COALESCE(city, ''),
    COALESCE(state_province, ''),
    COALESCE(postal_code, '')
) WHERE address IS NOT NULL OR city IS NOT NULL OR state_province IS NOT NULL OR postal_code IS NOT NULL;

-- Update priority values to match new enum (if not already done)
UPDATE work_orders
SET priority = CASE
    WHEN priority = 'low' THEN 'Low'
    WHEN priority = 'medium' THEN 'Medium'
    WHEN priority = 'high' THEN 'High'
    ELSE priority
END
WHERE priority IN ('low', 'medium', 'high');

-- Verify the final state
SELECT 'Migration completed successfully' as status;
