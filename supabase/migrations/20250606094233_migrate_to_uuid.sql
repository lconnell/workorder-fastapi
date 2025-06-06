-- Migration script to convert from integer IDs to UUIDs
-- This script will:
-- 1. Add name field to locations table
-- 2. Convert integer IDs to UUIDs
-- 3. Update foreign key references
-- 4. Add geocoding cache columns

-- Step 1: Add new columns to locations table
ALTER TABLE locations
ADD COLUMN IF NOT EXISTS name TEXT,
ADD COLUMN IF NOT EXISTS temp_uuid UUID DEFAULT gen_random_uuid();

-- Step 2: Populate name field for existing locations
UPDATE locations
SET name = COALESCE(
    CASE
        WHEN address IS NOT NULL THEN address
        ELSE 'Location ' || id::text
    END
)
WHERE name IS NULL;

-- Step 3: Make name NOT NULL after populating
ALTER TABLE locations
ALTER COLUMN name SET NOT NULL;

-- Step 4: Make address fields optional (remove NOT NULL constraints)
ALTER TABLE locations
ALTER COLUMN address DROP NOT NULL,
ALTER COLUMN city DROP NOT NULL,
ALTER COLUMN state_province DROP NOT NULL,
ALTER COLUMN postal_code DROP NOT NULL;

-- Step 5: Add new columns to work_orders table
ALTER TABLE work_orders
ADD COLUMN IF NOT EXISTS temp_uuid UUID DEFAULT gen_random_uuid(),
ADD COLUMN IF NOT EXISTS temp_location_id UUID;

-- Step 6: Create mapping between old integer IDs and new UUIDs for locations
UPDATE work_orders
SET temp_location_id = (
    SELECT temp_uuid
    FROM locations
    WHERE locations.id = work_orders.location_id
)
WHERE location_id IS NOT NULL;

-- Step 7: Drop old constraints and indexes
DROP INDEX IF EXISTS idx_work_orders_location;
ALTER TABLE work_orders DROP CONSTRAINT IF EXISTS work_orders_location_id_fkey;

-- Step 8: Replace old ID columns with new UUID columns

-- For locations table
ALTER TABLE locations DROP COLUMN id CASCADE;
ALTER TABLE locations RENAME COLUMN temp_uuid TO id;
ALTER TABLE locations ADD PRIMARY KEY (id);

-- For work_orders table
ALTER TABLE work_orders DROP COLUMN location_id;
ALTER TABLE work_orders DROP COLUMN id CASCADE;
ALTER TABLE work_orders RENAME COLUMN temp_uuid TO id;
ALTER TABLE work_orders RENAME COLUMN temp_location_id TO location_id;
ALTER TABLE work_orders ADD PRIMARY KEY (id);

-- Step 9: Recreate foreign key constraints
ALTER TABLE work_orders
ADD CONSTRAINT work_orders_location_id_fkey
FOREIGN KEY (location_id) REFERENCES locations(id);

-- Step 10: Recreate indexes for performance
CREATE INDEX IF NOT EXISTS idx_work_orders_status ON work_orders(status);
CREATE INDEX IF NOT EXISTS idx_work_orders_priority ON work_orders(priority);
CREATE INDEX IF NOT EXISTS idx_work_orders_assigned_to ON work_orders(assigned_to_user_id);
CREATE INDEX IF NOT EXISTS idx_work_orders_created_by ON work_orders(created_by_user_id);
CREATE INDEX IF NOT EXISTS idx_work_orders_location ON work_orders(location_id);

-- Step 11: Create indexes for locations
CREATE INDEX IF NOT EXISTS idx_locations_coordinates ON locations(latitude, longitude);
CREATE UNIQUE INDEX IF NOT EXISTS idx_locations_unique_address ON locations(
    COALESCE(address, ''),
    COALESCE(city, ''),
    COALESCE(state_province, ''),
    COALESCE(postal_code, '')
) WHERE address IS NOT NULL OR city IS NOT NULL OR state_province IS NOT NULL OR postal_code IS NOT NULL;

-- Step 12: Update priority values to match new enum
UPDATE work_orders
SET priority = CASE
    WHEN priority = 'low' THEN 'Low'
    WHEN priority = 'medium' THEN 'Medium'
    WHEN priority = 'high' THEN 'High'
    ELSE priority
END;

-- Verify the migration
SELECT 'Locations migrated:' as status, count(*) as count FROM locations;
SELECT 'Work orders migrated:' as status, count(*) as count FROM work_orders;
SELECT 'Work orders with locations:' as status, count(*) as count FROM work_orders WHERE location_id IS NOT NULL;
