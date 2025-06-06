-- Restore sample data if tables are empty

-- Check if we need to add sample data
DO $$
DECLARE
    location_count INTEGER;
    work_order_count INTEGER;
    sample_location_id UUID;
BEGIN
    -- Count existing data
    SELECT COUNT(*) INTO location_count FROM locations;
    SELECT COUNT(*) INTO work_order_count FROM work_orders;

    -- Only add sample data if tables are empty
    IF location_count = 0 THEN
        -- Insert sample locations
        INSERT INTO locations (id, name, address, city, state_province, postal_code, country)
        VALUES
            (gen_random_uuid(), '316 E. Washington St', '316 E. Washington St', 'Hagerstown', 'MD', '21740', 'USA'),
            (gen_random_uuid(), '11374 Cross Fields Dr', '11374 Cross Fields Dr', 'Waynesboro', 'PA', '17268', 'USA'),
            (gen_random_uuid(), 'Downtown Office', '123 Main St', 'Frederick', 'MD', '21701', 'USA');

        RAISE NOTICE 'Added sample locations';
    END IF;

    IF work_order_count = 0 THEN
        -- Get a sample location ID
        SELECT id INTO sample_location_id FROM locations LIMIT 1;

        -- Insert sample work orders
        INSERT INTO work_orders (id, title, description, status, priority, location_id, created_by_user_id)
        VALUES
            (gen_random_uuid(), 'Fix HVAC System', 'Air conditioning unit not working properly', 'Open', 'High', sample_location_id, gen_random_uuid()),
            (gen_random_uuid(), 'Replace Broken Window', 'Window in conference room is cracked', 'In Progress', 'Medium', sample_location_id, gen_random_uuid()),
            (gen_random_uuid(), 'Water Leak Investigation', 'Investigate source of water leak in basement', 'On Hold', 'Low', sample_location_id, gen_random_uuid());

        RAISE NOTICE 'Added sample work orders';
    END IF;

    -- Show final counts
    RAISE NOTICE 'Final counts - Locations: %, Work Orders: %',
        (SELECT COUNT(*) FROM locations),
        (SELECT COUNT(*) FROM work_orders);
END $$;
