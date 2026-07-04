import asyncio
import termux_code_chee_fixed

if __name__ == "__main__":
    try:
        asyncio.run(termux_code_chee_fixed.main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}")
