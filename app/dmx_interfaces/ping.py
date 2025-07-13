import subprocess
import sys

def ping_simple(host):
    """Simple ping using system ping command"""
    param = '-n' if sys.platform.lower().startswith('win') else '-c'
    command = ['ping', param, '1', host]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=5)
        print (f"Pinging {host}: {result.stdout.strip()}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False

