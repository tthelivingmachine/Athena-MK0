#!/usr/bin/bash

ABSOLUTE_REPO="$HOME/dev/Athena-MK0"
cd "$ABSOLUTE_REPO"


automated=false
if [ "$1" == "-a" ];
	then
	automated=true
	shift
fi


if [ -z "$1" ]; then
	COMMIT_MSG="Auto-commit on $(date '+%Y-%m-%d %H:%M:%S')"
else
	COMMIT_MSG="$1"
fi

git pull --rebase
git add .

if git diff --cached --quiet; then
	echo "No changes to commit. Aborting."
	exit 0
fi

if [ "$automated" = false ]; then
	git status
	read -p "Do you want to commit and push these changes? (y/N) " RESP
	if [[ ! "$RESP" =~ ^[Yy]$ ]]; then
		echo "Aborted."
		exit 0
	fi
fi

git commit -m "$COMMIT_MSG"
git push github main
git push vcs main

echo "Everything has been commited and pushed."
