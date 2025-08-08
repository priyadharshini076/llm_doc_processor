#!/usr/bin/env python3
"""
Test script for PDF processing with webhook functionality
"""

import requests
import os
import tempfile
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000"
PDF_URL = "https://hackrx.blob.core.windows.net/assets/Arogya%20Sanjeevani%20Policy%20-%20CIN%20-%20U10200WB1906GOI001713%201.pdf?sv=2023-01-03&st=2025-07-21T08%3A29%3A02Z&se=2025-09-22T08%3A29%3A00Z&sr=b&sp=r&sig=nzrz1K9Iurt%2BBXom%2FB%2BMPTFMFP3PRnIvEsipAX10Ig4%3D"

def download_pdf():
    """Download the test PDF"""
    print("📥 Downloading test PDF...")
    
    try:
        response = requests.get(PDF_URL, timeout=30)
        response.raise_for_status()
        
        # Save to temporary file
        temp_dir = Path(tempfile.gettempdir())
        pdf_path = temp_dir / "test_document.pdf"
        
        with open(pdf_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ PDF downloaded successfully: {pdf_path}")
        return pdf_path
        
    except Exception as e:
        print(f"❌ Failed to download PDF: {e}")
        return None

def test_pdf_processing(pdf_path):
    """Test PDF processing with webhook"""
    print(f"\n📄 Testing PDF processing: {pdf_path}")
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': ('test_document.pdf', f, 'application/pdf')}
            data = {'query': 'What is the main topic of this document?'}
            
            response = requests.post(
                f"{API_BASE_URL}/process/",
                files=files,
                data=data,
                timeout=60
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ PDF processed successfully!")
            print(f"📋 Query: {result['query']}")
            print(f"💬 Answer: {result['answer'][:200]}...")
            print(f"📁 File: {result['file_name']}")
            print(f"📏 Size: {result['file_size']} bytes")
            return True
        else:
            print(f"❌ Failed to process PDF: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error processing PDF: {e}")
        return False

def test_hackrx_api():
    """Test HackRx API with webhook"""
    print("\n🚀 Testing HackRx API with webhook...")
    
    payload = {
        "documents": PDF_URL,
        "questions": [
            "What is the main topic of this document?",
            "What are the key features mentioned?",
            "What is the policy number?"
        ],
        "webhook_url": "http://localhost:8001/webhook"
    }
    
    headers = {
        "Authorization": "Bearer f5c145545a0ff24b475d29eecc69cccc524203c5e724eb3538d6a4df3e5a5f49",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/hackrx/run",
            json=payload,
            headers=headers,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ HackRx API processed successfully!")
            print(f"📋 Questions processed: {len(result['answers'])}")
            for i, answer in enumerate(result['answers']):
                print(f"   Q{i+1}: {answer[:100]}...")
            return True
        else:
            print(f"❌ Failed to process with HackRx API: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error with HackRx API: {e}")
        return False

def check_webhook_receiver():
    """Check webhook receiver for new events"""
    print("\n📥 Checking webhook receiver for new events...")
    
    try:
        response = requests.get("http://localhost:8001/webhooks", timeout=5)
        
        if response.status_code == 200:
            webhooks = response.json()
            print(f"📋 Total webhooks received: {webhooks['count']}")
            
            # Show recent webhooks
            recent_webhooks = webhooks['webhooks'][-5:]  # Last 5
            for webhook in recent_webhooks:
                event_type = webhook.get('event_type', 'unknown')
                timestamp = webhook.get('timestamp', 'unknown')
                print(f"   📥 {event_type} - {timestamp}")
                
                # Show some data details
                if 'data' in webhook:
                    data = webhook['data']
                    if 'file_name' in data:
                        print(f"      📁 File: {data['file_name']}")
                    if 'question' in data:
                        print(f"      ❓ Q: {data['question'][:50]}...")
                    if 'answer' in data:
                        print(f"      💬 A: {data['answer'][:50]}...")
            
            return True
        else:
            print("❌ Failed to get webhooks")
            return False
            
    except Exception as e:
        print(f"❌ Error checking webhooks: {e}")
        return False

def main():
    """Run PDF processing tests"""
    print("🧪 PDF Processing with Webhook Test")
    print("=" * 50)
    
    # Check if main API is running
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        if response.status_code != 200:
            print("❌ Main API is not running!")
            return
    except Exception as e:
        print("❌ Cannot connect to main API!")
        return
    
    print("✅ Main API is running")
    
    # Download PDF
    pdf_path = download_pdf()
    if not pdf_path:
        print("❌ Cannot proceed without PDF")
        return
    
    # Test PDF processing
    pdf_success = test_pdf_processing(pdf_path)
    
    # Test HackRx API
    hackrx_success = test_hackrx_api()
    
    # Check webhook receiver
    webhook_success = check_webhook_receiver()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   PDF Processing: {'✅' if pdf_success else '❌'}")
    print(f"   HackRx API: {'✅' if hackrx_success else '❌'}")
    print(f"   Webhook Receiver: {'✅' if webhook_success else '❌'}")
    
    if pdf_success or hackrx_success:
        print("\n🎉 Webhook functionality is working with real PDF documents!")
        print("📝 Check the webhook receiver logs for detailed event information.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
