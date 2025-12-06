#!/usr/bin/env python3
import os
import sys
import argparse
import requests
import configparser


def get_public_ip():
    """Retrieves the current public IP address using api.ipify.org."""
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=10)
        response.raise_for_status()
        return response.json()['ip']
    except requests.RequestException as e:
        print(f"Error retrieving public IP: {e}", file=sys.stderr)
        sys.exit(1)

def load_config(config_file):
    config = configparser.ConfigParser()
    if os.path.exists(config_file):
        config.read(config_file)
        if 'gandi' in config:
            return config['gandi']
    return {}

def get_gandi_record(api_key, domain, name):
    """Retrieves the current A record from Gandi LiveDNS."""
    url = f"https://api.gandi.net/v5/livedns/domains/{domain}/records/{name}/A"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 404:
            return None # Record doesn't exist
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error communicating with Gandi API (Get): {e}", file=sys.stderr)
        if response.content:
            print(f"Response: {response.content.decode()}", file=sys.stderr)
        sys.exit(1)

def update_gandi_record(api_key, domain, name, new_ip, dry_run=False):
    """Updates the A record on Gandi LiveDNS."""
    url = f"https://api.gandi.net/v5/livedns/domains/{domain}/records/{name}/A"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "rrset_ttl": 1800, # Default TTL
        "rrset_values": [new_ip]
    }
    
    if dry_run:
        print(f"[DRY-RUN] Would update {name}.{domain} A record to {new_ip}")
        return

    try:
        # PUT creates or updates
        response = requests.put(url, headers=headers, json=payload)
        response.raise_for_status()
        print(f"Successfully updated {name}.{domain} to {new_ip}")
    except requests.RequestException as e:
        print(f"Error updating Gandi record: {e}", file=sys.stderr)
        if response.content:
            print(f"Response: {response.content.decode()}", file=sys.stderr)
        sys.exit(1)



def main():
    
    parser = argparse.ArgumentParser(description="Update Gandi DNS A record with current public IP.")
    parser.add_argument("--domain", help="The domain name (e.g., example.com)")
    parser.add_argument("--record", help="The A record name (e.g., @, www, sub)")
    parser.add_argument("--api-key", help="Gandi LiveDNS API Key")
    parser.add_argument("--config", default="config.ini", help="Path to config file (default: config.ini)")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without making changes")
    
    args = parser.parse_args()
    
    # Load config file
    file_config = load_config(args.config)
    
    # Priority: CLI Args > Config File > Environment Variables
    api_key = args.api_key or file_config.get('api_key') or os.getenv("GANDI_API_KEY")
    domain = args.domain or file_config.get('domain')
    record = args.record or file_config.get('record')
    
    if not api_key:
        print("Error: API Key must be provided via --api-key, config file, or GANDI_API_KEY.", file=sys.stderr)
        sys.exit(1)
    if not domain:
        print("Error: Domain must be provided via --domain or config file.", file=sys.stderr)
        sys.exit(1)
    if not record:
        print("Error: Record must be provided via --record or config file.", file=sys.stderr)
        sys.exit(1)

    print(f"Configuration loaded for: {record}.{domain}")
    print("Retrieving public IP...")
    current_ip = get_public_ip()
    print(f"Current Public IP: {current_ip}")

    print(f"Checking existing record for {record}.{domain}...")
    record_data = get_gandi_record(api_key, domain, record)
    
    if record_data:
        existing_ips = record_data.get('rrset_values', [])
        if current_ip in existing_ips:
            print(f"Record {record}.{domain} is already set to {current_ip}. No action needed.")
            return
        else:
            print(f"Current record values: {existing_ips}. Update required.")
    else:
        print(f"Record {record}.{domain} not found. Will create new record.")

    update_gandi_record(api_key, domain, record, current_ip, args.dry_run)

if __name__ == "__main__":
    main()
