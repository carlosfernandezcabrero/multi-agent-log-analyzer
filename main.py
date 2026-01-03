import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

from orchestrator.pipeline import LogAnalysisPipeline
from utils.exceptions import PipelineExecutionError
from utils.logging import setup_logging


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Multi-agent log analysis pipeline")
    parser.add_argument(
        "logfile",
        type=Path,
        help="Path to the log file to analyze",
    )
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    setup_logging()

    args = parse_args()

    try:
        if not args.logfile.exists():
            raise FileNotFoundError(f"Log file not found: {args.logfile}")

        pipeline = LogAnalysisPipeline()
        report = pipeline.run(args.logfile)

        output_path = Path("outputs/report.md")
        output_path.write_text(report)

        print(f"Report successfully generated at: {output_path}")
    except PipelineExecutionError as exc:
        print(f"[PIPELINE ERROR] {exc}", file=sys.stderr)
        sys.exit(1)

    except Exception as exc:
        print(f"[UNEXPECTED ERROR] {exc}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
