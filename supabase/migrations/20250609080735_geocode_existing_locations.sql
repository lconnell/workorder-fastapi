-- Add a trigger to ensure all locations have coordinates
-- This helps with the fallback for locations without coordinates

-- Create a function to notify when geocoding is needed
CREATE OR REPLACE FUNCTION notify_geocoding_needed()
RETURNS TRIGGER AS $$
BEGIN
  -- Only notify if coordinates are missing
  IF NEW.latitude IS NULL OR NEW.longitude IS NULL THEN
    -- Log for monitoring (you could also send to a queue)
    RAISE NOTICE 'Location % needs geocoding: %, %, %, %',
      NEW.id,
      NEW.address,
      NEW.city,
      NEW.state_province,
      NEW.postal_code;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for new locations
DROP TRIGGER IF EXISTS location_geocoding_check ON locations;
CREATE TRIGGER location_geocoding_check
  AFTER INSERT OR UPDATE ON locations
  FOR EACH ROW
  EXECUTE FUNCTION notify_geocoding_needed();

-- Add an index on coordinates to quickly find locations needing geocoding
CREATE INDEX IF NOT EXISTS idx_locations_missing_coordinates
ON locations(id)
WHERE latitude IS NULL OR longitude IS NULL;

-- Add a comment to document the geocoding process
COMMENT ON TABLE locations IS 'Stores location details for work orders. Each unique combination of address components represents a distinct location. Coordinates (latitude, longitude) are geocoded server-side when the location is created.';

-- Check current state
SELECT
  COUNT(*) as total_locations,
  COUNT(CASE WHEN latitude IS NOT NULL AND longitude IS NOT NULL THEN 1 END) as geocoded_locations,
  COUNT(CASE WHEN latitude IS NULL OR longitude IS NULL THEN 1 END) as missing_coordinates
FROM locations;
