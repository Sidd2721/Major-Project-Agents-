import sys
import time
from Backend.worker import process_complaints

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print("🤖 LangGraph AI Worker started. Watching for complaints in real-time... (Press Ctrl+C to stop)")
    while True:
        try:
            process_complaints()
        except KeyboardInterrupt:
            print("\n🛑 Worker stopped.")
            break
        except Exception as e:
            print(f"⚠️ Worker error: {e}")
        time.sleep(3)