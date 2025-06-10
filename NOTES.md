# Work Orders & Locations Architecture

## Map Implementation (MapLibre GL JS with Protomaps)
- **Replaced Leaflet with MapLibre GL JS** for better performance
- **Using Protomaps** free tier for vector tiles (no API key needed)
- **Server-side geocoding only** - no client-side geocoding delays
- **WebGL rendering** for smooth map interactions
- **Instant map loading** - uses pre-geocoded coordinates from database

## Database Relationship
- **work_orders** table has `location_id` (UUID, nullable) that references `locations.id`
- **locations** table stores unique address combinations with geocoding data
- Foreign key constraint ensures referential integrity
- **Automatic cleanup**: Locations have a `reference_count` that tracks usage
  - When a work order is deleted, the count decrements
  - When count reaches 0, the location is automatically deleted
  - Prevents orphaned locations from accumulating

## Location Management

### Duplicate Prevention
- Before creating a new location, the system checks if one already exists with the same:
  - Street address
  - City
  - State/Province
- If found, returns the existing location instead of creating a duplicate
- Database has a unique index on the combination of address fields

### Location Fields
- **No name field** - Removed as it was redundant with address
- Address components: address, city, state_province, postal_code, country
- Geocoding cache: latitude, longitude (auto-populated via OpenStreetMap)

### How It Works
1. **New Work Order**: If address fields provided → Create location → Link via location_id
2. **Edit Work Order**:
   - If location data changed → Create new location → Update location_id
   - If location unchanged → Keep existing location_id
3. **View Work Order**: Join with locations table to display full address

### Benefits
- Normalized data - addresses stored once, referenced many times
- Geocoding efficiency - cache lat/lng to avoid repeated API calls
- Data integrity - can't have orphaned addresses
- Future flexibility - easy to add location-based features (maps, routing, etc.)

## Debug System
- Environment variables: `DEBUG=true` (backend), `VITE_DEBUG=true` (frontend)
- Debug utilities in both backend and frontend for conditional logging
- Helps trace issues like the 500 error we fixed with location creation


* active work order displayed message on map view
* use lighter borders for inputs. see image
* consolidate, cleanup notes/docs (architeture?)
* create non-expiring jwt for llm usage
* atlas project management
* claude PRD's (Project Requirements Document)
