#!/usr/bin/env python3

import subprocess
import re
import os
import argparse

conf = None
CHANGELOG = "changelog"

if os.path.exists("settings.yaml"):
    import yaml
    from pathlib import Path
    conf = yaml.safe_load(Path("settings.yaml").read_text())
elif os.path.exists("settings.json"):
    import json
    conf = json.loads(open("settings.json").read())

def get_branch():
    branch = subprocess.check_output(["git", "branch"], stderr=subprocess.STDOUT)
    return branch.decode().removeprefix("*")

def get_commits(reg, dir):
    output_lines = []
    checkout = subprocess.call(["git", "checkout", conf["branch"]], cwd=dir)
    lines = subprocess.check_output(
        ['git', 'log', '--since', conf["from_date"]], stderr=subprocess.STDOUT
    )
    lines = str(lines).split("\\n")
    for line in lines:
        if line.find(reg) != -1:
            output_lines.append(line)
    return output_lines

def get_non_prefixed_commits(reg):
    output_lines = []
    checkout = subprocess.call(["git", "checkout", conf["branch"]])
    lines = subprocess.check_output(
        ['git', 'log', '--since', conf["from_date"]], stderr=subprocess.STDOUT
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
    conf["from_date"] = args.from_date
if args.directory:
    conf["scan_dir"] = args.directory
if args.commit_prefix:
    conf["commit_prefix"] = args.commit_prefix
if args.branch:
    conf["branch"] = args.branch

data = gen_markdown(get_branch(), get_commits(conf["commit_prefix"], conf["scan_dir"]))
file_name = CHANGELOG + "_" + conf["branch"] + ".md"
create_changelog_file(file_name, data)