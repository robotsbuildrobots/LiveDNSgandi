# Gandi DNS Updater

A Python script to automatically update a Gandi LiveDNS A record with your current public IP address.

## Setup

1.  **Create and Activate Virtual Environment**:
    Mac/Linux:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
    
    *Note: You must activate the virtual environment (`source venv/bin/activate`) before running the script, or use the direct path `./venv/bin/python`.*

2.  **Configuration**:
    You can configure the script using a `config.ini` file, command-line arguments, or environment variables.

    **Option A: config.ini (Recommended)**
    Copy the template and edit it:
    ```bash
    cp config.ini my_config.ini
    nano my_config.ini
    ```
    Content:
    ```ini
    [gandi]
    api_key = YOUR_GANDI_API_KEY
    domain = example.com
    record = @
    ```

    **Option B: Environment Variables**
    ```bash
    export GANDI_API_KEY="your_api_key"
    ```

## Usage

**Run with default config (config.ini):**
```bash
python3 gandi_updater.py
```

**Run with custom config file:**
```bash
python3 gandi_updater.py --config my_config.ini
```

**Run with CLI arguments (overrides config):**
```bash
python3 gandi_updater.py --domain example.com --record www --api-key YOUR_KEY
```

**Dry Run (Test without changes):**
```bash
python3 gandi_updater.py --dry-run
```

## Automation (Cron)

To run this every hour, add `cron` entry:
```bash
0 * * * * cd /path/to/GandiDNS && /usr/bin/python3 gandi_updater.py
```
