-- Add reference counting to locations table for automatic cleanup of orphaned locations
-- This migration adds a reference_count column and triggers to maintain it automatically

-- Step 1: Add reference_count column to locations table
ALTER TABLE locations
ADD COLUMN reference_count INTEGER DEFAULT 0 NOT NULL;

-- Step 2: Update existing location counts based on current work orders
UPDATE locations
SET reference_count = (
  SELECT COUNT(*)
  FROM work_orders
  WHERE work_orders.location_id = locations.id
);

-- Step 3: Create function to maintain location reference counts
CREATE OR REPLACE FUNCTION update_location_reference_count()
RETURNS TRIGGER AS $$
DECLARE
  v_old_location_id UUID;
  v_new_location_id UUID;
BEGIN
  -- Set variables for clarity
  v_old_location_id := CASE WHEN TG_OP = 'UPDATE' OR TG_OP = 'DELETE' THEN OLD.location_id ELSE NULL END;
  v_new_location_id := CASE WHEN TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN NEW.location_id ELSE NULL END;

  -- Handle INSERT: increment count for new location
  IF TG_OP = 'INSERT' AND v_new_location_id IS NOT NULL THEN
    UPDATE locations
    SET reference_count = reference_count + 1
    WHERE id = v_new_location_id;

    RAISE NOTICE 'Location % reference count incremented on INSERT', v_new_location_id;
  END IF;

  -- Handle UPDATE: update counts when location changes
  IF TG_OP = 'UPDATE' AND v_old_location_id IS DISTINCT FROM v_new_location_id THEN
    -- Decrement old location count
    IF v_old_location_id IS NOT NULL THEN
      UPDATE locations
      SET reference_count = reference_count - 1
      WHERE id = v_old_location_id;

      -- Delete old location if no longer referenced
      DELETE FROM locations
      WHERE id = v_old_location_id
        AND reference_count = 0;

      RAISE NOTICE 'Location % reference count decremented on UPDATE', v_old_location_id;
    END IF;

    -- Increment new location count
    IF v_new_location_id IS NOT NULL THEN
      UPDATE locations
      SET reference_count = reference_count + 1
      WHERE id = v_new_location_id;

      RAISE NOTICE 'Location % reference count incremented on UPDATE', v_new_location_id;
    END IF;
  END IF;

  -- Handle DELETE: decrement count and remove if orphaned
  IF TG_OP = 'DELETE' AND v_old_location_id IS NOT NULL THEN
    UPDATE locations
    SET reference_count = reference_count - 1
    WHERE id = v_old_location_id;

    -- Delete location if no longer referenced
    DELETE FROM locations
    WHERE id = v_old_location_id
      AND reference_count = 0;

    RAISE NOTICE 'Location % reference count decremented on DELETE', v_old_location_id;
  END IF;

  -- Return appropriate value
  RETURN CASE
    WHEN TG_OP = 'DELETE' THEN OLD
    ELSE NEW
  END;
END;
$$ LANGUAGE plpgsql;

-- Step 4: Create trigger to maintain reference counts
DROP TRIGGER IF EXISTS maintain_location_reference_count ON work_orders;
CREATE TRIGGER maintain_location_reference_count
AFTER INSERT OR UPDATE OR DELETE ON work_orders
FOR EACH ROW
EXECUTE FUNCTION update_location_reference_count();

-- Step 5: Add constraint to ensure reference_count never goes negative
ALTER TABLE locations
ADD CONSTRAINT positive_reference_count
CHECK (reference_count >= 0);

-- Step 6: Add index for performance when finding orphaned locations
CREATE INDEX idx_locations_reference_count
ON locations(reference_count)
WHERE reference_count = 0;

-- Step 7: Add comment to document the reference counting system
COMMENT ON COLUMN locations.reference_count IS
'Number of work orders currently referencing this location. Maintained automatically by triggers. Location is deleted when count reaches 0.';

-- Step 8: Verify the migration
DO $$
DECLARE
  v_total_locations INTEGER;
  v_referenced_locations INTEGER;
  v_orphaned_locations INTEGER;
BEGIN
  -- Count locations
  SELECT COUNT(*) INTO v_total_locations FROM locations;

  -- Count referenced locations
  SELECT COUNT(*) INTO v_referenced_locations
  FROM locations
  WHERE reference_count > 0;

  -- Count orphaned locations (should be 0 after migration)
  SELECT COUNT(*) INTO v_orphaned_locations
  FROM locations
  WHERE reference_count = 0;

  RAISE NOTICE 'Migration Summary:';
  RAISE NOTICE '- Total locations: %', v_total_locations;
  RAISE NOTICE '- Referenced locations: %', v_referenced_locations;
  RAISE NOTICE '- Orphaned locations: %', v_orphaned_locations;
  RAISE NOTICE '';
  RAISE NOTICE 'Reference counting system is now active.';
  RAISE NOTICE 'Orphaned locations will be automatically deleted when work orders are removed.';
END $$;

-- Step 9: Clean up any existing orphaned locations (optional)
-- Uncomment the following lines if you want to remove orphaned locations immediately
-- DELETE FROM locations WHERE reference_count = 0;
-- RAISE NOTICE 'Cleaned up % orphaned locations', FOUND;
