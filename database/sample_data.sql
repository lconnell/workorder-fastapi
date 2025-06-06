-- Insert sample locations
INSERT INTO locations (id, address, city, state_province, postal_code, country, latitude, longitude) VALUES
('550e8400-e29b-41d4-a716-446655440001', '123 Main Street', 'New York', 'NY', '10001', 'USA', 40.7128, -74.0060),
('550e8400-e29b-41d4-a716-446655440002', '456 Oak Avenue', 'Los Angeles', 'CA', '90210', 'USA', 34.0522, -118.2437),
('550e8400-e29b-41d4-a716-446655440003', '789 Pine Road', 'Chicago', 'IL', '60601', 'USA', 41.8781, -87.6298)
ON CONFLICT (id) DO NOTHING;

-- Note: You'll need to replace the UUIDs below with actual user IDs from your auth.users table
-- For now, these are placeholder UUIDs that you should update after creating users

-- Insert sample work orders
-- Replace 'YOUR_USER_ID_HERE' with actual user IDs from auth.users table
INSERT INTO work_orders (
    id,
    title,
    description,
    status,
    priority,
    location_id,
    created_by_user_id
) VALUES
(
    '660e8400-e29b-41d4-a716-446655440001',
    'Fix leaky faucet',
    'Kitchen faucet is dripping and needs repair',
    'Open',
    'medium',
    '550e8400-e29b-41d4-a716-446655440001',
    auth.uid() -- This will use the current user's ID
),
(
    '660e8400-e29b-41d4-a716-446655440002',
    'Replace broken window',
    'Living room window has a crack and needs replacement',
    'In Progress',
    'high',
    '550e8400-e29b-41d4-a716-446655440002',
    auth.uid() -- This will use the current user's ID
),
(
    '660e8400-e29b-41d4-a716-446655440003',
    'Unclog drain',
    'Bathroom sink drain is slow and needs cleaning',
    'Open',
    'low',
    '550e8400-e29b-41d4-a716-446655440003',
    auth.uid() -- This will use the current user's ID
)
ON CONFLICT (id) DO NOTHING;
