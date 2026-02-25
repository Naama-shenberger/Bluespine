import os
from core.agent import run_agent
if __name__ == "__main__":
    os.makedirs("output_files", exist_ok=True)
    run_agent("input_files/rp-031.pdf")