import argparse
from pathlib import Path

from vep_annotate.pipeline import run_annotation
from vep_annotate.vep_client import DEFAULT_SERVER


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Annotate ClinVar benchmark variants with Ensembl VEP consequence terms."
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--checkpoint-dir", type=Path, default=Path(".vep_cache"))
    parser.add_argument("--batch-size", type=int, default=200)
    parser.add_argument("--delay-seconds", type=float, default=1.0)
    parser.add_argument("--server", type=str, default=DEFAULT_SERVER)
    parser.add_argument(
        "--no-resume",
        dest="resume",
        action="store_false",
        help="Ignore existing checkpoints and refetch everything.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    df = run_annotation(
        input_csv=args.input,
        output_csv=args.output,
        checkpoint_dir=args.checkpoint_dir,
        batch_size=args.batch_size,
        delay_seconds=args.delay_seconds,
        server=args.server,
        resume=args.resume,
    )
    n_target = int(df["is_target_consequence"].sum())
    print(f"Annotated {len(df)} variants, {n_target} matched target consequences.")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
