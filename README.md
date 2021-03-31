# d42-apptemplates
Quick way to define templates to create application components for apps that Device42 does not support out of the box and pin/star services accordingly.

## Features
- Automatically pin / set topology status for service instances matching on name or cmd path args.
- Automatically create application component records on devices with associated service instances

## Requirements
- Python 3.6.9 or > 
    - PyYAML==5.4.1
    - requests==2.25.1
- Device42 MA 16.22.00.1612807182 or >

## How to Use
### 1. Create a new virtualenv 

    venv d42-apptemplates

### 2. Install requirements

    pip install -r requirements.txt

### 3. Rename config.yaml.example to config.yaml and fill out the required fields

### 4. Replace example templates in templates.yaml with your own

### 5. Run 

    python starter.py

### 6. Schedule via cron
In crontab add a line like the following to set your command execution schedule:

    0 0 * * * python /home/your_user_here/d42-apptemplates/starter.py

This will run the script every night at midnight.