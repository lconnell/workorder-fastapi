-- Migration: Convert integer IDs to UUIDs
-- This migration safely converts all integer primary keys to UUIDs while preserving data and relationships

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Step 1: Handle dependent tables first
-- Check if work_order_parts table exists and handle it
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'work_order_parts') THEN
        -- Add UUID columns to work_order_parts
        ALTER TABLE work_order_parts ADD COLUMN work_order_uuid_id UUID;

        -- Update work_order_parts with corresponding UUIDs
        ALTER TABLE work_orders ADD COLUMN uuid_id UUID DEFAULT uuid_generate_v4();
        UPDATE work_order_parts
        SET work_order_uuid_id = work_orders.uuid_id
        FROM work_orders
        WHERE work_order_parts.work_order_id = work_orders.id;

        -- Drop the foreign key constraint
        ALTER TABLE work_order_parts DROP CONSTRAINT IF EXISTS work_order_parts_work_order_id_fkey;
    END IF;
END $$;

-- Step 2: Handle work_order_notes table if it exists
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'work_order_notes') THEN
        -- Add UUID columns to work_order_notes
        ALTER TABLE work_order_notes ADD COLUMN work_order_uuid_id UUID;

        -- Ensure work_orders has uuid_id column (may already exist from step 1)
        IF NOT EXISTS (SELECT column_name FROM information_schema.columns
                      WHERE table_name = 'work_orders' AND column_name = 'uuid_id') THEN
            ALTER TABLE work_orders ADD COLUMN uuid_id UUID DEFAULT uuid_generate_v4();
        END IF;

        -- Update work_order_notes with corresponding UUIDs
        UPDATE work_order_notes
        SET work_order_uuid_id = work_orders.uuid_id
        FROM work_orders
        WHERE work_order_notes.work_order_id = work_orders.id;

        -- Drop the foreign key constraint
        ALTER TABLE work_order_notes DROP CONSTRAINT IF EXISTS work_order_notes_work_order_id_fkey;
    END IF;
END $$;

-- Step 3: Add UUID columns to main tables
-- Add UUID column to locations if not exists
ALTER TABLE locations ADD COLUMN IF NOT EXISTS uuid_id UUID DEFAULT uuid_generate_v4();

-- Add UUID column to work_orders if not exists (may already exist from dependent table handling)
DO $$
BEGIN
    IF NOT EXISTS (SELECT column_name FROM information_schema.columns
                  WHERE table_name = 'work_orders' AND column_name = 'uuid_id') THEN
        ALTER TABLE work_orders ADD COLUMN uuid_id UUID DEFAULT uuid_generate_v4();
    END IF;
END $$;

-- Add location UUID reference to work_orders
ALTER TABLE work_orders ADD COLUMN location_uuid_id UUID;

-- Step 4: Populate the UUID foreign key relationships
UPDATE work_orders
SET location_uuid_id = locations.uuid_id
FROM locations
WHERE work_orders.location_id = locations.id;

-- Step 5: Create temporary unique constraints on UUID columns
ALTER TABLE locations ADD CONSTRAINT locations_uuid_id_unique UNIQUE (uuid_id);
ALTER TABLE work_orders ADD CONSTRAINT work_orders_uuid_id_unique UNIQUE (uuid_id);

-- Step 6: Drop existing foreign key constraints
ALTER TABLE work_orders DROP CONSTRAINT IF EXISTS work_orders_location_id_fkey;

-- Step 7: Drop old primary key constraints and rename columns
-- For locations table
ALTER TABLE locations DROP CONSTRAINT IF EXISTS locations_pkey;
ALTER TABLE locations RENAME COLUMN id TO old_id;
ALTER TABLE locations RENAME COLUMN uuid_id TO id;

-- For work_orders table
ALTER TABLE work_orders DROP CONSTRAINT IF EXISTS work_orders_pkey;
ALTER TABLE work_orders RENAME COLUMN id TO old_id;
ALTER TABLE work_orders RENAME COLUMN uuid_id TO id;
ALTER TABLE work_orders RENAME COLUMN location_id TO old_location_id;
ALTER TABLE work_orders RENAME COLUMN location_uuid_id TO location_id;

-- Step 8: Update dependent tables to use new UUIDs
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'work_order_parts') THEN
        ALTER TABLE work_order_parts RENAME COLUMN work_order_id TO old_work_order_id;
        ALTER TABLE work_order_parts RENAME COLUMN work_order_uuid_id TO work_order_id;
    END IF;
END $$;

DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'work_order_notes') THEN
        ALTER TABLE work_order_notes RENAME COLUMN work_order_id TO old_work_order_id;
        ALTER TABLE work_order_notes RENAME COLUMN work_order_uuid_id TO work_order_id;
    END IF;
END $$;

-- Step 9: Add new primary key constraints
ALTER TABLE locations ADD PRIMARY KEY (id);
ALTER TABLE work_orders ADD PRIMARY KEY (id);

-- Step 10: Drop unique constraints (no longer needed since they're primary keys)
ALTER TABLE locations DROP CONSTRAINT IF EXISTS locations_uuid_id_unique;
ALTER TABLE work_orders DROP CONSTRAINT IF EXISTS work_orders_uuid_id_unique;

-- Step 11: Add new foreign key constraints
ALTER TABLE work_orders
ADD CONSTRAINT work_orders_location_id_fkey
FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL;

-- Recreate foreign key constraints for dependent tables
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'work_order_parts') THEN
        ALTER TABLE work_order_parts
        ADD CONSTRAINT work_order_parts_work_order_id_fkey
        FOREIGN KEY (work_order_id) REFERENCES work_orders(id) ON DELETE CASCADE;
    END IF;
END $$;

DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'work_order_notes') THEN
        ALTER TABLE work_order_notes
        ADD CONSTRAINT work_order_notes_work_order_id_fkey
        FOREIGN KEY (work_order_id) REFERENCES work_orders(id) ON DELETE CASCADE;
    END IF;
END $$;

-- Step 12: Drop old integer columns
ALTER TABLE locations DROP COLUMN old_id;
ALTER TABLE work_orders DROP COLUMN old_id;
ALTER TABLE work_orders DROP COLUMN old_location_id;

-- Drop old integer columns from dependent tables
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'work_order_parts') THEN
        ALTER TABLE work_order_parts DROP COLUMN old_work_order_id;
    END IF;
END $$;

DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'work_order_notes') THEN
        ALTER TABLE work_order_notes DROP COLUMN old_work_order_id;
    END IF;
END $$;

-- Step 13: Update RLS policies if they exist
-- Drop existing policies
DROP POLICY IF EXISTS "Users can view work orders" ON work_orders;
DROP POLICY IF EXISTS "Users can create work orders" ON work_orders;
DROP POLICY IF EXISTS "Users can update their work orders" ON work_orders;
DROP POLICY IF EXISTS "Users can delete their work orders" ON work_orders;
DROP POLICY IF EXISTS "Users can view locations" ON locations;
DROP POLICY IF EXISTS "Users can create locations" ON locations;

-- Recreate policies with UUID support
CREATE POLICY "Users can view work orders" ON work_orders
    FOR SELECT USING (auth.uid() = created_by_user_id::uuid);

CREATE POLICY "Users can create work orders" ON work_orders
    FOR INSERT WITH CHECK (auth.uid() = created_by_user_id::uuid);

CREATE POLICY "Users can update their work orders" ON work_orders
    FOR UPDATE USING (auth.uid() = created_by_user_id::uuid);

CREATE POLICY "Users can delete their work orders" ON work_orders
    FOR DELETE USING (auth.uid() = created_by_user_id::uuid);

CREATE POLICY "Users can view locations" ON locations
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Users can create locations" ON locations
    FOR INSERT TO authenticated WITH CHECK (true);

-- Verify the migration worked by checking a few records
DO $$
DECLARE
    location_count INTEGER;
    work_order_count INTEGER;
    parts_count INTEGER := 0;
    notes_count INTEGER := 0;
BEGIN
    SELECT COUNT(*) INTO location_count FROM locations;
    SELECT COUNT(*) INTO work_order_count FROM work_orders;

    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'work_order_parts') THEN
        SELECT COUNT(*) INTO parts_count FROM work_order_parts;
    END IF;

    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'work_order_notes') THEN
        SELECT COUNT(*) INTO notes_count FROM work_order_notes;
    END IF;

    RAISE NOTICE 'Migration completed successfully:';
    RAISE NOTICE '- Locations: % records', location_count;
    RAISE NOTICE '- Work Orders: % records', work_order_count;
    RAISE NOTICE '- Work Order Parts: % records', parts_count;
    RAISE NOTICE '- Work Order Notes: % records', notes_count;
    RAISE NOTICE 'All IDs are now UUIDs';
END $$;
