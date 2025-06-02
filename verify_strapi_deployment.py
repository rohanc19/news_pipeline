"""
Verification script to test Strapi deployment after it's live on Render.
"""
import requests
import json
from datetime import datetime, timedelta

def test_strapi_deployment():
    """Test the deployed Strapi instance."""
    
    print("🔍 Testing Strapi Deployment...")
    print("=" * 50)
    
    strapi_url = "https://prediction-markets-strapi.onrender.com"
    
    # Test 1: Check if Strapi is running
    print("1️⃣ Testing Strapi Service Status...")
    try:
        response = requests.get(f"{strapi_url}/api/prediction-markets", timeout=15)
        
        if response.status_code == 200:
            print("   ✅ Strapi service is running!")
            data = response.json()
            market_count = len(data.get('data', []))
            print(f"   📊 Markets in database: {market_count}")
            
        elif response.status_code == 403:
            print("   ⚠️ Service running but API permissions not set")
            print("   💡 Need to configure API permissions in admin panel")
            return "permissions_needed"
            
        elif response.status_code == 404:
            print("   ❌ Content type not found - this shouldn't happen!")
            print("   💡 Content type should be pre-configured")
            return "content_type_missing"
            
        else:
            print(f"   ❌ Unexpected response: {response.status_code}")
            print(f"   📄 Response: {response.text[:200]}...")
            return "unexpected_error"
            
    except requests.exceptions.Timeout:
        print("   ⏳ Service is starting up (this is normal on first deploy)")
        print("   💡 Render services take 1-2 minutes to start")
        return "starting_up"
        
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to Strapi service")
        print("   💡 Check if deployment completed successfully")
        return "connection_failed"
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return "error"
    
    # Test 2: Check admin panel accessibility
    print("\n2️⃣ Testing Admin Panel Access...")
    try:
        response = requests.get(f"{strapi_url}/admin", timeout=10)
        if response.status_code == 200:
            print("   ✅ Admin panel is accessible")
            print(f"   🔗 Admin URL: {strapi_url}/admin")
        else:
            print(f"   ⚠️ Admin panel response: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Admin panel test failed: {str(e)}")
    
    # Test 3: Try to create a test market (will fail without API token, but tests endpoint)
    print("\n3️⃣ Testing Market Creation Endpoint...")
    test_market = {
        "data": {
            "title": "Test Market: Strapi Integration Working?",
            "description": "This is a test market to verify the integration is working.",
            "category": "Tech",
            "tags": ["Test", "Integration"],
            "status": "open",
            "endTime": (datetime.now() + timedelta(days=30)).isoformat(),
            "resolutionTime": (datetime.now() + timedelta(days=30)).isoformat(),
            "yesCount": 50000,
            "noCount": 50000,
            "totalVolume": 100000,
            "currentYesProbability": 0.5,
            "currentNoProbability": 0.5,
            "creatorId": "test-deployment",
            "resolutionSource": "https://example.com/test",
            "marketId": f"test_deployment_{int(datetime.now().timestamp())}"
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
            print("   ✅ Market creation endpoint working!")
            print("   🎉 API is fully functional!")
            return "fully_working"
            
        elif response.status_code == 403:
            print("   ⚠️ Endpoint working but needs API permissions")
            print("   💡 Configure permissions in admin panel")
            return "needs_permissions"
            
        elif response.status_code == 401:
            print("   ⚠️ Endpoint working but needs authentication")
            print("   💡 Create API token in admin panel")
            return "needs_token"
            
        else:
            print(f"   ❌ Unexpected response: {response.status_code}")
            print(f"   📄 Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Market creation test failed: {str(e)}")
    
    return "basic_working"

def print_next_steps(status):
    """Print next steps based on test results."""
    
    print(f"\n📋 NEXT STEPS:")
    print("=" * 50)
    
    if status == "starting_up":
        print("⏳ **Strapi is starting up**")
        print("   • Wait 2-3 minutes for service to fully start")
        print("   • Run this test again")
        print("   • Check Render service logs if it takes longer")
        
    elif status == "connection_failed":
        print("❌ **Deployment Issue**")
        print("   • Check Render dashboard for deployment status")
        print("   • Verify repository is connected correctly")
        print("   • Check service logs for errors")
        
    elif status == "permissions_needed" or status == "needs_permissions":
        print("🔧 **Configure API Permissions**")
        print(f"   1. Go to: https://prediction-markets-strapi.onrender.com/admin")
        print("   2. Create admin account (first time)")
        print("   3. Go to Settings → Users & Permissions → Roles → Public")
        print("   4. Enable permissions for prediction-market:")
        print("      ✅ find, findOne, create, update")
        print("   5. Save changes")
        
    elif status == "needs_token":
        print("🔑 **Create API Token**")
        print(f"   1. Go to: https://prediction-markets-strapi.onrender.com/admin")
        print("   2. Go to Settings → API Tokens")
        print("   3. Create new token with full access")
        print("   4. Copy token and update strapi_service.py")
        
    elif status == "fully_working":
        print("🎉 **Strapi is fully working!**")
        print("   ✅ Service running")
        print("   ✅ Admin panel accessible")
        print("   ✅ API endpoints working")
        print("   ✅ Ready for pipeline integration")
        
    elif status == "basic_working":
        print("✅ **Strapi is working - needs final configuration**")
        print("   1. Configure API permissions (see above)")
        print("   2. Create API token (see above)")
        print("   3. Test pipeline integration")
        
    print(f"\n🔗 **Important URLs:**")
    print("   • Admin Panel: https://prediction-markets-strapi.onrender.com/admin")
    print("   • API Endpoint: https://prediction-markets-strapi.onrender.com/api/prediction-markets")
    print("   • Render Dashboard: https://dashboard.render.com/")

def main():
    """Main function."""
    
    print("🚀 STRAPI DEPLOYMENT VERIFICATION")
    print("=" * 50)
    print("Testing your deployed Strapi instance...")
    print("Repository: https://github.com/rohanc19/prediction-markets-strapi")
    print()
    
    status = test_strapi_deployment()
    print_next_steps(status)
    
    print(f"\n💡 **Remember:**")
    print("   • First deployment takes 2-3 minutes to start")
    print("   • Admin account creation is required on first visit")
    print("   • API permissions must be configured manually")
    print("   • API token needed for pipeline integration")

if __name__ == "__main__":
    main()
