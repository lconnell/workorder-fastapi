-- Remove the redundant name field from locations table
-- The name field serves no real purpose and just duplicates the address

-- Step 1: Drop the NOT NULL constraint first (if it exists)
ALTER TABLE locations
ALTER COLUMN name DROP NOT NULL;

-- Step 2: Drop the name column
ALTER TABLE locations
DROP COLUMN IF EXISTS name;

-- Step 3: Update the unique index to ensure we don't create duplicate locations
-- Drop the existing index first
DROP INDEX IF EXISTS idx_locations_unique_address;

-- Create a new unique index that prevents duplicate locations
-- This ensures we can't have two locations with the exact same address components
CREATE UNIQUE INDEX idx_locations_unique_full_address ON locations(
    COALESCE(address, ''),
    COALESCE(city, ''),
    COALESCE(state_province, ''),
    COALESCE(postal_code, ''),
    COALESCE(country, '')
) WHERE address IS NOT NULL OR city IS NOT NULL OR state_province IS NOT NULL OR postal_code IS NOT NULL;

-- Add a comment to explain the table structure
COMMENT ON TABLE locations IS 'Stores location details for work orders. Each unique combination of address components represents a distinct location.';
