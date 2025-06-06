-- Fix UUID migration - complete the conversion that was partially applied
-- This handles the case where the previous migration partially succeeded

-- Step 1: Check if we need to complete the UUID conversion for locations
DO $$
BEGIN
    -- Check if locations table still has integer ID
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'locations'
        AND column_name = 'id'
        AND data_type = 'integer'
    ) THEN
        -- Complete locations table conversion
        ALTER TABLE locations DROP COLUMN id CASCADE;
        ALTER TABLE locations RENAME COLUMN temp_uuid TO id;
        ALTER TABLE locations ADD PRIMARY KEY (id);
    END IF;
END $$;

-- Step 2: Check if we need to complete the UUID conversion for work_orders
DO $$
BEGIN
    -- Check if work_orders table still has integer ID
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'work_orders'
        AND column_name = 'id'
        AND data_type = 'integer'
    ) THEN
        -- Complete work_orders table conversion
        ALTER TABLE work_orders DROP COLUMN location_id;
        ALTER TABLE work_orders DROP COLUMN id CASCADE;
        ALTER TABLE work_orders RENAME COLUMN temp_uuid TO id;
        ALTER TABLE work_orders RENAME COLUMN temp_location_id TO location_id;
        ALTER TABLE work_orders ADD PRIMARY KEY (id);
    END IF;
END $$;

-- Step 3: Ensure foreign key constraints exist
ALTER TABLE work_orders
ADD CONSTRAINT work_orders_location_id_fkey
FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL;

-- Step 4: Recreate indexes for performance (with IF NOT EXISTS)
CREATE INDEX IF NOT EXISTS idx_work_orders_status ON work_orders(status);
CREATE INDEX IF NOT EXISTS idx_work_orders_priority ON work_orders(priority);
CREATE INDEX IF NOT EXISTS idx_work_orders_assigned_to ON work_orders(assigned_to_user_id);
CREATE INDEX IF NOT EXISTS idx_work_orders_created_by ON work_orders(created_by_user_id);
CREATE INDEX IF NOT EXISTS idx_work_orders_location ON work_orders(location_id);

-- Step 5: Create indexes for locations (with IF NOT EXISTS)
CREATE INDEX IF NOT EXISTS idx_locations_coordinates ON locations(latitude, longitude);
CREATE UNIQUE INDEX IF NOT EXISTS idx_locations_unique_address ON locations(
    COALESCE(address, ''),
    COALESCE(city, ''),
    COALESCE(state_province, ''),
    COALESCE(postal_code, '')
) WHERE address IS NOT NULL OR city IS NOT NULL OR state_province IS NOT NULL OR postal_code IS NOT NULL;

-- Step 6: Update priority values to match new enum (if not already done)
UPDATE work_orders
SET priority = CASE
    WHEN priority = 'low' THEN 'Low'
    WHEN priority = 'medium' THEN 'Medium'
    WHEN priority = 'high' THEN 'High'
    ELSE priority
END
WHERE priority IN ('low', 'medium', 'high');

-- Verify the final state
SELECT 'Locations migrated:' as status, count(*) as count FROM locations;
SELECT 'Work orders migrated:' as status, count(*) as count FROM work_orders;
SELECT 'Work orders with locations:' as status, count(*) as count FROM work_orders WHERE location_id IS NOT NULL;
