from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
from github import Github, Commit
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
TOKENIZER = RegexpTokenizer(r'\w+')

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
  count = 0
  for commit in commits:
    count += 1
    process_commit(commit)
    if count > 1000: break

def process_commit(commit):
  message = commit.commit.message
  tokens = set(tokenize(message))
  if len(FIX_WORDS.intersection(tokens)) == 0: return None
  for commit_file in commit.files:
    print(commit_file.filename)
  exit()



def tokenize(message):
  return TOKENIZER.tokenize(stem(message.lower()))


if __name__ == "__main__":
  #get_issues(REPO_NAME, label_names=["confirmed"])
  get_commits(REPO_NAME, "18/03/2013", "18/09/2014")
