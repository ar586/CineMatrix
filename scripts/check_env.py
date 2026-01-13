import sys
import os

# Ensure we can import backend.config
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from backend import config
except ImportError:
    # If running from root
    sys.path.append(os.getcwd())
    from backend import config

def check_env():
    print("Checking environment variables...")
    missing = config.validate_config()
    
    if missing:
        print("\n❌ Missing critical environment variables:")
        for var in missing:
            print(f"   - {var}")
        print("\nPlease create a .env file based on .env.example and add these keys.")
        sys.exit(1)
    else:
        print("\n✅ All critical environment variables found!")
        print("Backend configuration is ready.")
        sys.exit(0)

if __name__ == "__main__":
    check_env()
