#!/usr/bin/env python3
import json
import os
import re
import subprocess
import sys
import urllib.request


def get_upstream_version():
    """Fetch latest release from upstream"""
    url = "https://api.github.com/repos/SaltifyDev/yogurt-releases/releases/latest"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.load(resp)
            return data.get("tag_name", "")
    except Exception as e:
        print(f"Error fetching upstream version: {e}", file=sys.stderr)
        return ""


def git_tag_exists(tag):
    """Check if git tag exists"""
    try:
        subprocess.run(["git", "rev-parse", tag], capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def extract_upstream(version):
    """Extract upstream version from patch version (e.g., v0.1.0-dev.181.2 -> v0.1.0-dev.181)"""
    match = re.match(r"^(.+\.\d+)\.\d+$", version)
    return match.group(1) if match else version


def main():
    # Get inputs from environment
    event_name = os.environ.get("GITHUB_EVENT_NAME", "")
    input_version = os.environ.get("INPUT_VERSION", "")

    if input_version:
        # Manual trigger with specified version
        version = input_version
        upstream = extract_upstream(version)
        should_build = True
        print(f"Manual trigger: version={version}, upstream={upstream}")
    else:
        # Auto-detect from upstream
        upstream = get_upstream_version()
        if not upstream or upstream == "null":
            print("Failed to fetch upstream version")
            print("should_build=false")
            return

        print(f"Latest upstream version: {upstream}")

        if git_tag_exists(upstream):
            print(f"Version {upstream} already released")
            if event_name == "push":
                # Create patch version
                patch = 1
                while git_tag_exists(f"{upstream}.{patch}"):
                    patch += 1
                version = f"{upstream}.{patch}"
                print(f"Creating patch version: {version}")
                should_build = True
            else:
                print("should_build=false")
                return
        else:
            print(f"New version detected: {upstream}")
            version = upstream
            should_build = True

    # Output results
    print(f"version={version}")
    print(f"upstream_version={upstream}")
    print(f"should_build={str(should_build).lower()}")

    # Set GitHub Actions outputs
    with open(os.environ.get("GITHUB_OUTPUT", "/dev/null"), "a") as f:
        f.write(f"version={version}\n")
        f.write(f"upstream_version={upstream}\n")
        f.write(f"should_build={str(should_build).lower()}\n")


if __name__ == "__main__":
    main()
