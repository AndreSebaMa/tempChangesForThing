# Djanbee

A free command-line tool to simplify Django project deployment in production environments.

## Overview

Djanbee automates the critical configuration steps needed to transition a Django application from development to production. Available through the pip package manager, Djanbee handles server setup, environment configuration, Django settings optimization, and deployment - all from a simple command-line interface.

## Installation

```bash
pip install djanbee
```

## Requirements

- Python 3.6+
- pip
- Django project
- Linux/Ubuntu environment

## Features

Djanbee executes the following deployment tasks in sequence:

### 1. Launch
- Initializes server deployment
- Creates and configures socket files for the Django process with Gunicorn
- Generates optimized Nginx configuration files for serving the application

### 2. Setup
- Automatically locates and validates Django project structure
- Creates isolated Python environment with venv
- Installs all dependencies from requirements.txt

### 3. Configure
- Modifies settings.py to set DEBUG=False
- Configures ALLOWED_HOSTS and security settings
- Sets up database configuration for production use
- Generates secure SECRET_KEY

### 4. Deploy
- Transfers files to production location (/var/www/[domain_name]/)
- Sets appropriate permissions for production environment
- Configures Nginx and Gunicorn for the Django application

### 5. Run
- Executes Django's collectstatic command to gather static files
- Runs database migration commands to set up the database schema

## Server Architecture

Djanbee implements the industry-standard server architecture for Django applications:

```
Client requests → Nginx → Gunicorn → Django application
```

- **Nginx**: Handles client connections, SSL, static files, and acts as a buffer to the internet
- **Gunicorn**: Runs Python/Django code efficiently with multiple workers

## Command Reference

### Basic Command Syntax
```bash
django-djanbee [command] [options]
```

### Commands

| Command    | Description |
|------------|-------------|
| djanbee    | Display help information and available commands |
| launch     | Initialize Django server deployment by setting up Gunicorn socket and Nginx configuration |
| setup      | Create and configure virtual environment and install project dependencies |
| configure  | Modify Django settings.py for production and prepare database configuration |
| deploy     | Copy Django project and dependencies to web server directory |
| run        | Execute final deployment steps including database migrations and static file collection |

### Options

| Option    | Description | Used With |
|-----------|-------------|-----------|
| --help    | Show the help message and exit | All commands |
| -s        | Open the settings.py editing menu for production configuration | configure |

## Example Usage

### Complete Deployment Process
To run the complete deployment process:

```bash
djanbee launch
djanbee setup
djanbee configure
djanbee deploy
djanbee run
```

## Production Environment

After deployment, Djanbee creates the following structure:

```
/var/www/[domain_name]/
├── application/       # Your Django project files
│   ├── manage.py
│   ├── yourproject/
│   └── ...
├── env/               # Virtual environment
│   ├── bin/
│   ├── lib/
│   └── ...
├── static/            # Collected static files
└── media/             # User uploaded files
```

## Database Support

Currently, Djanbee is optimized for PostgreSQL with peer authentication, which:
- Uses the operating system's username to authenticate automatically
- Eliminates password management
- Provides enhanced security for local connections
- Simplifies deployment

## Security Notes

- Settings.py is modified before deployment for production-ready security
- File permissions are properly set (644 for files, 755 for directories)
- Socket file has 660 permissions owned by www-data group
- Static/media directories have 755 permissions with www-data ownership

## License

[Insert your license information here]

## Contributing

[Insert contribution guidelines here]
