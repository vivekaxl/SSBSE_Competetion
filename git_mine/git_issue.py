from __future__ import print_function, division
import sys, os, re, csv
sys.path.append(os.path.abspath("."))
from github import Github
from github.GithubObject import NotSet
from config import user_name, password
from datetime import datetime
from stemming.porter2 import stem
from nltk.tokenize import RegexpTokenizer

__author__ = 'panzer'

REPO_NAME = "odoo/odoo"
DATE_FORMAT = "%d/%m/%Y"
GIT = Github(user_name, password)
FIX_WORDS = set(["error", "bug", "fix", "issue", "mistake", "incorrect", "fault", "defect", "flaw", "type"])
WHITE_SPACE_REGEX = "\\s"
ISSUE_REGEX = r'#\d+'
TOKENIZER = RegexpTokenizer(r'\w+')
#CSV_HEADERS = ["FileName", "Message", "SHA", "Author", "Issue"]
#CSV_HEADERS = ["FileName", "SHA", "Author", "Issue"]
CSV_HEADERS = ["FileName", "SHA", "Issue"]

RELEASES = [
  ("8", "19/09/2014", "17/03/2016")
  #("7", "17/01/2013", "18/09/2014")
]

def say(*lst):
  print(*lst, end="")
  sys.stdout.flush()

def get_date(date_string):
  return datetime.strptime(date_string, DATE_FORMAT)

def get_repo(repo_name):
  return GIT.get_repo(repo_name)

def get_issues(repo_name, label_names=None):
  #query += "+repo:%s"%repo_name
  repo = get_repo(repo_name)
  labels = NotSet

  if label_names:
    labels = [repo.get_label(label_name) for label_name in label_names]
  issues = repo.get_issues(state="closed", labels=labels)
  count = 0
  for i in issues:
    count += 1
  print(count)
  #print(GIT.search_issues(query).totalCount)
  # for issue in GIT.search_issues(query):
  #   print(issue.title)

def get_commits(rep_name, start, end):
  start = get_date(start)
  end =  get_date(end)
  repo = get_repo(rep_name)
  commits = repo.get_commits(since=start, until=end)
  changes = []
  for commit in commits:
    commit_changes = process_commit(commit)
    if commit_changes:
      changes += commit_changes
  return changes

def process_commit(commit):
  message = commit.commit.message
  tokens = set(tokenize(message))
  if len(FIX_WORDS.intersection(tokens)) == 0: return None
  issues = re.findall(ISSUE_REGEX, message)
  if not issues: return None
  issues = map(lambda x: int(x[1:]), issues)
  if not commit.files: return None
  files = [commit_file.filename for commit_file in commit.files]
  changes = []
  for issue in issues:
    for file_name in files:
      #changes.append([str(file_name), message.encode("utf-8"), str(commit.sha), str(commit.author.login) ,issue])
      #author_name = str(commit.author.login) if commit.author else None
      changes.append([str(file_name), str(commit.sha), issue])
  return changes

def tokenize(message):
  return TOKENIZER.tokenize(stem(message.lower()))

def to_csv(header, rows, file_name):
  with open(file_name, "wb") as f:
    writer =  csv.writer(f)
    writer.writerows([header]+rows)


def _main():
  for release, start, end in RELEASES:
    print("Release %s"%release)
    commits = get_commits(REPO_NAME, start, end)
    print("Legit Commits : %d"%len(commits))
    to_csv(CSV_HEADERS, commits, "Release_%s.csv"%release)

if __name__ == "__main__":
  # commits = get_commits(REPO_NAME, "18/03/2013", "18/07/2013")
  # to_csv(CSV_HEADERS, commits, "temp.csv")
  _main()
