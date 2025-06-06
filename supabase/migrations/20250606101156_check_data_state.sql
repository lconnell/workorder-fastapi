-- Check current data state and verify UUID conversion

-- Check table structure
SELECT 'Locations table structure:' as info;
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'locations'
ORDER BY ordinal_position;

SELECT 'Work orders table structure:' as info;
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'work_orders'
ORDER BY ordinal_position;

-- Check data counts
SELECT 'Data counts:' as info;
SELECT 'locations' as table_name, count(*) as row_count FROM locations
UNION ALL
SELECT 'work_orders' as table_name, count(*) as row_count FROM work_orders;

-- Check sample data
SELECT 'Sample location data:' as info;
SELECT id, name, address, city FROM locations LIMIT 3;

SELECT 'Sample work order data:' as info;
SELECT id, title, status, priority, location_id FROM work_orders LIMIT 3;
