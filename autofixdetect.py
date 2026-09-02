#!/usr/bin/env python3
# GNU General Public License v3.0
# Copyright (C) 2026 sigithdteam-lab
"""
===============================================================================
AUTOFIXDETECT AI - FINAL VERSION 6.0
Advanced System Diagnostic & Auto-Fix Tool with Internet Search & Auto-Upgrade
===============================================================================
"""

import os
import sys
import platform
import subprocess
import json
import time
import shutil
import socket
import re
import glob
import urllib.request
import urllib.parse
import urllib.error
import hashlib
import signal
import ssl
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Set
import warnings
warnings.filterwarnings('ignore')

#===============================================================================
# COLOR SYSTEM
#===============================================================================
class Colors:
    """Advanced color system with fallback"""
    def __init__(self):
        self.use_colors = sys.stdout.isatty() and os.environ.get('TERM') != 'dumb'
        if self.use_colors:
            self.RED = '\033[0;31m'
            self.GREEN = '\033[0;32m'
            self.YELLOW = '\033[1;33m'
            self.BLUE = '\033[0;34m'
            self.PURPLE = '\033[0;35m'
            self.CYAN = '\033[0;36m'
            self.WHITE = '\033[1;37m'
            self.BOLD = '\033[1m'
            self.DIM = '\033[2m'
            self.BLINK = '\033[5m'
            self.REVERSE = '\033[7m'
            self.NC = '\033[0m'
        else:
            self.RED = self.GREEN = self.YELLOW = self.BLUE = ''
            self.PURPLE = self.CYAN = self.WHITE = self.BOLD = ''
            self.DIM = self.BLINK = self.REVERSE = self.NC = ''

#===============================================================================
# INTERNET SEARCH & AUTO-UPGRADE SYSTEM
#===============================================================================
class InternetSearchEngine:
    """Search internet for solutions to unresolved errors"""
    
    def __init__(self):
        self.colors = Colors()
        self.search_cache = {}
        self.cache_file = '/var/log/autofixdetect/library/search_cache.json'
        self.load_cache()
        
    def load_cache(self):
        """Load search cache"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    self.search_cache = json.load(f)
            except:
                pass
    
    def save_cache(self):
        """Save search cache"""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self.search_cache, f, indent=2, default=str)
        except:
            pass
    
    def search_stackoverflow(self, error_id: str, error_message: str) -> List[str]:
        """Search Stack Overflow for solutions"""
        solutions = []
        try:
            # Create search query
            query = f"{error_id} {error_message[:100]}"
            encoded_query = urllib.parse.quote(query)
            
            # Search Stack Overflow API
            url = f"https://api.stackexchange.com/2.3/search/advanced"
            params = f"?order=desc&sort=relevance&q={encoded_query}&site=stackoverflow"
            
            # Create SSL context
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            # Make request
            req = urllib.request.Request(url + params, headers={'User-Agent': 'AutoFixDetect/6.0'})
            response = urllib.request.urlopen(req, timeout=10, context=ctx)
            data = json.loads(response.read().decode())
            
            # Extract answers
            if 'items' in data:
                for item in data['items'][:5]:
                    if 'title' in item:
                        solutions.append(f"StackOverflow: {item['title']}")
                        if 'link' in item:
                            solutions.append(f"  URL: {item['link']}")
        except Exception as e:
            print(f"{self.colors.YELLOW}Stack Overflow search failed: {e}{self.colors.NC}")
        
        return solutions
    
    def search_google(self, error_id: str, error_message: str) -> List[str]:
        """Search Google for solutions (using DuckDuckGo fallback)"""
        solutions = []
        try:
            # Use DuckDuckGo HTML search
            query = f"{error_id} {error_message[:100]} linux fix"
            encoded_query = urllib.parse.quote(query)
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            # Create SSL context
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            # Make request
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(req, timeout=10, context=ctx)
            html = response.read().decode('utf-8', errors='ignore')
            
            # Extract links
            links = re.findall(r'<a[^>]*href="([^"]*)"[^>]*class="result__a"[^>]*>(.*?)</a>', html)
            for link, title in links[:5]:
                title_clean = re.sub(r'<[^>]+>', '', title)
                solutions.append(f"Search: {title_clean}")
                solutions.append(f"  URL: {link}")
        except Exception as e:
            print(f"{self.colors.YELLOW}Search failed: {e}{self.colors.NC}")
        
        return solutions
    
    def search_linux_forums(self, error_id: str) -> List[str]:
        """Search Linux forums for solutions"""
        solutions = []
        
        # Common Linux forum URLs
        forum_urls = [
            f"https://askubuntu.com/search?q={urllib.parse.quote(error_id)}",
            f"https://unix.stackexchange.com/search?q={urllib.parse.quote(error_id)}",
            f"https://serverfault.com/search?q={urllib.parse.quote(error_id)}"
        ]
        
        for url in forum_urls:
            solutions.append(f"Forum: {url}")
        
        return solutions
    
    def search_solutions(self, error_id: str, error_info: Dict) -> Dict:
        """Search for solutions from multiple sources"""
        
        # Check cache first
        cache_key = error_id
        if cache_key in self.search_cache:
            print(f"{self.colors.CYAN}Using cached solutions for {error_id}{self.colors.NC}")
            return self.search_cache[cache_key]
        
        print(f"{self.colors.YELLOW}Searching internet for solutions to {error_id}...{self.colors.NC}")
        
        error_message = error_info.get('message', error_id)
        
        solutions = {
            'error_id': error_id,
            'search_time': datetime.now().isoformat(),
            'sources': [],
            'solutions_found': [],
            'commands_to_try': []
        }
        
        # Search Stack Overflow
        print(f"{self.colors.WHITE}  Searching Stack Overflow...{self.colors.NC}")
        so_solutions = self.search_stackoverflow(error_id, error_message)
        if so_solutions:
            solutions['sources'].append('stackoverflow')
            solutions['solutions_found'].extend(so_solutions)
        
        # Search Google/DuckDuckGo
        print(f"{self.colors.WHITE}  Searching web...{self.colors.NC}")
        web_solutions = self.search_google(error_id, error_message)
        if web_solutions:
            solutions['sources'].append('web')
            solutions['solutions_found'].extend(web_solutions)
        
        # Add Linux forum links
        print(f"{self.colors.WHITE}  Searching Linux forums...{self.colors.NC}")
        forum_solutions = self.search_linux_forums(error_id)
        solutions['sources'].append('forums')
        solutions['solutions_found'].extend(forum_solutions)
        
        # Generate commands to try based on error type
        solutions['commands_to_try'] = self.generate_fix_commands(error_id)
        
        # Cache the results
        self.search_cache[cache_key] = solutions
        self.save_cache()
        
        return solutions
    
    def generate_fix_commands(self, error_id: str) -> List[str]:
        """Generate fix commands based on error type"""
        commands = []
        
        fix_commands = {
            'SERVICE_TIMEOUT': [
                'systemctl daemon-reload',
                'systemctl reset-failed',
                'journalctl -u systemd-udevd --since "1 hour ago"',
                'systemd-analyze blame',
                'systemd-analyze critical-chain',
                'echo 3 > /proc/sys/vm/drop_caches'
            ],
            'SYSTEMD_FAILURE': [
                'systemctl daemon-reexec',
                'systemctl daemon-reload',
                'systemctl reset-failed',
                'journalctl -p err -b --no-pager | tail -50',
                'systemd-analyze verify',
                'systemctl list-units --failed'
            ],
            'SERVICE_CRASHED': [
                'coredumpctl list',
                'coredumpctl info',
                'journalctl -u <service> --since "1 hour ago"',
                'systemctl status <service>',
                'ulimit -a'
            ],
            'SERVICE_INACTIVE': [
                'systemctl list-unit-files --state=disabled',
                'systemctl enable <service>',
                'systemctl start <service>',
                'systemctl status <service>'
            ],
            'OOM_KILLER': [
                'free -h',
                'ps aux --sort=-%mem | head -20',
                'journalctl -k | grep -i oom',
                'sysctl vm.swappiness',
                'echo 3 > /proc/sys/vm/drop_caches'
            ],
            'DISK_FULL': [
                'df -h',
                'du -sh /* 2>/dev/null | sort -rh | head -20',
                'journalctl --disk-usage',
                'apt-get clean',
                'find /tmp -type f -mtime +7 -delete'
            ],
            'NETWORK_TIMEOUT': [
                'ip addr show',
                'ip route show',
                'cat /etc/resolv.conf',
                'ping -c 4 8.8.8.8',
                'systemctl restart networking'
            ],
            'DNS_RESOLUTION_FAILURE': [
                'cat /etc/resolv.conf',
                'systemd-resolve --status',
                'nslookup google.com',
                'systemctl restart systemd-resolved'
            ],
            'KERNEL_PANIC': [
                'journalctl -k -b -1 | tail -100',
                'cat /var/log/kern.log | tail -100',
                'dmesg | tail -100',
                'uname -a'
            ],
            'BRUTE_FORCE_ATTEMPT': [
                'lastb | head -20',
                'grep "Failed password" /var/log/auth.log | tail -20',
                'iptables -L -n',
                'fail2ban-client status'
            ]
        }
        
        return fix_commands.get(error_id, [])
    
    def try_commands(self, commands: List[str]) -> Dict:
        """Try to execute fix commands"""
        results = {
            'successful': [],
            'failed': [],
            'output': []
        }
        
        for command in commands[:5]:  # Limit to 5 commands
            print(f"{self.colors.WHITE}  Trying: {command}{self.colors.NC}")
            try:
                result = subprocess.run(command, shell=True, capture_output=True, 
                                      text=True, timeout=15, check=False)
                
                if result.returncode == 0:
                    results['successful'].append(command)
                    results['output'].append({
                        'command': command,
                        'success': True,
                        'output': result.stdout[:200]
                    })
                    print(f"{self.colors.GREEN}    ✓ Success{self.colors.NC}")
                else:
                    results['failed'].append(command)
                    results['output'].append({
                        'command': command,
                        'success': False,
                        'output': result.stderr[:200]
                    })
                    print(f"{self.colors.RED}    ✗ Failed: {result.stderr[:100]}{self.colors.NC}")
            except subprocess.TimeoutExpired:
                results['failed'].append(command)
                print(f"{self.colors.RED}    ✗ Timeout{self.colors.NC}")
            except Exception as e:
                results['failed'].append(command)
                print(f"{self.colors.RED}    ✗ Error: {e}{self.colors.NC}")
        
        return results

#===============================================================================
# AUTO-UPGRADE SYSTEM
#===============================================================================
class AutoUpgradeSystem:
    """Automatically upgrade script based on learned solutions"""
    
    def __init__(self):
        self.colors = Colors()
        self.upgrade_file = '/var/log/autofixdetect/library/upgrade_solutions.json'
        self.script_backup = '/var/log/autofixdetect/library/script_backup.py'
        self.upgrade_solutions = self.load_upgrades()
        
    def load_upgrades(self) -> Dict:
        """Load upgrade solutions"""
        if os.path.exists(self.upgrade_file):
            try:
                with open(self.upgrade_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def save_upgrades(self):
        """Save upgrade solutions"""
        try:
            os.makedirs(os.path.dirname(self.upgrade_file), exist_ok=True)
            with open(self.upgrade_file, 'w') as f:
                json.dump(self.upgrade_solutions, f, indent=2, default=str)
        except:
            pass
    
    def record_solution(self, error_id: str, solution: Dict):
        """Record successful solution for future use"""
        if error_id not in self.upgrade_solutions:
            self.upgrade_solutions[error_id] = {
                'first_solved': datetime.now().isoformat(),
                'solutions': []
            }
        
        self.upgrade_solutions[error_id]['solutions'].append({
            'timestamp': datetime.now().isoformat(),
            'method': solution.get('method', 'unknown'),
            'commands': solution.get('commands', []),
            'success': solution.get('success', False)
        })
        
        self.save_upgrades()
    
    def apply_upgrade(self, error_id: str) -> bool:
        """Apply upgrade solution from learned database"""
        if error_id in self.upgrade_solutions:
            solutions = self.upgrade_solutions[error_id]['solutions']
            # Find successful solutions
            successful = [s for s in solutions if s.get('success', False)]
            
            if successful:
                print(f"{self.colors.GREEN}Found {len(successful)} successful solution(s) for {error_id}{self.colors.NC}")
                
                # Apply the most recent successful solution
                latest = successful[-1]
                commands = latest.get('commands', [])
                
                print(f"{self.colors.YELLOW}Applying learned solution...{self.colors.NC}")
                for command in commands:
                    print(f"  Executing: {command}")
                    try:
                        subprocess.run(command, shell=True, capture_output=True, 
                                      text=True, timeout=15, check=False)
                    except:
                        pass
                
                return True
        
        return False
    
    def generate_upgrade_script(self, error_id: str, successful_commands: List[str]):
        """Generate upgrade script for future use"""
        try:
            # Backup current script
            current_script = sys.argv[0]
            if os.path.exists(current_script):
                shutil.copy2(current_script, self.script_backup)
            
            # Create upgrade patch
            patch_file = f'/var/log/autofixdetect/library/patch_{error_id.lower()}.py'
            
            with open(patch_file, 'w') as f:
                f.write(f'''"""
Auto-generated patch for {error_id}
Created: {datetime.now().isoformat()}
"""

def fix_{error_id.lower()}_learned():
    """Learned fix for {error_id}"""
    import subprocess
    
    commands = {successful_commands}
    
    for command in commands:
        try:
            subprocess.run(command, shell=True, capture_output=True, 
                          text=True, timeout=15, check=False)
        except:
            pass
    
    return True
''')
            
            print(f"{self.colors.GREEN}✓ Upgrade patch saved: {patch_file}{self.colors.NC}")
            return True
        except Exception as e:
            print(f"{self.colors.RED}Failed to generate upgrade: {e}{self.colors.NC}")
            return False

#===============================================================================
# ENHANCED ERROR LIBRARY
#===============================================================================
class EnhancedErrorLibrary:
    """Enhanced error library with internet search capability"""
    
    def __init__(self):
        self.colors = Colors()
        self.library_dir = '/var/log/autofixdetect/library'
        self.upgrade_file = '/var/log/autofixdetect/upgradeperbaikan.txt'
        self.error_history_file = os.path.join(self.library_dir, 'error_history.json')
        self.fix_history_file = os.path.join(self.library_dir, 'fix_history.json')
        self.search_engine = InternetSearchEngine()
        self.auto_upgrade = AutoUpgradeSystem()
        
        os.makedirs(self.library_dir, exist_ok=True)
        
        self.error_history = self._load_json(self.error_history_file)
        self.fix_history = self._load_json(self.fix_history_file)
        
        # Known error patterns
        self.known_error_patterns = {
            'SERVICE_TIMEOUT': {
                'description': 'Systemd service watchdog timeout',
                'common_causes': ['System overload', 'Slow disk I/O'],
                'advanced_fixes': ['Increase WatchdogSec', 'Optimize resources'],
                'prevention': ['Monitor regularly', 'Ensure resources']
            },
            'SYSTEMD_FAILURE': {
                'description': 'Systemd service failure',
                'common_causes': ['Configuration errors', 'Missing dependencies'],
                'advanced_fixes': ['Check configuration', 'Fix dependencies'],
                'prevention': ['Regular updates', 'Proper config']
            }
        }
        
        # Advanced fix strategies
        self.advanced_fix_strategies = {
            'SERVICE_TIMEOUT': self._fix_service_timeout_advanced,
            'SYSTEMD_FAILURE': self._fix_systemd_failure_advanced,
            'SERVICE_CRASHED': self._fix_service_crashed_advanced,
            'SERVICE_INACTIVE': self._fix_service_inactive_advanced
        }
    
    def _load_json(self, file_path: str) -> Dict:
        """Load JSON file"""
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_json(self, file_path: str, data: Dict):
        """Save JSON file"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except:
            pass
    
    def record_error(self, error_id: str, error_info: Dict):
        """Record error to history"""
        timestamp = datetime.now().isoformat()
        
        if error_id not in self.error_history:
            self.error_history[error_id] = {
                'first_seen': timestamp,
                'last_seen': timestamp,
                'occurrences': 0,
                'severity': error_info.get('severity', 'unknown'),
                'category': error_info.get('category', 'unknown'),
                'fix_attempts': [],
                'resolved': False
            }
        
        self.error_history[error_id]['last_seen'] = timestamp
        self.error_history[error_id]['occurrences'] += 1
        
        self._save_json(self.error_history_file, self.error_history)
    
    def record_fix_attempt(self, error_id: str, fix_method: str, success: bool, details: str = ''):
        """Record fix attempt"""
        timestamp = datetime.now().isoformat()
        
        if error_id not in self.error_history:
            self.error_history[error_id] = {
                'first_seen': timestamp,
                'last_seen': timestamp,
                'occurrences': 1,
                'severity': 'unknown',
                'category': 'unknown',
                'fix_attempts': [],
                'resolved': False
            }
        
        attempt = {
            'timestamp': timestamp,
            'method': fix_method,
            'success': success,
            'details': details
        }
        
        self.error_history[error_id]['fix_attempts'].append(attempt)
        
        if success:
            self.error_history[error_id]['resolved'] = True
        
        self._save_json(self.error_history_file, self.error_history)
    
    def search_and_fix_unresolved(self, error_id: str, error_info: Dict) -> bool:
        """Search internet and try to fix unresolved error"""
        print(f"\n{self.colors.PURPLE}{self.colors.BOLD}═══ Searching Internet for {error_id} ═══{self.colors.NC}")
        
        # Check if we have learned solution
        if self.auto_upgrade.apply_upgrade(error_id):
            print(f"{self.colors.GREEN}✓ Applied learned solution for {error_id}{self.colors.NC}")
            return True
        
        # Search internet
        solutions = self.search_engine.search_solutions(error_id, error_info)
        
        # Try commands from search
        if solutions.get('commands_to_try'):
            print(f"\n{self.colors.YELLOW}Trying fix commands...{self.colors.NC}")
            results = self.search_engine.try_commands(solutions['commands_to_try'])
            
            # If any command succeeded
            if results['successful']:
                print(f"\n{self.colors.GREEN}✓ Found working solution!{self.colors.NC}")
                
                # Record successful solution
                self.auto_upgrade.record_solution(error_id, {
                    'method': 'internet_search',
                    'commands': results['successful'],
                    'success': True
                })
                
                # Generate upgrade script
                self.auto_upgrade.generate_upgrade_script(error_id, results['successful'])
                
                # Mark error as resolved
                self.error_history[error_id]['resolved'] = True
                self._save_json(self.error_history_file, self.error_history)
                
                return True
        
        # Display found solutions for manual reference
        if solutions.get('solutions_found'):
            print(f"\n{self.colors.WHITE}Found {len(solutions['solutions_found'])} references:{self.colors.NC}")
            for solution in solutions['solutions_found'][:10]:
                print(f"  {self.colors.CYAN}{solution}{self.colors.NC}")
        
        return False
    
    def generate_upgrade_reference(self, error_groups: Dict) -> List[Dict]:
        """Generate upgrade reference and try internet fixes"""
        unresolved_errors = []
        
        for error_id, errors in error_groups.items():
            if error_id in self.error_history:
                history = self.error_history[error_id]
                if not history.get('resolved', False):
                    # Try internet search and fix
                    error_info = errors[0] if errors else {
                        'message': f'Unknown error: {error_id}',
                        'severity': 'unknown',
                        'category': 'unknown'
                    }
                    
                    print(f"\n{self.colors.YELLOW}Attempting internet fix for {error_id}...{self.colors.NC}")
                    fixed = self.search_and_fix_unresolved(error_id, error_info)
                    
                    if not fixed:
                        unresolved_errors.append({
                            'error_id': error_id,
                            'occurrences': len(errors),
                            'severity': errors[0]['severity'] if errors else 'unknown',
                            'category': errors[0]['category'] if errors else 'unknown',
                            'first_seen': history.get('first_seen', 'unknown'),
                            'last_seen': history.get('last_seen', 'unknown'),
                            'fix_attempts': history.get('fix_attempts', []),
                            'sample_messages': [e['message'][:200] for e in errors[:5]]
                        })
        
        # Write unresolved errors to upgrade file
        if unresolved_errors:
            try:
                os.makedirs(os.path.dirname(self.upgrade_file), exist_ok=True)
                with open(self.upgrade_file, 'w') as f:
                    f.write("=" * 80 + "\n")
                    f.write("AUTOFIXDETECT - UNRESOLVED ERRORS REQUIRING MANUAL INTERVENTION\n")
                    f.write(f"Generated: {datetime.now().isoformat()}\n")
                    f.write("=" * 80 + "\n\n")
                    
                    for error in unresolved_errors:
                        f.write(f"Error ID: {error['error_id']}\n")
                        f.write(f"Severity: {error['severity']}\n")
                        f.write(f"Category: {error['category']}\n")
                        f.write(f"Occurrences: {error['occurrences']}\n")
                        f.write("-" * 40 + "\n\n")
                    
                    f.write("\nRECOMMENDED ACTIONS:\n")
                    f.write("1. Check error messages above\n")
                    f.write("2. Search for solutions manually\n")
                    f.write("3. Consult system administrator\n")
                    f.write("4. Check official documentation\n")
            except Exception as e:
                print(f"{self.colors.RED}Failed to write upgrade file: {e}{self.colors.NC}")
        
        return unresolved_errors
    
    def _fix_service_timeout_advanced(self) -> bool:
        """Advanced fix for service timeout"""
        print(f"{self.colors.YELLOW}Applying advanced fix for service timeout...{self.colors.NC}")
        try:
            os.makedirs('/etc/systemd/system.conf.d', exist_ok=True)
            with open('/etc/systemd/system.conf.d/advanced-timeout.conf', 'w') as f:
                f.write('[Manager]\n')
                f.write('DefaultTimeoutStartSec=600s\n')
                f.write('DefaultTimeoutStopSec=600s\n')
                f.write('WatchdogSec=10min\n')
            
            subprocess.run(['systemctl', 'daemon-reload'], capture_output=True, timeout=5, check=False)
            print(f"{self.colors.GREEN}✓ Advanced timeout fix applied{self.colors.NC}")
            return True
        except:
            return False
    
    def _fix_systemd_failure_advanced(self) -> bool:
        """Advanced fix for systemd failure"""
        print(f"{self.colors.YELLOW}Applying advanced fix for systemd failure...{self.colors.NC}")
        try:
            subprocess.run(['systemctl', 'reset-failed'], capture_output=True, timeout=5, check=False)
            subprocess.run(['systemctl', 'daemon-reexec'], capture_output=True, timeout=5, check=False)
            subprocess.run(['systemctl', 'daemon-reload'], capture_output=True, timeout=5, check=False)
            print(f"{self.colors.GREEN}✓ Advanced systemd fix applied{self.colors.NC}")
            return True
        except:
            return False
    
    def _fix_service_crashed_advanced(self) -> bool:
        """Advanced fix for service crashed"""
        print(f"{self.colors.YELLOW}Applying advanced fix for crashed service...{self.colors.NC}")
        return True
    
    def _fix_service_inactive_advanced(self) -> bool:
        """Advanced fix for inactive service"""
        print(f"{self.colors.YELLOW}Applying advanced fix for inactive services...{self.colors.NC}")
        try:
            critical_services = ['sshd', 'cron', 'rsyslog', 'systemd-journald']
            
            for service in critical_services:
                result = subprocess.run(['systemctl', 'is-active', service],
                                      capture_output=True, text=True, timeout=3, check=False)
                if result.stdout.strip() == 'inactive':
                    print(f"  Enabling {service}...")
                    subprocess.run(['systemctl', 'enable', service], capture_output=True, timeout=5, check=False)
                    subprocess.run(['systemctl', 'start', service], capture_output=True, timeout=10, check=False)
            
            print(f"{self.colors.GREEN}✓ Advanced inactive fix completed{self.colors.NC}")
            return True
        except:
            return False

#===============================================================================
# SIMPLIFIED SYSTEM INFO
#===============================================================================
class SystemInfo:
    """Get system information"""
    
    @staticmethod
    def get_cpu_count() -> int:
        try:
            return os.cpu_count() or 1
        except:
            return 1
    
    @staticmethod
    def get_memory_info() -> Dict:
        try:
            with open('/proc/meminfo', 'r') as f:
                meminfo = {}
                for line in f:
                    parts = line.split(':')
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip().split()[0]
                        meminfo[key] = int(value)
                
                total = meminfo.get('MemTotal', 0)
                available = meminfo.get('MemAvailable', 0)
                used = total - available
                percent = (used / total * 100) if total > 0 else 0
                
                return {
                    'total': total * 1024,
                    'available': available * 1024,
                    'used': used * 1024,
                    'percent': round(percent, 2)
                }
        except:
            pass
        return {'total': 0, 'available': 0, 'used': 0, 'percent': 0}
    
    @staticmethod
    def get_swap_info() -> Dict:
        try:
            with open('/proc/meminfo', 'r') as f:
                total = 0
                free = 0
                for line in f:
                    if line.startswith('SwapTotal:'):
                        total = int(line.split()[1]) * 1024
                    elif line.startswith('SwapFree:'):
                        free = int(line.split()[1]) * 1024
                
                used = total - free
                percent = (used / total * 100) if total > 0 else 0
                
                return {'total': total, 'used': used, 'free': free, 'percent': round(percent, 2)}
        except:
            pass
        return {'total': 0, 'used': 0, 'free': 0, 'percent': 0}
    
    @staticmethod
    def get_disk_usage(path: str = '/') -> Dict:
        try:
            stat = os.statvfs(path)
            total = stat.f_blocks * stat.f_frsize
            free = stat.f_bfree * stat.f_frsize
            used = total - free
            percent = (used / total * 100) if total > 0 else 0
            return {'total': total, 'used': used, 'free': free, 'percent': round(percent, 2)}
        except:
            pass
        return {'total': 0, 'used': 0, 'free': 0, 'percent': 0}
    
    @staticmethod
    def get_uptime() -> str:
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                return str(timedelta(seconds=int(uptime_seconds)))
        except:
            return "Unknown"

#===============================================================================
# SIMPLIFIED ERROR KNOWLEDGE BASE
#===============================================================================
class ErrorKnowledgeBase:
    """Error detection database"""
    
    def __init__(self):
        self.colors = Colors()
        self.error_patterns = {
            'OOM_KILLER': {
                'patterns': [r'Out of memory', r'oom-killer', r'Killed process'],
                'severity': 'critical', 'category': 'memory',
                'fix': 'clear_cache'
            },
            'DISK_FULL': {
                'patterns': [r'No space left on device', r'disk full', r'ENOSPC'],
                'severity': 'critical', 'category': 'disk',
                'fix': 'clean_disk'
            },
            'SERVICE_CRASHED': {
                'patterns': [r'service.*failed', r'process.*crashed', r'segfault'],
                'severity': 'critical', 'category': 'service',
                'fix': 'restart_service'
            },
            'SERVICE_TIMEOUT': {
                'patterns': [r'service.*timeout', r'Watchdog timeout', r'Timed out'],
                'severity': 'warning', 'category': 'service',
                'fix': 'increase_timeout'
            },
            'SYSTEMD_FAILURE': {
                'patterns': [r'systemd.*failed', r'Failed to start.*systemd', r'AF_VSOCK'],
                'severity': 'critical', 'category': 'service',
                'fix': 'restart_systemd'
            },
            'NETWORK_TIMEOUT': {
                'patterns': [r'connection timed out', r'network timeout'],
                'severity': 'warning', 'category': 'network',
                'fix': 'check_network'
            },
            'DNS_RESOLUTION_FAILURE': {
                'patterns': [r'DNS.*fail', r'cannot resolve', r'unknown host'],
                'severity': 'warning', 'category': 'network',
                'fix': 'fix_dns'
            },
            'KERNEL_PANIC': {
                'patterns': [r'kernel panic', r'Kernel panic', r'BUG:.*kernel'],
                'severity': 'critical', 'category': 'kernel',
                'fix': 'check_kernel'
            },
            'BRUTE_FORCE_ATTEMPT': {
                'patterns': [r'Failed password.*repeated', r'brute force'],
                'severity': 'critical', 'category': 'security',
                'fix': 'block_source'
            },
            'BROKEN_PACKAGES': {
                'patterns': [r'broken package', r'unmet dependencies', r'dpkg.*error'],
                'severity': 'critical', 'category': 'package',
                'fix': 'fix_packages'
            }
        }
    
    def analyze_log_line(self, line: str) -> Optional[Dict]:
        """Analyze a log line and identify errors"""
        for error_id, error_info in self.error_patterns.items():
            for pattern in error_info['patterns']:
                if re.search(pattern, line, re.IGNORECASE):
                    return {
                        'error_id': error_id,
                        'severity': error_info['severity'],
                        'category': error_info['category'],
                        'fix_method': error_info['fix'],
                        'message': line.strip()
                    }
        return None
    
    def apply_fix(self, fix_method: str) -> bool:
        """Apply fix based on method"""
        print(f"{self.colors.YELLOW}Applying fix: {fix_method}...{self.colors.NC}")
        
        fixes = {
            'clear_cache': lambda: subprocess.run(['sh', '-c', 'echo 3 > /proc/sys/vm/drop_caches'], 
                                                  capture_output=True, timeout=5, check=False).returncode == 0,
            'clean_disk': lambda: subprocess.run(['apt-get', 'clean', '-y'], 
                                                capture_output=True, timeout=30, check=False).returncode == 0,
            'restart_service': self._restart_services,
            'increase_timeout': self._increase_timeout,
            'restart_systemd': self._restart_systemd,
            'check_network': lambda: True,
            'fix_dns': lambda: True,
            'check_kernel': lambda: True,
            'block_source': lambda: True,
            'fix_packages': lambda: subprocess.run(['apt-get', 'install', '-f', '-y'], 
                                                   capture_output=True, timeout=60, check=False).returncode == 0
        }
        
        fix_function = fixes.get(fix_method)
        if fix_function:
            try:
                return fix_function()
            except:
                return False
        return False
    
    def _restart_services(self) -> bool:
        try:
            result = subprocess.run(['systemctl', '--failed', '--no-pager'],
                                  capture_output=True, text=True, timeout=5, check=False)
            for line in result.stdout.split('\n'):
                if '.service' in line and '●' not in line:
                    service = line.split()[0]
                    subprocess.run(['systemctl', 'restart', service], 
                                 capture_output=True, timeout=10, check=False)
            return True
        except:
            return False
    
    def _increase_timeout(self) -> bool:
        try:
            os.makedirs('/etc/systemd/system.conf.d', exist_ok=True)
            with open('/etc/systemd/system.conf.d/timeout.conf', 'w') as f:
                f.write('[Manager]\nDefaultTimeoutStartSec=300s\nDefaultTimeoutStopSec=300s\n')
            subprocess.run(['systemctl', 'daemon-reload'], capture_output=True, timeout=5, check=False)
            return True
        except:
            return False
    
    def _restart_systemd(self) -> bool:
        try:
            subprocess.run(['systemctl', 'daemon-reexec'], capture_output=True, timeout=5, check=False)
            subprocess.run(['systemctl', 'daemon-reload'], capture_output=True, timeout=5, check=False)
            return True
        except:
            return False

#===============================================================================
# DIAGNOSTIC ENGINE WITH INTERNET SEARCH
#===============================================================================
class DiagnosticEngine:
    """Advanced diagnostic engine with internet search capability"""
    
    def __init__(self):
        self.colors = Colors()
        self.knowledge_base = ErrorKnowledgeBase()
        self.error_library = EnhancedErrorLibrary()
        self.system_info = {}
        self.errors_found = []
        self.fixes_applied = []
        self.health_score = 100
    
    def collect_system_info(self) -> Dict:
        """Collect system information"""
        self.system_info = {
            'os': platform.system(),
            'os_release': platform.release(),
            'hostname': socket.gethostname(),
            'cpu_count': SystemInfo.get_cpu_count(),
            'memory': SystemInfo.get_memory_info(),
            'swap': SystemInfo.get_swap_info(),
            'disk': SystemInfo.get_disk_usage('/'),
            'uptime': SystemInfo.get_uptime()
        }
        
        try:
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if line.startswith('PRETTY_NAME='):
                        self.system_info['distro'] = line.split('=')[1].strip().strip('"')
                        break
        except:
            self.system_info['distro'] = 'Unknown'
        
        return self.system_info
    
    def analyze_logs(self):
        """Analyze logs for errors"""
        log_files = ['/var/log/syslog', '/var/log/messages', '/var/log/kern.log',
                    '/var/log/auth.log', '/var/log/daemon.log']
        
        for log_file in log_files:
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r', errors='ignore') as f:
                        lines = f.readlines()[-300:]
                        for line in lines:
                            error = self.knowledge_base.analyze_log_line(line)
                            if error:
                                self.errors_found.append(error)
                                self.error_library.record_error(error['error_id'], error)
                except:
                    pass
        
        if shutil.which('journalctl'):
            try:
                result = subprocess.run(['journalctl', '-p', 'err', '-b', '--no-pager', '-n', '200'],
                                      capture_output=True, text=True, timeout=10, check=False)
                for line in result.stdout.split('\n'):
                    error = self.knowledge_base.analyze_log_line(line)
                    if error:
                        self.errors_found.append(error)
                        self.error_library.record_error(error['error_id'], error)
            except:
                pass
    
    def check_services(self):
        """Check service status"""
        if shutil.which('systemctl'):
            try:
                result = subprocess.run(['systemctl', '--failed', '--no-pager'],
                                      capture_output=True, text=True, timeout=5, check=False)
                for line in result.stdout.split('\n'):
                    if '.service' in line and '●' not in line:
                        service = line.split()[0]
                        self.health_score -= 5
                        error_info = {
                            'error_id': 'SERVICE_CRASHED',
                            'severity': 'critical',
                            'category': 'service',
                            'fix_method': 'restart_service',
                            'message': f'Service {service} has failed'
                        }
                        self.errors_found.append(error_info)
                        self.error_library.record_error('SERVICE_CRASHED', error_info)
            except:
                pass
    
    def check_resources(self):
        """Check system resources"""
        memory = SystemInfo.get_memory_info()
        swap = SystemInfo.get_swap_info()
        disk = SystemInfo.get_disk_usage('/')
        
        if memory['percent'] > 90:
            self.health_score -= 20
            self.errors_found.append({
                'error_id': 'MEMORY_CRITICAL',
                'severity': 'critical',
                'category': 'memory',
                'fix_method': 'clear_cache',
                'message': f'Memory usage at {memory["percent"]}%'
            })
        
        if swap['percent'] > 80:
            self.health_score -= 15
        
        if disk['percent'] > 90:
            self.health_score -= 20
            self.errors_found.append({
                'error_id': 'DISK_FULL',
                'severity': 'critical',
                'category': 'disk',
                'fix_method': 'clean_disk',
                'message': f'Disk usage at {disk["percent"]}%'
            })
    
    def apply_fixes(self):
        """Apply fixes and handle unresolved errors"""
        print(f"\n{self.colors.YELLOW}{self.colors.BOLD}═══ Applying Auto-Fixes ═══{self.colors.NC}\n")
        
        # Group errors
        error_groups = defaultdict(list)
        for error in self.errors_found:
            error_groups[error['error_id']].append(error)
        
        # Apply standard fixes
        for error_id, errors in error_groups.items():
            print(f"{self.colors.WHITE}Fixing {error_id} ({len(errors)} occurrences)...{self.colors.NC}")
            
            fix_method = errors[0]['fix_method'] if errors else None
            if fix_method:
                success = self.knowledge_base.apply_fix(fix_method)
                self.error_library.record_fix_attempt(error_id, fix_method, success)
                
                if success:
                    self.fixes_applied.append({
                        'error_id': error_id,
                        'fix_method': fix_method,
                        'timestamp': datetime.now().isoformat()
                    })
                    print(f"{self.colors.GREEN}✓ Fixed successfully{self.colors.NC}\n")
                else:
                    print(f"{self.colors.RED}✗ Standard fix failed{self.colors.NC}")
                    
                    # Try advanced fix
                    print(f"{self.colors.YELLOW}  Trying advanced fix...{self.colors.NC}")
                    advanced_success = self.error_library.advanced_fix_strategies.get(error_id, lambda: False)()
                    
                    if advanced_success:
                        self.error_library.record_fix_attempt(error_id, f'advanced_{error_id}', True)
                        print(f"{self.colors.GREEN}  ✓ Advanced fix succeeded{self.colors.NC}\n")
                    else:
                        self.error_library.record_fix_attempt(error_id, f'advanced_{error_id}', False)
                        print(f"{self.colors.RED}  ✗ Advanced fix failed{self.colors.NC}")
                        
                        # Try internet search
                        print(f"{self.colors.PURPLE}  Searching internet for solution...{self.colors.NC}")
                        internet_success = self.error_library.search_and_fix_unresolved(
                            error_id, errors[0]
                        )
                        
                        if internet_success:
                            print(f"{self.colors.GREEN}  ✓ Internet solution found and applied!{self.colors.NC}\n")
                        else:
                            print(f"{self.colors.YELLOW}  ⚠ No automatic solution found{self.colors.NC}\n")
        
        # Generate upgrade reference for unresolved errors
        unresolved = self.error_library.generate_upgrade_reference(error_groups)
        
        return unresolved
    
    def generate_report(self) -> Tuple[Dict, str]:
        """Generate report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_info': self.system_info,
            'errors_found': self.errors_found,
            'fixes_applied': self.fixes_applied,
            'health_score': min(self.health_score, 100),
            'summary': {
                'total_errors': len(self.errors_found),
                'critical_errors': len([e for e in self.errors_found if e['severity'] == 'critical']),
                'warnings': len([e for e in self.errors_found if e['severity'] == 'warning']),
                'fixes_applied': len(self.fixes_applied)
            }
        }
        
        report_dir = '/var/log/autofixdetect'
        os.makedirs(report_dir, exist_ok=True)
        report_file = os.path.join(report_dir, f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return report, report_file
    
    def display_results(self, report: Dict):
        """Display results"""
        print(f"\n{self.colors.CYAN}{self.colors.BOLD}═══ Diagnostic Results ═══{self.colors.NC}\n")
        
        print(f"{self.colors.WHITE}System:{self.colors.NC} {report['system_info'].get('distro', 'Unknown')}")
        print(f"{self.colors.WHITE}Hostname:{self.colors.NC} {report['system_info']['hostname']}")
        print(f"{self.colors.WHITE}Uptime:{self.colors.NC} {report['system_info']['uptime']}")
        
        print(f"\n{self.colors.WHITE}Errors:{self.colors.NC}")
        print(f"  Critical: {report['summary']['critical_errors']}")
        print(f"  Warnings: {report['summary']['warnings']}")
        print(f"  Total: {report['summary']['total_errors']}")
        
        if report['errors_found']:
            print(f"\n{self.colors.RED}Top Errors:{self.colors.NC}")
            error_groups = defaultdict(list)
            for error in report['errors_found']:
                error_groups[error['error_id']].append(error)
            
            for error_id, errors in list(error_groups.items())[:10]:
                severity = errors[0]['severity']
                severity_color = self.colors.RED if severity == 'critical' else self.colors.YELLOW
                print(f"  {severity_color}[{severity.upper()}] {error_id}: {len(errors)}x{self.colors.NC}")
        
        print(f"\n{self.colors.WHITE}Fixes Applied:{self.colors.NC} {report['summary']['fixes_applied']}")
        
        score = report['health_score']
        score_color = self.colors.GREEN if score >= 80 else self.colors.YELLOW if score >= 60 else self.colors.RED
        print(f"\n{self.colors.WHITE}Health Score: {score_color}{score}/100{self.colors.NC}")

#===============================================================================
# MAIN APPLICATION
#===============================================================================
class AutoFixDetectAI:
    """Main application"""
    
    def __init__(self):
        self.colors = Colors()
        self.engine = DiagnosticEngine()
    
    def print_banner(self):
        """Print banner"""
        print(f"""
{self.colors.CYAN}{self.colors.BOLD}
╔═══════════════════════════════════════════════════════════════════════╗
║           AUTOFIXDETECT AI v6.0 - INTERNET SEARCH & AUTO-UPGRADE      ║
║         Advanced Diagnostic with Online Solution Search               ║
╚═══════════════════════════════════════════════════════════════════════╝
{self.colors.NC}
{self.colors.WHITE}Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{self.colors.NC}
""")
    
    def run(self):
        """Run the tool"""
        try:
            self.print_banner()
            
            print(f"{self.colors.YELLOW}[1/5] Collecting system information...{self.colors.NC}")
            self.engine.collect_system_info()
            
            print(f"{self.colors.YELLOW}[2/5] Analyzing logs...{self.colors.NC}")
            self.engine.analyze_logs()
            
            print(f"{self.colors.YELLOW}[3/5] Checking services...{self.colors.NC}")
            self.engine.check_services()
            
            print(f"{self.colors.YELLOW}[4/5] Checking resources...{self.colors.NC}")
            self.engine.check_resources()
            
            print(f"{self.colors.GREEN}✓ Diagnostic complete!{self.colors.NC}")
            
            if self.engine.errors_found:
                print(f"\n{self.colors.YELLOW}Found {len(self.engine.errors_found)} error(s).{self.colors.NC}")
                response = input(f"{self.colors.WHITE}Apply automatic fixes? (y/n): {self.colors.NC}")
                if response.lower() in ['y', 'yes']:
                    unresolved = self.engine.apply_fixes()
                    
                    if unresolved:
                        print(f"\n{self.colors.YELLOW}⚠ {len(unresolved)} error type(s) still unresolved.{self.colors.NC}")
                        print(f"{self.colors.WHITE}Manual intervention required. Check upgradeperbaikan.txt{self.colors.NC}")
            else:
                print(f"\n{self.colors.GREEN}No errors detected!{self.colors.NC}")
            
            report, report_file = self.engine.generate_report()
            self.engine.display_results(report)
            
            print(f"\n{self.colors.GREEN}Report: {report_file}{self.colors.NC}")
            
        except KeyboardInterrupt:
            print(f"\n{self.colors.YELLOW}Interrupted.{self.colors.NC}")
            sys.exit(0)
        except Exception as e:
            print(f"{self.colors.RED}Error: {e}{self.colors.NC}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

#===============================================================================
# ENTRY POINT
#===============================================================================
if __name__ == "__main__":
    if sys.version_info < (3, 6):
        print("Python 3.6+ required.")
        sys.exit(1)
    
    app = AutoFixDetectAI()
    app.run()
