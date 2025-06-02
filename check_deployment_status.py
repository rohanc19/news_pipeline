"""
Real-time deployment status checker for Strapi on Render.
"""
import requests
import time
import json
from datetime import datetime

def check_strapi_status():
    """Check Strapi deployment status in real-time."""
    
    print("🚀 STRAPI DEPLOYMENT STATUS CHECKER")
    print("=" * 60)
    print("Repository: https://github.com/rohanc19/prediction-markets-strapi")
    print("Expected URL: https://prediction-markets-strapi.onrender.com")
    print()
    
    strapi_url = "https://prediction-markets-strapi.onrender.com"
    max_attempts = 20
    attempt = 1
    
    while attempt <= max_attempts:
        print(f"🔍 Attempt {attempt}/{max_attempts} - {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            # Test basic connectivity
            print("   📡 Testing service connectivity...")
            response = requests.get(f"{strapi_url}/api/prediction-markets", timeout=15)
            
            if response.status_code == 200:
                print("   ✅ SUCCESS! Strapi is fully operational!")
                data = response.json()
                market_count = len(data.get('data', []))
                print(f"   📊 Markets in database: {market_count}")
                
                # Test admin panel
                admin_response = requests.get(f"{strapi_url}/admin", timeout=10)
                if admin_response.status_code == 200:
                    print("   ✅ Admin panel is accessible")
                
                print(f"\n🎉 DEPLOYMENT SUCCESSFUL!")
                print(f"🔗 Admin Panel: {strapi_url}/admin")
                print(f"🔗 API Endpoint: {strapi_url}/api/prediction-markets")
                
                return True
                
            elif response.status_code == 403:
                print("   ✅ Service running! (API permissions need configuration)")
                print(f"   🔗 Configure at: {strapi_url}/admin")
                return True
                
            elif response.status_code == 404:
                print("   ⚠️ Service running but content type missing")
                print("   💡 This shouldn't happen with our pre-configured setup")
                
            elif response.status_code == 502 or response.status_code == 503:
                print("   ⏳ Service is starting up...")
                
            else:
                print(f"   ⚠️ Unexpected response: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("   ⏳ Service is starting (timeout - normal during startup)")
            
        except requests.exceptions.ConnectionError:
            print("   ⏳ Service not ready yet (connection refused)")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        if attempt < max_attempts:
            print("   ⏱️ Waiting 30 seconds before next check...")
            time.sleep(30)
        
        attempt += 1
    
    print(f"\n⚠️ Service not responding after {max_attempts} attempts")
    print("💡 Check Render dashboard for deployment status")
    return False

def print_troubleshooting_guide():
    """Print troubleshooting guide."""
    
    print("\n🔧 TROUBLESHOOTING GUIDE:")
    print("=" * 60)
    
    print("\n1️⃣ **Check Render Dashboard:**")
    print("   • Go to https://dashboard.render.com/")
    print("   • Find your 'prediction-markets-strapi' service")
    print("   • Check 'Logs' tab for build/runtime errors")
    print("   • Verify 'Events' tab for deployment status")
    
    print("\n2️⃣ **Common Issues & Solutions:**")
    print("   🔴 Build Failed:")
    print("      → Check if latest commit was pushed")
    print("      → Verify package.json has React dependencies")
    print("      → Try manual redeploy")
    
    print("   🔴 Service Won't Start:")
    print("      → Check environment variables are set")
    print("      → Verify JWT_SECRET is auto-generated")
    print("      → Check Node.js version compatibility")
    
    print("   🔴 Timeout/Connection Issues:")
    print("      → Wait longer (first deploy takes 5-10 minutes)")
    print("      → Check Render service region")
    print("      → Verify service is not sleeping (free tier)")
    
    print("\n3️⃣ **Manual Checks:**")
    print("   • Repository: https://github.com/rohanc19/prediction-markets-strapi")
    print("   • Render Dashboard: https://dashboard.render.com/")
    print("   • Expected URL: https://prediction-markets-strapi.onrender.com")
    
    print("\n4️⃣ **If All Else Fails:**")
    print("   • Delete and recreate the Render service")
    print("   • Ensure repository is public")
    print("   • Try deploying from a different branch")
    print("   • Contact Render support if persistent issues")

def main():
    """Main function."""
    
    success = check_strapi_status()
    
    if success:
        print("\n📋 NEXT STEPS:")
        print("1. Access admin panel and create admin account")
        print("2. Configure API permissions (Settings → Users & Permissions)")
        print("3. Create API token (Settings → API Tokens)")
        print("4. Update strapi_service.py with the new token")
        print("5. Test pipeline integration")
        
    else:
        print_troubleshooting_guide()
    
    print(f"\n💡 TIP: Run this script again anytime to check status")

if __name__ == "__main__":
    main()
