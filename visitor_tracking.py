"""
Visitor Tracking Module
Handles IP-based visitor analytics with S3 storage
"""

import os
import json
import boto3
from datetime import datetime, timedelta
from user_agents import parse


class VisitorTracker:
    """Handles visitor tracking and analytics"""

    def __init__(self, s3_bucket='mail.dustinreed.info', s3_key='visitor_count.json'):
        self.S3_BUCKET = s3_bucket
        self.VISITOR_COUNT_KEY = s3_key

        # Initialize S3 client
        try:
            self.s3_client = boto3.client('s3')
        except Exception as e:
            print(f"Warning: Could not initialize S3 client: {e}")
            self.s3_client = None

    def parse_user_agent(self, user_agent_string):
        """Parse user agent string and return device/browser info"""
        if not user_agent_string:
            return {
                'browser': 'Unknown',
                'browser_version': 'Unknown',
                'os': 'Unknown',
                'os_version': 'Unknown',
                'device': 'Unknown',
                'device_brand': 'Unknown',
                'device_model': 'Unknown',
                'is_mobile': False,
                'is_tablet': False,
                'is_pc': True,
                'is_bot': False
            }

        # Handle test/development user agents
        if 'werkzeug' in user_agent_string.lower() or 'test' in user_agent_string.lower():
            return {
                'browser': 'Test Client',
                'browser_version': 'N/A',
                'os': 'Development',
                'os_version': 'N/A',
                'device': 'Server',
                'device_brand': 'Unknown',
                'device_model': 'Unknown',
                'is_mobile': False,
                'is_tablet': False,
                'is_pc': False,
                'is_bot': False
            }

        try:
            ua = parse(user_agent_string)

            # Improve device detection
            device_family = ua.device.family if ua.device.family else 'Unknown'
            if device_family == 'Other' and ua.is_mobile:
                device_family = 'Mobile'
            elif device_family == 'Other' and ua.is_tablet:
                device_family = 'Tablet'
            elif device_family == 'Other' and ua.is_pc:
                device_family = 'Desktop'
            elif device_family == 'Other' and not ua.is_mobile and not ua.is_tablet and not ua.is_pc:
                device_family = 'Desktop'  # Default assumption

            return {
                'browser': ua.browser.family if ua.browser.family else 'Unknown',
                'browser_version': str(ua.browser.version_string) if ua.browser.version_string else 'Unknown',
                'os': ua.os.family if ua.os.family else 'Unknown',
                'os_version': str(ua.os.version_string) if ua.os.version_string else 'Unknown',
                'device': device_family,
                'device_brand': ua.device.brand if ua.device.brand else 'Unknown',
                'device_model': ua.device.model if ua.device.model else 'Unknown',
                'is_mobile': ua.is_mobile,
                'is_tablet': ua.is_tablet,
                'is_pc': ua.is_pc,
                'is_bot': ua.is_bot
            }
        except Exception as e:
            print(f"Warning: Could not parse user agent '{user_agent_string}': {e}")
            return {
                'browser': 'Unknown',
                'browser_version': 'Unknown',
                'os': 'Unknown',
                'os_version': 'Unknown',
                'device': 'Unknown',
                'device_brand': 'Unknown',
                'device_model': 'Unknown',
                'is_mobile': False,
                'is_tablet': False,
                'is_pc': True,
                'is_bot': False
            }

    def load_visitor_data(self):
        """Load visitor data from S3 with IP tracking"""
        if not self.s3_client:
            return {
                'unique_visitors': 0,
                'total_pageviews': 0,
                'monthly': {},
                'daily': {},
                'ips': {}
            }

        try:
            response = self.s3_client.get_object(Bucket=self.S3_BUCKET, Key=self.VISITOR_COUNT_KEY)
            body = response['Body']
            content = body.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            data = json.loads(content)

            # Ensure all fields exist for backward compatibility
            if not isinstance(data, dict):
                # Convert old simple count to new format
                data = {
                    'unique_visitors': data if isinstance(data, int) else 0,
                    'total_pageviews': data if isinstance(data, int) else 0
                }
            elif 'count' in data and 'unique_visitors' not in data:
                # Handle old format: {"count": 1}
                data = {
                    'unique_visitors': data.get('count', 0),
                    'total_pageviews': data.get('count', 0)
                }

            # Initialize new fields if missing
            data.setdefault('unique_visitors', 0)
            data.setdefault('total_pageviews', 0)
            data.setdefault('monthly', {})
            data.setdefault('daily', {})
            data.setdefault('ips', {})

            # Ensure monthly/daily have proper structure
            for period in data.get('monthly', {}):
                if not isinstance(data['monthly'][period], dict):
                    data['monthly'][period] = {'unique_visitors': data['monthly'][period], 'pageviews': data['monthly'][period]}

            for period in data.get('daily', {}):
                if not isinstance(data['daily'][period], dict):
                    data['daily'][period] = {'unique_visitors': data['daily'][period], 'pageviews': data['daily'][period]}

            return data
        except self.s3_client.exceptions.NoSuchKey:
            return {
                'unique_visitors': 0,
                'total_pageviews': 0,
                'monthly': {},
                'daily': {},
                'ips': {}
            }
        except Exception as e:
            print(f"Warning: Could not load visitor data from S3: {e}")
            return {
                'unique_visitors': 0,
                'total_pageviews': 0,
                'monthly': {},
                'daily': {},
                'ips': {}
            }

    def save_visitor_data(self, data):
        """Save visitor data to S3"""
        if not self.s3_client:
            return

        try:
            json_string = json.dumps(data)
            self.s3_client.put_object(
                Bucket=self.S3_BUCKET,
                Key=self.VISITOR_COUNT_KEY,
                Body=json_string,
                ContentType='application/json'
            )
        except Exception as e:
            print(f"Warning: Could not save visitor data to S3: {e}")

    def track_visitor(self, client_ip, user_agent_string=None):
        """Track a visitor with IP-based counting and user agent analysis"""
        if not client_ip:
            return

        # Parse user agent
        user_agent_info = self.parse_user_agent(user_agent_string)

        # Get current date info
        now = datetime.now()
        current_month = now.strftime('%Y-%m')
        current_day = now.strftime('%Y-%m-%d')

        # Load existing data
        visitor_data = self.load_visitor_data()
        # Track IP visits
        if client_ip not in visitor_data['ips']:
            visitor_data['ips'][client_ip] = {
                'first_visit': now.isoformat(),
                'visit_count': 0,
                'last_visit': now.isoformat(),
                'user_agent': user_agent_info,
                'user_agents': [user_agent_info]  # Track all user agents used
            }
            # New unique visitor
            visitor_data['unique_visitors'] += 1
        else:
            # Always update to the most recent user agent
            visitor_data['ips'][client_ip]['user_agent'] = user_agent_info

            # Track user agent history (avoid duplicates)
            existing_uas = visitor_data['ips'][client_ip].get('user_agents', [])
            ua_signature = f"{user_agent_info['browser']}_{user_agent_info['os']}_{user_agent_info['device']}"

            # Check if this user agent combination is already tracked
            ua_exists = False
            for existing_ua in existing_uas:
                try:
                    existing_signature = f"{existing_ua.get('browser', 'Unknown')}_{existing_ua.get('os', 'Unknown')}_{existing_ua.get('device', 'Unknown')}"
                    if existing_signature == ua_signature:
                        ua_exists = True
                        break
                except (KeyError, TypeError):
                    # Skip malformed user agent entries
                    continue

            if not ua_exists:
                existing_uas.append(user_agent_info)

            visitor_data['ips'][client_ip]['user_agents'] = existing_uas

        # Update IP data
        visitor_data['ips'][client_ip]['visit_count'] += 1
        visitor_data['ips'][client_ip]['last_visit'] = now.isoformat()

        # Increment total pageviews
        visitor_data['total_pageviews'] += 1

        # Handle monthly tracking
        if current_month not in visitor_data['monthly']:
            visitor_data['monthly'][current_month] = {
                'unique_visitors': 0,
                'pageviews': 0,
                'ips': {},
                'browsers': {},
                'os': {},
                'devices': {}
            }

        # Check if this IP is new for this month
        if client_ip not in visitor_data['monthly'][current_month]['ips']:
            visitor_data['monthly'][current_month]['unique_visitors'] += 1
            visitor_data['monthly'][current_month]['ips'][client_ip] = True

        visitor_data['monthly'][current_month]['pageviews'] += 1

        # Track browser stats for this month
        browser = user_agent_info['browser']
        if browser not in visitor_data['monthly'][current_month]['browsers']:
            visitor_data['monthly'][current_month]['browsers'][browser] = 0
        visitor_data['monthly'][current_month]['browsers'][browser] += 1

        # Track OS stats for this month
        os_name = user_agent_info['os']
        if os_name not in visitor_data['monthly'][current_month]['os']:
            visitor_data['monthly'][current_month]['os'][os_name] = 0
        visitor_data['monthly'][current_month]['os'][os_name] += 1

        # Track device stats for this month
        device = user_agent_info['device']
        if device not in visitor_data['monthly'][current_month]['devices']:
            visitor_data['monthly'][current_month]['devices'][device] = 0
        visitor_data['monthly'][current_month]['devices'][device] += 1

        # Handle daily tracking
        if current_day not in visitor_data['daily']:
            visitor_data['daily'][current_day] = {
                'unique_visitors': 0,
                'pageviews': 0,
                'ips': {},
                'browsers': {},
                'os': {},
                'devices': {}
            }

        # Check if this IP is new for this day
        if client_ip not in visitor_data['daily'][current_day]['ips']:
            visitor_data['daily'][current_day]['unique_visitors'] += 1
            visitor_data['daily'][current_day]['ips'][client_ip] = True

        visitor_data['daily'][current_day]['pageviews'] += 1

        # Track browser stats for this day
        if browser not in visitor_data['daily'][current_day]['browsers']:
            visitor_data['daily'][current_day]['browsers'][browser] = 0
        visitor_data['daily'][current_day]['browsers'][browser] += 1

        # Track OS stats for this day
        if os_name not in visitor_data['daily'][current_day]['os']:
            visitor_data['daily'][current_day]['os'][os_name] = 0
        visitor_data['daily'][current_day]['os'][os_name] += 1

        # Track device stats for this day
        if device not in visitor_data['daily'][current_day]['devices']:
            visitor_data['daily'][current_day]['devices'][device] = 0
        visitor_data['daily'][current_day]['devices'][device] += 1

        # Save updated data
        self.save_visitor_data(visitor_data)

    def get_stats_for_api(self):
        """Get visitor statistics for JSON API"""
        visitor_data = self.load_visitor_data()

        # Calculate last month's stats
        now = datetime.now()
        current_month = now.strftime('%Y-%m')
        last_month = (now.replace(day=1) - timedelta(days=1)).strftime('%Y-%m')

        current_month_data = visitor_data['monthly'].get(current_month, {'unique_visitors': 0, 'pageviews': 0})
        last_month_data = visitor_data['monthly'].get(last_month, {'unique_visitors': 0, 'pageviews': 0})

        # Get recent daily stats (last 7 days)
        recent_daily = {}
        for i in range(7):
            day = (now - timedelta(days=i)).strftime('%Y-%m-%d')
            day_data = visitor_data['daily'].get(day, {'unique_visitors': 0, 'pageviews': 0})
            recent_daily[day] = day_data

        # Get top IPs by visit count
        top_ips = sorted(
            visitor_data['ips'].items(),
            key=lambda x: x[1]['visit_count'],
            reverse=True
        )[:10]  # Top 10 IPs

        # Convert to ordered dict to preserve sorting
        top_ips_dict = {}
        for ip, data in top_ips:
            top_ips_dict[ip] = data

        return {
            'unique_visitors': visitor_data['unique_visitors'],
            'total_pageviews': visitor_data['total_pageviews'],
            'current_month': {
                'period': current_month,
                'unique_visitors': current_month_data.get('unique_visitors', 0),
                'pageviews': current_month_data.get('pageviews', 0)
            },
            'last_month': {
                'period': last_month,
                'unique_visitors': last_month_data.get('unique_visitors', 0),
                'pageviews': last_month_data.get('pageviews', 0)
            },
            'recent_daily': recent_daily,
            'monthly_breakdown': visitor_data['monthly'],
            'top_ips': top_ips_dict,
            'total_ips_tracked': len(visitor_data['ips']),
            'storage': f'S3 ({self.S3_BUCKET})',
            'status': 'success'
        }

    def get_stats_for_template(self):
        """Get visitor statistics formatted for HTML template"""
        visitor_data = self.load_visitor_data()
        # Calculate last month's stats
        now = datetime.now()
        current_month = now.strftime('%Y-%m')
        last_month = (now.replace(day=1) - timedelta(days=1)).strftime('%Y-%m')

        current_month_data = visitor_data['monthly'].get(current_month, {'unique_visitors': 0, 'pageviews': 0})
        last_month_data = visitor_data['monthly'].get(last_month, {'unique_visitors': 0, 'pageviews': 0})

        # Get recent daily stats (last 7 days) - chronological order
        recent_daily = []
        for i in range(6, -1, -1):  # Show in chronological order (oldest to newest)
            day = (now - timedelta(days=i)).strftime('%Y-%m-%d')
            day_data = visitor_data['daily'].get(day, {'unique_visitors': 0, 'pageviews': 0})
            recent_daily.append({
                'date': day,
                'unique_visitors': day_data.get('unique_visitors', 0),
                'pageviews': day_data.get('pageviews', 0)
            })

        # Get top IPs by visit count
        top_ips = sorted(
            visitor_data['ips'].items(),
            key=lambda x: x[1]['visit_count'],
            reverse=True
        )[:10]  # Top 10 IPs
        # Format top IPs for template
        formatted_top_ips = []
        for ip, data in top_ips:
            formatted_top_ips.append({
                'ip': ip,
                'visit_count': data['visit_count'],
                'first_visit': data['first_visit'][:10],  # Just date part
                'last_visit': data['last_visit'][:10],     # Just date part
                'browser': data.get('user_agent', {}).get('browser', 'Unknown'),
                'os': data.get('user_agent', {}).get('os', 'Unknown'),
                'device': data.get('user_agent', {}).get('device', 'Unknown'),
                'user_agents': data.get('user_agents', [])  # Include full user agents list
            })

        # Get browser, OS, and device analytics for current month
        current_browsers = current_month_data.get('browsers', {})
        current_os = current_month_data.get('os', {})
        current_devices = current_month_data.get('devices', {})

        return {
            'visitor_data': visitor_data,
            'current_month': current_month_data,
            'last_month': last_month_data,
            'recent_daily': recent_daily,
            'top_ips': formatted_top_ips,
            'current_month_period': current_month,
            'last_month_period': last_month,
            'browsers': current_browsers,
            'os_stats': current_os,
            'devices': current_devices
        }


# Global tracker instance
tracker = VisitorTracker()
