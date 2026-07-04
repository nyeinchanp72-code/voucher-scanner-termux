import os
import subprocess
import sys

def setup_so():
    if not os.path.exists("termux_code_chee_fixed.so"):
        # Check if the .so exists with architecture suffix
        so_files = [f for f in os.listdir('.') if f.startswith('termux_code_chee_fixed') and f.endswith('.so')]
        if so_files:
            return

        print("First time setup: Compiling and securing code...")
        try:
            # Compile using setup.py
            subprocess.run([sys.executable, "setup.py", "build_ext", "--inplace"], check=True)
            # Remove original source code and build artifacts to protect it
            if os.path.exists("termux_code_chee_fixed.py"):
                os.remove("termux_code_chee_fixed.py")
            if os.path.exists("termux_code_chee_fixed.c"):
                os.remove("termux_code_chee_fixed.c")
            print("Setup complete! Code is now secured.")
        except Exception as e:
            print(f"Setup failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    setup_so()
    import termux_code_chee_fixed
    import asyncio
    try:
        asyncio.run(termux_code_chee_fixed.main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}")
