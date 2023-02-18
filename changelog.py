#!/usr/bin/env python3

import subprocess
import os
import argparse

CONF = None
CHANGELOG = "changelog"

if os.path.exists("settings.yaml"):
    import yaml
    from pathlib import Path
    CONF = yaml.safe_load(Path("settings.yaml").read_text())
elif os.path.exists("settings.json"):
    import json
    CONF = json.loads(open("settings.json", "r", encoding="utf-8").read())

def get_branch():
    branch = subprocess.check_output(["git", "branch"], stderr=subprocess.STDOUT)
    return branch.decode().removeprefix("*")

def get_commits(reg, path):
    output_lines = []
    subprocess.call(["git", "checkout", CONF["branch"]], cwd=path)
    lines = subprocess.check_output(
        ['git', 'log', '--since', CONF["from_date"]], stderr=subprocess.STDOUT, cwd=path
    )
    lines = str(lines).split("\\n")
    for line in lines:
        if line.find(reg) != -1:
            output_lines.append(line)
    return output_lines

def get_non_prefixed_commits(reg):
    output_lines = []
    subprocess.call(["git", "checkout", CONF["branch"]])
    lines = subprocess.check_output(
        ['git', 'log', '--since', CONF["from_date"]], stderr=subprocess.STDOUT
    )
    lines = str(lines).split("\\n")
    for line in lines:
        if not line.find(reg) != -1:
            output_lines.append(line)
    return output_lines

def gen_markdown(branch, logs):
    output = ""
    branch = "# " + branch + "\n"
    output += branch
    for line in logs:
        md = "- " + line.strip() + "\n"
        output += md
    return output

def create_changelog_file(file_name, data): 
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(data)

parser = argparse.ArgumentParser(
                    prog = 'log2md',
                    description = 'Generate changelog MD files from Git log',
                    )

parser.add_argument('--from', nargs='?', help='Start date', dest="from_date")
parser.add_argument('--dir', nargs='?', help='Target directory', dest="directory")
parser.add_argument('--prefix', nargs='?', help='Commit prefix to look for', dest="commit_prefix")
parser.add_argument('--branch', nargs='?', help='Git branch', dest="branch")

args = parser.parse_args()

if args.from_date:
    CONF["from_date"] = args.from_date
if args.directory:
    CONF["scan_dir"] = args.directory
if args.commit_prefix:
    CONF["commit_prefix"] = args.commit_prefix
if args.branch:
    CONF["branch"] = args.branch

md_data = gen_markdown(get_branch(), get_commits(CONF["commit_prefix"], CONF["scan_dir"]))
name = CHANGELOG + "_" + CONF["branch"] + ".md"
create_changelog_file(name, md_data)
