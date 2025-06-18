#!/usr/bin/env python3
"""
LLM enrichment CLI for R.A.D.A.R. project.
Subcommands:
  llm          - LLM-enrich a single issue
  batch-llm    - Batch LLM-enrich multiple issues
"""
import sys
import subprocess

def main():
    import argparse
    parser = argparse.ArgumentParser(
        prog='github_cli.py',
        description='LLM enrichment CLI for R.A.D.A.R. project'
    )
    sub = parser.add_subparsers(dest='command', required=True)


    # llm single
    p_llm = sub.add_parser('llm', help='LLM-enrich a single issue')
    p_llm.add_argument('--repo', required=True, help='owner/repo')
    p_llm.add_argument('--issue', type=int, required=True, help='Issue number')
    p_llm.add_argument('--apply', action='store_true', help='Apply the update')

    # batch-llm
    p_batch = sub.add_parser('batch-llm', help='Batch LLM-enrich multiple issues')
    p_batch.add_argument('--repo', required=True, help='owner/repo')
    p_batch.add_argument('--csv', help='Output CSV file for review')
    p_batch.add_argument('--interactive', action='store_true', help='Approve per-issue interactively')
    p_batch.add_argument('--apply', action='store_true', help='Apply all updates')

    args = parser.parse_args()

    # Map commands to scripts (LLM enrichment only)
    cmd_map = {
        'llm': [
            'scripts/github_enrich_issue_llm.py',
            ['--repo', args.repo, '--issue', str(args.issue)] + (['--apply'] if args.apply else []),
        ],
        'batch-llm': [
            'scripts/github_batch_enrich_llm.py',
            ['--repo', args.repo] + (['--csv', args.csv] if args.csv else []) + (['--interactive'] if args.interactive else []) + (['--apply'] if args.apply else []),
        ],
    }

    script, extra = cmd_map[args.command]
    full_cmd = ['python3', script] + extra
    try:
        subprocess.run(full_cmd, check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)

if __name__ == '__main__':
    main()