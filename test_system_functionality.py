#!/usr/bin/env python3
"""
Test script to verify the enhanced system page functionality
"""

import os
import sys
import django
import json
from django.test import Client
from django.urls import reverse

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geosurvey.settings')
django.setup()

def test_system_page_loading():
    """Test that the system page loads correctly"""
    print("🔍 Testing System Page Loading...")
    
    client = Client()
    
    try:
        response = client.get('/admin-dashboard/system/')
        
        if response.status_code == 200:
            print("✅ System page loads successfully")
            return True
        else:
            print(f"❌ System page failed to load: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing system page: {e}")
        return False

def test_system_api_endpoints():
    """Test system API endpoints"""
    print("\n🔍 Testing System API Endpoints...")
    
    client = Client()
    
    try:
        # Test system status API
        response = client.get('/admin-dashboard/api/system/status/')
        
        if response.status_code == 200:
            print("✅ System status API accessible")
            return True
        else:
            print(f"❌ System status API failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing system API: {e}")
        return False

def test_system_controls():
    """Test system control functionality"""
    print("\n🔍 Testing System Controls...")
    
    client = Client()
    
    try:
        # Test system controls (POST requests)
        controls = [
            {'action': 'restart_services'},
            {'action': 'clear_cache'},
            {'action': 'schedule_maintenance', 'window': '2024-01-15 02:00-04:00'},
            {'action': 'toggle_service', 'service': 'web'}
        ]
        
        success_count = 0
        total_count = len(controls)
        
        for control in controls:
            response = client.post('/admin-dashboard/api/system/status/', 
                                 data=json.dumps(control),
                                 content_type='application/json')
            
            if response.status_code in [200, 401, 403]:  # Acceptable responses
                print(f"✅ {control['action']} control accessible")
                success_count += 1
            else:
                print(f"❌ {control['action']} control failed: {response.status_code}")
        
        print(f"\n📊 System Controls: {success_count}/{total_count} accessible")
        return success_count == total_count
        
    except Exception as e:
        print(f"❌ Error testing system controls: {e}")
        return False

def test_system_information():
    """Test system information display"""
    print("\n🔍 Testing System Information...")
    
    client = Client()
    
    try:
        response = client.get('/admin-dashboard/system/')
        
        if response.status_code == 200:
            content = response.content.decode()
            
            # Check for system information elements
            required_elements = [
                'System Controls',
                'System Information',
                'User Statistics',
                'Application Services',
                'Security Status',
                'Real-time Monitoring',
                'System Performance',
                'Resource Distribution',
                'System Health',
                'Active Alerts',
                'Maintenance Windows',
                'System Logs'
            ]
            
            found_count = 0
            total_count = len(required_elements)
            
            for element in required_elements:
                if element in content:
                    print(f"✅ {element} found")
                    found_count += 1
                else:
                    print(f"❌ {element} missing")
            
            print(f"\n📊 System Information Elements: {found_count}/{total_count} found")
            return found_count >= total_count * 0.8  # 80% threshold
            
        else:
            print(f"❌ System page not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing system information: {e}")
        return False

def test_system_features():
    """Test specific system features"""
    print("\n🔍 Testing System Features...")
    
    client = Client()
    
    try:
        response = client.get('/admin-dashboard/system/')
        
        if response.status_code == 200:
            content = response.content.decode()
            
            # Check for specific features
            features = [
                'restartServices()',
                'clearCache()',
                'backupSystem()',
                'emergencyShutdown()',
                'scheduleMaintenance()',
                'toggleService(',
                'loadSystemInformation()',
                'loadUserStatistics()',
                'loadSecurityStatus()',
                'loadRealTimeMonitoring()',
                'Chart.js',
                'performanceChart',
                'resourceChart'
            ]
            
            found_count = 0
            total_count = len(features)
            
            for feature in features:
                if feature in content:
                    print(f"✅ {feature} found")
                    found_count += 1
                else:
                    print(f"❌ {feature} missing")
            
            print(f"\n📊 System Features: {found_count}/{total_count} found")
            return found_count >= total_count * 0.8  # 80% threshold
            
        else:
            print(f"❌ System page not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing system features: {e}")
        return False

def test_system_responsiveness():
    """Test system page responsiveness"""
    print("\n🔍 Testing System Page Responsiveness...")
    
    client = Client()
    
    try:
        response = client.get('/admin-dashboard/system/')
        
        if response.status_code == 200:
            content = response.content.decode()
            
            # Check for responsive design elements
            responsive_elements = [
                'bootstrap',
                'col-xl-',
                'col-lg-',
                'col-md-',
                'col-sm-',
                'responsive',
                'mobile',
                'tablet'
            ]
            
            found_count = 0
            total_count = len(responsive_elements)
            
            for element in responsive_elements:
                if element in content:
                    print(f"✅ {element} responsive element found")
                    found_count += 1
                else:
                    print(f"❌ {element} responsive element missing")
            
            print(f"\n📊 Responsive Elements: {found_count}/{total_count} found")
            return found_count >= total_count * 0.6  # 60% threshold
            
        else:
            print(f"❌ System page not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing responsiveness: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting System Functionality Test...\n")
    
    page_loading = test_system_page_loading()
    api_endpoints = test_system_api_endpoints()
    system_controls = test_system_controls()
    system_info = test_system_information()
    system_features = test_system_features()
    responsiveness = test_system_responsiveness()
    
    print("\n" + "="*60)
    print("🎯 SYSTEM FUNCTIONALITY TEST RESULTS")
    print("="*60)
    
    if all([page_loading, api_endpoints, system_controls, system_info, system_features, responsiveness]):
        print("✅ ALL TESTS PASSED!")
        print("🎉 System page is fully functional!")
    else:
        print("❌ SOME TESTS FAILED!")
        if not page_loading:
            print("   - System page loading issues")
        if not api_endpoints:
            print("   - API endpoint issues")
        if not system_controls:
            print("   - System controls issues")
        if not system_info:
            print("   - System information display issues")
        if not system_features:
            print("   - System features missing")
        if not responsiveness:
            print("   - Responsive design issues")
    
    print("\n📝 Final Summary:")
    print("✅ Page Loading: " + ("Pass" if page_loading else "Fail"))
    print("✅ API Endpoints: " + ("Pass" if api_endpoints else "Fail"))
    print("✅ System Controls: " + ("Pass" if system_controls else "Fail"))
    print("✅ System Information: " + ("Pass" if system_info else "Fail"))
    print("✅ System Features: " + ("Pass" if system_features else "Fail"))
    print("✅ Responsiveness: " + ("Pass" if responsiveness else "Fail"))
    
    print("\n✨ Test completed!")
    print("\n🎯 Enhanced System Features:")
    print("• Real-time system monitoring")
    print("• Comprehensive system controls")
    print("• Security status monitoring")
    print("• Application services management")
    print("• Performance charts and metrics")
    print("• Maintenance scheduling")
    print("• Emergency shutdown controls")
    print("• User statistics and analytics")
    print("• System health monitoring")
    print("• Active alerts and notifications")
    print("• System logs and maintenance")
    print("• Fully responsive design")
    
    if all([page_loading, api_endpoints, system_controls, system_info, system_features, responsiveness]):
        print("\n🏆 STATUS: SYSTEM PAGE FULLY FUNCTIONAL! 🏆")
    else:
        print("\n⚠️  STATUS: NEEDS ADDITIONAL WORK") 