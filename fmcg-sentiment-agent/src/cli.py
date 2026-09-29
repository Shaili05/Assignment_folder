"""
cli.py


Single entry point for every offline/CLI command in the project. Each
subcommand wraps one module's core function; the modules themselves have
no argparse or __main__ block, so they stay importable without side effects.


Run:
    python -m src.cli sentiment-trend --aspect packaging --granularity month
    python -m src.cli flagged-reviews --level high --days 365
    python -m src.cli summary-report --days 30 --save
    python -m src.cli apply-label-rules
    python -m src.cli recompute-safety-flags
    python -m src.cli scrub-pii --input ... --output ...
    python -m src.cli evaluate --models groq:openai/gpt-oss-120b
    python -m src.cli audit-summary
"""


import argparse
import json


from src.config.logging_config import configure_logging
from src.config.settings import LABELED_REVIEWS_PATH, REVIEWS_PATH, VECTORSTORE_DIR
from src.utils.output import write_line




def run_sentiment_trend(args):
    from src.mcp.tools.sentiment_trend import sentiment_trend


    result = sentiment_trend(args.aspect, args.product, args.brand, args.granularity, args.periods, args.as_of)
    write_line(json.dumps(result, indent=2))




def run_flagged_reviews(args):
    from src.mcp.tools.flagged_reviews import flagged_reviews


    result = flagged_reviews(args.level, args.issue_type, args.days, limit=args.limit)
    write_line(json.dumps(result, indent=2))




def run_summary_report(args):
    from src.mcp.tools.summary_report import generate_summary_report, save_report


    report = generate_summary_report(args.days, args.as_of, args.product, args.brand)
    if "error" in report:
        raise SystemExit(report["error"])
    if args.json:
        write_line(json.dumps({k: v for k, v in report.items() if k != "markdown"}, indent=2))
    else:
        write_line(report["markdown"])
    if args.save:
        write_line(f"Saved {save_report(report)}")




def run_apply_label_rules(args):
    from src.data_prep.apply_label_rules import run as apply_label_rules_run


    apply_label_rules_run(args.labeled, args.scrubbed, args.chroma_dir, args.collection, args.skip_chroma)




def run_recompute_safety_flags(args):
    from src.data_prep.recompute_safety_flags import run as recompute_safety_flags_run


    recompute_safety_flags_run(args.labeled, args.scrubbed, args.chroma_dir, args.collection, args.skip_chroma)




def run_scrub_pii(args):
    from src.data_prep.scrub_pii import run as scrub_pii_run


    scrub_pii_run(args.input, args.output)




def run_evaluate(args):
    from src.evaluation.run_evaluation import run as evaluate_run


    evaluate_run(args.models, args.ids)




def run_audit_summary(args):
    from src.utils.audit_logger import load_log, usage_summary


    records = load_log()
    write_line(f"{len(records)} interactions")
    write_line(usage_summary(records).to_string(index=False))




def build_parser():
    parser = argparse.ArgumentParser(prog="python -m src.cli")
    subparsers = parser.add_subparsers(dest="command", required=True)


    p = subparsers.add_parser("sentiment-trend", description="Sentiment counts and shares over time.")
    p.add_argument("--aspect", default=None)
    p.add_argument("--product", default=None)
    p.add_argument("--brand", default=None)
    p.add_argument("--granularity", default="month")
    p.add_argument("--periods", type=int, default=6)
    p.add_argument("--as-of", default=None)
    p.set_defaults(func=run_sentiment_trend)


    p = subparsers.add_parser("flagged-reviews", description="Reviews flagged for a safety or quality issue.")
    p.add_argument("--level", default=None)
    p.add_argument("--issue-type", default=None)
    p.add_argument("--days", type=int, default=None)
    p.add_argument("--limit", type=int, default=5)
    p.set_defaults(func=run_flagged_reviews)


    p = subparsers.add_parser("summary-report", description="Brand-health summary for a recent window.")
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--as-of", default=None)
    p.add_argument("--product", default=None)
    p.add_argument("--brand", default=None)
    p.add_argument("--save", action="store_true")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=run_summary_report)


    p = subparsers.add_parser("apply-label-rules", description="Replace sentiment and aspect labels with the rule-based versions.")
    p.add_argument("--scrubbed", default=str(REVIEWS_PATH))
    p.add_argument("--labeled", default=str(LABELED_REVIEWS_PATH))
    p.add_argument("--chroma-dir", default=str(VECTORSTORE_DIR))
    p.add_argument("--collection", default="reviews")
    p.add_argument("--skip-chroma", action="store_true")
    p.set_defaults(func=run_apply_label_rules)


    p = subparsers.add_parser("recompute-safety-flags", description="Recompute safety/quality flags and sync Chroma metadata.")
    p.add_argument("--scrubbed", default=str(REVIEWS_PATH))
    p.add_argument("--labeled", default=str(LABELED_REVIEWS_PATH))
    p.add_argument("--chroma-dir", default=str(VECTORSTORE_DIR))
    p.add_argument("--collection", default="reviews")
    p.add_argument("--skip-chroma", action="store_true")
    p.set_defaults(func=run_recompute_safety_flags)


    p = subparsers.add_parser("scrub-pii", description="Mask reviewer identity columns and redact PII typed inside review text.")
    p.add_argument("--input", default=str(LABELED_REVIEWS_PATH))
    p.add_argument("--output", default=str(REVIEWS_PATH))
    p.set_defaults(func=run_scrub_pii)


    p = subparsers.add_parser("evaluate", description="Score the agent on the evaluation questions.")
    p.add_argument("--models", nargs="+", default=None)
    p.add_argument("--ids", nargs="+", default=None, help="Run only these question ids.")
    p.set_defaults(func=run_evaluate)


    p = subparsers.add_parser("audit-summary", description="Show latency, tokens and cost per model.")
    p.set_defaults(func=run_audit_summary)


    return parser




def main():
    configure_logging()
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)




if __name__ == "__main__":
    main()

