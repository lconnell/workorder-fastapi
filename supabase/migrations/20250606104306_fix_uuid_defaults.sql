-- Fix UUID defaults for primary keys
-- Ensure all UUID primary key columns have proper default values

-- Enable UUID extension (should already be enabled but just in case)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Check column types first and only set defaults for UUID columns
DO $$
DECLARE
    locations_type TEXT;
    work_orders_type TEXT;
BEGIN
    -- Get column types
    SELECT data_type INTO locations_type
    FROM information_schema.columns
    WHERE table_name = 'locations' AND column_name = 'id';

    SELECT data_type INTO work_orders_type
    FROM information_schema.columns
    WHERE table_name = 'work_orders' AND column_name = 'id';

    RAISE NOTICE 'Column types found:';
    RAISE NOTICE '- locations.id type: %', locations_type;
    RAISE NOTICE '- work_orders.id type: %', work_orders_type;

    -- Only set UUID defaults if columns are actually UUID type
    IF locations_type = 'uuid' THEN
        EXECUTE 'ALTER TABLE locations ALTER COLUMN id SET DEFAULT uuid_generate_v4()';
        RAISE NOTICE 'Set UUID default for locations.id';
    ELSE
        RAISE NOTICE 'Skipping locations.id - not UUID type';
    END IF;

    IF work_orders_type = 'uuid' THEN
        EXECUTE 'ALTER TABLE work_orders ALTER COLUMN id SET DEFAULT uuid_generate_v4()';
        RAISE NOTICE 'Set UUID default for work_orders.id';
    ELSE
        RAISE NOTICE 'Skipping work_orders.id - not UUID type';
    END IF;
END $$;
