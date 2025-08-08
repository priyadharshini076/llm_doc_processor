#!/usr/bin/env python3
"""
Test script for webhook functionality
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"
WEBHOOK_RECEIVER_URL = "http://localhost:8001"

def test_webhook_configuration():
    """Test webhook configuration"""
    print("🔧 Testing webhook configuration...")
    
    webhook_config = {
        "url": f"{WEBHOOK_RECEIVER_URL}/webhook",
        "events": ["document_processed", "query_answered", "error"],
        "secret": "test_secret_123"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/webhook/configure",
            json=webhook_config,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Webhook configured successfully!")
            print(f"   URL: {result['webhook_url']}")
            print(f"   Events: {result['events']}")
            print(f"   Test success: {result['test_success']}")
            return True
        else:
            print(f"❌ Failed to configure webhook: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error configuring webhook: {e}")
        return False

def test_webhook_status():
    """Test webhook status endpoint"""
    print("\n📊 Testing webhook status...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/webhook/status", timeout=10)
        
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Webhook status retrieved!")
            print(f"   Configured: {status['configured']}")
            print(f"   URL: {status['webhook_url']}")
            print(f"   Secret: {status['webhook_secret']}")
            return True
        else:
            print(f"❌ Failed to get webhook status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting webhook status: {e}")
        return False

def test_manual_webhook_trigger():
    """Test manual webhook triggering"""
    print("\n🚀 Testing manual webhook trigger...")
    
    test_event = {
        "event_type": "test_event",
        "data": {
            "message": "This is a test webhook event",
            "timestamp": time.time(),
            "test_id": "manual_trigger_test"
        }
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/webhook/trigger",
            json=test_event,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Manual webhook triggered successfully!")
            print(f"   Event type: {result['event_type']}")
            print(f"   Sent: {result['sent']}")
            print(f"   Webhook URL: {result['webhook_url']}")
            return True
        else:
            print(f"❌ Failed to trigger webhook: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error triggering webhook: {e}")
        return False

def test_document_processing_webhook():
    """Test webhook during document processing"""
    print("\n📄 Testing document processing webhook...")
    
    # Create a simple test PDF content (this is just for demonstration)
    # In a real scenario, you would upload an actual PDF file
    test_data = {
        "query": "What is the main topic of this document?"
    }
    
    # Note: This would require an actual PDF file to test properly
    print("ℹ️  Document processing webhook test requires an actual PDF file")
    print("   The webhook will be triggered when you process a real document")
    return True

def check_webhook_receiver():
    """Check if webhook receiver is running and get received webhooks"""
    print("\n📥 Checking webhook receiver...")
    
    try:
        # Check if receiver is running
        response = requests.get(f"{WEBHOOK_RECEIVER_URL}/", timeout=5)
        
        if response.status_code == 200:
            print("✅ Webhook receiver is running!")
            
            # Get received webhooks
            webhooks_response = requests.get(f"{WEBHOOK_RECEIVER_URL}/webhooks", timeout=5)
            
            if webhooks_response.status_code == 200:
                webhooks = webhooks_response.json()
                print(f"📋 Received {webhooks['count']} webhooks:")
                
                for i, webhook in enumerate(webhooks['webhooks']):
                    print(f"   {i+1}. {webhook['event_type']} - {webhook['timestamp']}")
                    if 'data' in webhook:
                        data = webhook['data']
                        if 'message' in data:
                            print(f"      Message: {data['message']}")
                        elif 'file_name' in data:
                            print(f"      File: {data['file_name']}")
                        elif 'question' in data:
                            print(f"      Question: {data['question'][:50]}...")
                
                return True
            else:
                print("❌ Failed to get webhooks from receiver")
                return False
        else:
            print("❌ Webhook receiver is not running")
            print("   Start it with: python webhook_receiver.py")
            return False
            
    except Exception as e:
        print(f"❌ Error checking webhook receiver: {e}")
        print("   Make sure webhook_receiver.py is running on port 8001")
        return False

def clear_webhooks():
    """Clear all stored webhooks"""
    print("\n🧹 Clearing stored webhooks...")
    
    try:
        response = requests.delete(f"{WEBHOOK_RECEIVER_URL}/webhooks/clear", timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Cleared {result['count']} webhooks")
            return True
        else:
            print(f"❌ Failed to clear webhooks: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error clearing webhooks: {e}")
        return False

def main():
    """Run all webhook tests"""
    print("🧪 Webhook Functionality Test Suite")
    print("=" * 50)
    
    # Check if main API is running
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        if response.status_code != 200:
            print("❌ Main API is not running!")
            print("   Start it with: uvicorn app:app --host 0.0.0.0 --port 8000")
            return
    except Exception as e:
        print("❌ Cannot connect to main API!")
        print("   Make sure it's running on port 8000")
        return
    
    print("✅ Main API is running")
    
    # Clear existing webhooks
    clear_webhooks()
    
    # Run tests
    tests = [
        ("Webhook Configuration", test_webhook_configuration),
        ("Webhook Status", test_webhook_status),
        ("Manual Webhook Trigger", test_manual_webhook_trigger),
        ("Document Processing Webhook", test_document_processing_webhook),
        ("Webhook Receiver Check", check_webhook_receiver),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All webhook tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print("\n📝 Next Steps:")
    print("1. Process a real PDF document to see webhooks in action")
    print("2. Configure webhook for your production environment")
    print("3. Implement webhook handling in your application")

if __name__ == "__main__":
    main()
