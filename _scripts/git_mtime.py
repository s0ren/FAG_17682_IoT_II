"""Pre-render: sæt hver sides ændringstid til datoen for sidste commit.

Quarto henter "Ændret" (date-modified: last-modified) fra filens
ændringstid. Den nulstilles af git checkout og kloning, så her sættes den
til tidspunktet for sidste commit, der ændrede filen.

Filer med ikke-committede ændringer springes over: deres ændringstid er
allerede den rigtige.
"""

import os
import subprocess


def git(*args):
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, check=True
    ).stdout


def main():
    try:
        root = git("rev-parse", "--show-toplevel").strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return  # ikke et git-repo: lad ændringstiderne være

    os.chdir(root)
    tracked = set(git("ls-files", "-z", "*.qmd", "*.md").split("\0")) - {""}
    dirty = set(git("diff", "--name-only", "-z", "HEAD").split("\0"))

    # Ét gennemløb af historikken, nyeste commit først:
    # første gang en fil dukker op, er det dens seneste commit.
    last_commit = {}
    timestamp = None
    log = git("log", "--format=@%ct", "--name-only", "-z", "--", *tracked)
    for entry in log.replace("\n", "\0").split("\0"):
        if entry.startswith("@"):
            timestamp = int(entry[1:])
        elif entry and entry in tracked and entry not in last_commit:
            last_commit[entry] = timestamp

    for path, ts in last_commit.items():
        if path not in dirty:
            os.utime(path, (ts, ts))


if __name__ == "__main__":
    main()
