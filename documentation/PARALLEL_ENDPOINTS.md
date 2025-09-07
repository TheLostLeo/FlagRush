# Parallel Endpoints Architecture

The FlagRush CTF platform implements a dual-endpoint architecture for enhanced security and separation of concerns.

## Endpoint Overview

### Main API (Port 5000)
- **Purpose**: Serves regular CTF participants
- **Access**: All authenticated users
- **Base URL**: `http://your-server:5000`
- **Features**:
  - Challenge viewing
  - Flag submission
  - Leaderboard access
  - User profile management

### Admin API (Port 5001)
- **Purpose**: Administrative operations
- **Access**: Admin users only
- **Base URL**: `http://your-server:5001`
- **Features**:
  - Challenge management (CRUD)
  - User management
  - Submission monitoring
  - System configuration
  - Advanced analytics
  - System logs

#### Admin-Only Endpoints

1. **Dashboard**
   - `GET /api/admin/dashboard`
   - System-wide statistics and recent activity

2. **User Management**
   - `GET /api/admin/users` - List all users
   - `PUT /api/admin/users/<user_id>` - Update user
   - `DELETE /api/admin/users/<user_id>` - Delete user

3. **System Statistics**
   - `GET /api/admin/system/stats` - Detailed system statistics
   - Challenge performance metrics
   - Category analysis
   
4. **System Logs**
   - `GET /api/admin/system/logs` - Recent system events
   - Activity monitoring
   - Security audit trail

## Security Implementation

### Port-Level Separation
- Physical separation of admin and user traffic
- Different ports for different security contexts
- Reduced attack surface for administrative functions

### Authentication Flow
1. Users authenticate through either endpoint
2. JWT tokens issued contain role information
3. Middleware validates token and port combination
4. Requests are filtered based on user role and target port

### Access Control
```python
# Example middleware protection
@route_middleware()
def admin_function():
    # Only accessible on admin port (5001)
    # Only accessible to admin users
    pass
```

## Load Balancing Considerations

### Independent Scaling
- Each endpoint can be scaled independently
- Admin interface can have different resource allocations
- Main API can handle higher traffic volumes

### Performance Monitoring
- Separate monitoring for admin vs user traffic
- Independent rate limiting per endpoint
- Isolated error tracking and logging

## Configuration

### Environment Variables
```bash
# Main API Configuration
PORT=5000                 # Main user interface port
ADMIN_PORT=5001          # Administrative interface port
DEBUG=False              # Production debug setting
```

### Networking Setup
1. Configure firewall rules for both ports
2. Set up SSL/TLS certificates for both endpoints
3. Consider separate domain names for admin interface

## Best Practices

### Development
- Use different `.env` configurations for dev/prod
- Test both endpoints independently
- Monitor resource usage per endpoint

### Production
- Implement rate limiting per endpoint
- Set up monitoring for both ports
- Use SSL/TLS for both endpoints
- Consider IP whitelisting for admin port

