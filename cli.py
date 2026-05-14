#!/usr/bin/env python3
"""
GeoData-Acquirer CLI — LLM-based intelligent geographic data acquisition.
"""
import sys
import os
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / "config" / ".env"
load_dotenv(env_path)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.main import GeoDataAcquirer


def main():
    parser = argparse.ArgumentParser(
        description="GeoData-Acquirer — Intelligent Geographic Data Acquisition System"
    )
    parser.add_argument(
        "query", nargs="?",
        help="Natural language query (e.g. '武汉市行政区划边界')"
    )
    parser.add_argument(
        "--list-sources", action="store_true",
        help="List available data sources and exit"
    )
    parser.add_argument(
        "--source", "-s",
        help="Force a specific data source (bypass matching)"
    )
    parser.add_argument(
        "--data-type", "-t",
        help="Override detected data type (e.g. boundary, road, weather)"
    )
    parser.add_argument(
        "--output", "-o", default="output",
        help="Output directory (default: output)"
    )

    args = parser.parse_args()

    # List sources mode
    if args.list_sources:
        kg_path = "data/admin_kg.json"
        if not os.path.exists(kg_path):
            print(f"[ERROR] Knowledge graph file not found: {kg_path}")
            sys.exit(1)

        acquirer = GeoDataAcquirer(kg_path)
        print("\nAvailable Data Sources:\n")
        print(f"{'Name':<20} {'Data Types':<35} {'Auth':<8} {'Coverage':<12}")
        print("-" * 75)
        for src in acquirer.list_available_sources():
            types = ", ".join(src.get("data_types", []))
            auth = "Yes" if src.get("requires_auth") else "No"
            print(f"{src['name']:<20} {types:<35} {auth:<8} {src.get('coverage', ''):<12}")
        print()
        acquirer.close()
        return

    # Query mode
    if not args.query:
        parser.print_help()
        print("\nExamples:")
        print('  python cli.py "武汉市行政区划边界"')
        print('  python cli.py "武汉的路网数据"')
        print('  python cli.py "武汉今天天气"')
        print('  python cli.py --list-sources')
        sys.exit(1)

    kg_path = "data/admin_kg.json"
    if not os.path.exists(kg_path):
        print(f"[ERROR] Knowledge graph file not found: {kg_path}")
        sys.exit(1)

    try:
        acquirer = GeoDataAcquirer(kg_path)
        output_path = acquirer.process(
            user_input=args.query,
            force_source=args.source,
        )
        print(f"[SUCCESS] Output: {output_path}")

    except Exception as e:
        print(f"\n{'=' * 60}")
        print(f"[ERROR] {e}")
        print(f"{'=' * 60}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        if 'acquirer' in locals():
            acquirer.close()


if __name__ == "__main__":
    main()
