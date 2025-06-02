"""
Test script to verify Strapi integration is working correctly.
"""
import requests
import json
from datetime import datetime, timedelta

def test_strapi_connection():
    """Test basic connection to Strapi."""
    
    strapi_url = "https://prediction-markets-strapi.onrender.com"
    
    print("🔍 Testing Strapi Integration...")
    print("=" * 50)
    
    # Test 1: Check if Strapi is running
    print("1️⃣ Testing Strapi Service Status...")
    try:
        response = requests.get(f"{strapi_url}/api/prediction-markets", timeout=10)
        if response.status_code == 200:
            print("   ✅ Strapi service is running")
            data = response.json()
            print(f"   📊 Current markets in database: {len(data.get('data', []))}")
        elif response.status_code == 404:
            print("   ❌ Content type 'prediction-markets' not found")
            print("   💡 Please create the content type first (see Step 3)")
            return False
        else:
            print(f"   ❌ Unexpected response: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Connection failed: {str(e)}")
        return False
    
    # Test 2: Try to create a test market
    print("\n2️⃣ Testing Market Creation...")
    
    # Sample market data
    test_market = {
        "data": {
            "title": "Test Market: Will this integration work?",
            "description": "This is a test market to verify Strapi integration is working correctly.",
            "category": "Tech",
            "tags": ["Test", "Integration", "Strapi"],
            "status": "open",
            "endTime": (datetime.now() + timedelta(days=30)).isoformat(),
            "resolutionTime": (datetime.now() + timedelta(days=30)).isoformat(),
            "yesCount": 50000,
            "noCount": 50000,
            "totalVolume": 100000,
            "currentYesProbability": 0.5,
            "currentNoProbability": 0.5,
            "creatorId": "test-integration",
            "resolutionSource": "https://example.com/test",
            "marketId": f"test_market_{int(datetime.now().timestamp())}"
        }
    }
    
    try:
        response = requests.post(
            f"{strapi_url}/api/prediction-markets",
            json=test_market,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print("   ✅ Test market created successfully!")
            market_data = response.json()
            market_id = market_data.get('data', {}).get('id')
            print(f"   📝 Market ID: {market_id}")
            return True
        elif response.status_code == 403:
            print("   ❌ Permission denied - API permissions not set correctly")
            print("   💡 Please configure API permissions (see Step 5)")
            return False
        elif response.status_code == 400:
            print("   ❌ Bad request - Content type fields may be incorrect")
            print(f"   📄 Response: {response.text}")
            return False
        else:
            print(f"   ❌ Failed to create market: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Request failed: {str(e)}")
        return False

def test_pipeline_integration():
    """Test the actual pipeline integration."""
    
    print("\n3️⃣ Testing Pipeline Integration...")
    
    # Import and test the Strapi service
    try:
        from strapi_service import StrapiService
        
        strapi_service = StrapiService()
        
        # Test market data (same format as pipeline generates)
        test_market = {
            "id": f"test_pipeline_{int(datetime.now().timestamp())}",
            "title": "Test Pipeline Market: Will the news pipeline work correctly?",
            "description": "This market tests the complete pipeline integration with Strapi CMS.",
            "category": "Tech",
            "tags": ["Pipeline", "Integration", "News"],
            "status": "open",
            "createdAt": datetime.now().isoformat(),
            "startTime": datetime.now().isoformat(),
            "endTime": (datetime.now() + timedelta(days=30)).isoformat(),
            "resolutionTime": (datetime.now() + timedelta(days=30)).isoformat(),
            "result": None,
            "yesCount": 50000,
            "noCount": 50000,
            "totalVolume": 100000,
            "currentYesProbability": 0.5,
            "currentNoProbability": 0.5,
            "creatorId": "kalshi-generator",
            "resolutionSource": "https://example.com/pipeline-test"
        }
        
        # Test pushing to Strapi
        success = strapi_service.push_market_to_strapi(test_market)
        
        if success:
            print("   ✅ Pipeline integration test successful!")
            print("   🎉 Your pipeline can now push markets to Strapi!")
            return True
        else:
            print("   ❌ Pipeline integration test failed")
            print("   💡 Check the API token in strapi_service.py")
            return False
            
    except ImportError as e:
        print(f"   ❌ Import error: {str(e)}")
        return False
    except Exception as e:
        print(f"   ❌ Integration test failed: {str(e)}")
        return False

def print_setup_checklist():
    """Print setup checklist."""
    
    print("\n📋 STRAPI SETUP CHECKLIST:")
    print("=" * 50)
    print("□ 1. Strapi deployed on Render")
    print("□ 2. Admin account created")
    print("□ 3. Content type 'prediction-market' created with all fields")
    print("□ 4. API token generated")
    print("□ 5. API permissions configured for Public role")
    print("□ 6. API token updated in strapi_service.py")
    print("□ 7. Integration tests passing")
    
    print("\n🔗 USEFUL LINKS:")
    print("• Strapi Admin: https://prediction-markets-strapi.onrender.com/admin")
    print("• API Endpoint: https://prediction-markets-strapi.onrender.com/api/prediction-markets")
    print("• Content Type Builder: Admin → Content-Type Builder")
    print("• API Tokens: Admin → Settings → API Tokens")
    print("• Permissions: Admin → Settings → Users & Permissions → Roles → Public")

if __name__ == "__main__":
    print_setup_checklist()
    print("\n" + "="*50)
    
    # Run tests
    basic_test = test_strapi_connection()
    
    if basic_test:
        pipeline_test = test_pipeline_integration()
        
        if pipeline_test:
            print("\n🎉 ALL TESTS PASSED!")
            print("Your Strapi integration is ready for production!")
        else:
            print("\n⚠️ Basic connection works, but pipeline integration needs fixing")
    else:
        print("\n❌ Basic connection failed - please complete Strapi setup first")
    
    print("\n💡 If tests fail, follow the setup steps in STRAPI_INTEGRATION_GUIDE.md")
