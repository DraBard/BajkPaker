# Database User Configuration

## User Types

Our MySQL database container uses two distinct users:

1. **Regular User (`bajkpaker`)**
   - Password set via `DB_PASSWORD`
   - Limited permissions to specific database
   - Used by the application for normal operations
   - Connection string: `mysql+asyncmy://bajkpaker:${DB_PASSWORD}@db/bajkpaker_dev`

2. **Root User (`root`)**
   - Password set via `DB_ROOT_PASSWORD`
   - Full administrative access
   - Used for maintenance, migrations, and healthchecks
   - Not meant for application connections

## Security Best Practices

- Use different strong passwords for each user
- The application should connect as the regular user, not root
- Root access should be limited to administrative tasks only

## Environment Configuration

Both passwords are defined in the `.env` file and passed to the database container through Docker Compose:

```
DB_USER=bajkpaker
DB_PASSWORD=user_password_here
DB_ROOT_PASSWORD=root_password_here
```
