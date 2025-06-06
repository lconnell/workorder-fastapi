-- Final cleanup - remove duplicates and complete setup

-- First, add latitude and longitude columns
ALTER TABLE locations
ADD COLUMN IF NOT EXISTS latitude DECIMAL(10, 8),
ADD COLUMN IF NOT EXISTS longitude DECIMAL(11, 8);

-- Clean up duplicate locations by merging them
-- Keep the oldest location and update work_orders to reference it
WITH duplicate_locations AS (
    SELECT
        address, city, state_province, postal_code,
        array_agg(id ORDER BY created_at) as location_ids,
        min(id) as keep_id
    FROM locations
    WHERE address IS NOT NULL OR city IS NOT NULL OR state_province IS NOT NULL OR postal_code IS NOT NULL
    GROUP BY COALESCE(address, ''), COALESCE(city, ''), COALESCE(state_province, ''), COALESCE(postal_code, '')
    HAVING count(*) > 1
),
updates AS (
    UPDATE work_orders
    SET location_id = dl.keep_id
    FROM duplicate_locations dl
    WHERE location_id = ANY(dl.location_ids[2:])
    RETURNING work_orders.location_id, dl.keep_id
)
DELETE FROM locations
WHERE id IN (
    SELECT unnest(location_ids[2:])
    FROM duplicate_locations
);

-- Now create the unique index
CREATE UNIQUE INDEX IF NOT EXISTS idx_locations_unique_address ON locations(
    COALESCE(address, ''),
    COALESCE(city, ''),
    COALESCE(state_province, ''),
    COALESCE(postal_code, '')
) WHERE address IS NOT NULL OR city IS NOT NULL OR state_province IS NOT NULL OR postal_code IS NOT NULL;

-- Create other indexes
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

-- Final verification
SELECT 'UUID Migration completed successfully!' as status;
SELECT 'Total locations:' as info, count(*) as count FROM locations;
SELECT 'Total work orders:' as info, count(*) as count FROM work_orders;
SELECT 'Work orders with locations:' as info, count(*) as count FROM work_orders WHERE location_id IS NOT NULL;
