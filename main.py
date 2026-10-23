#!/usr/bin/env python3
"""EdgeInfer - AI Model Deployment for Edge Devices"""

import sys
from src.cli import cli
from src.llm import LLMError

if __name__ == '__main__':
    # Windows consoles and pipes may default to a codepage that can't print emoji
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    try:
        cli()
    except LLMError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
