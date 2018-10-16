import requests
import json
import pprint
import collections
import pandas as pd
import os
import unittest
first_url_to_get = 'https://api.github.com/user/starred'
myun = "wislish"
mypw = os.environ['GITHUBPW']

def get_starred_by_me():
    my_starred_repos = []
    resp_list = []
    last_resp = ''
    first_url_resp = requests.get(first_url_to_get, auth=(myun, mypw))
    last_resp = first_url_resp
    # print(first_url_resp.text)
    # print(last_resp.links)
    resp_list.append(json.loads(first_url_resp.text))

    # GitHub uses pagination rather than return everything in one call.
    # Due to this, we'll need to check the .links that are returned from each response.
    # As long as there is a next link to call, we'll continue to do so.
    while last_resp.links.get('next'):
        next_url_to_get = last_resp.links['next']['url']
        next_url_resp = requests.get(next_url_to_get, auth=(myun, mypw))
        last_resp = next_url_resp
        resp_list.append(json.loads(next_url_resp.text))

    for resp in resp_list:
        for repo in resp:
            msr = repo['html_url']
            my_starred_repos.append(msr)

    pprint.pprint("Starred Repos URL : {}".format(my_starred_repos))

    # get the author of the starred repo.
    my_starred_users = []
    for ln in my_starred_repos:
        right_split = ln.split('.com/')[1]
        starred_usr = right_split.split('/')[0]
        my_starred_users.append(starred_usr)

    pprint.pprint("Starred Repo Author : {}".format(my_starred_users))

    return my_starred_users


def get_starred_by_users(user_name, level=1):
    """ 
    @user_name: must be iterable 
    @level: degree of connections
    """
    if isinstance(user_name, str) or not isinstance(user_name, collections.Iterable):
        raise Exception("Input user_name must be iterable, and not String")

    cur_level = 0
    # visited = set()
    user_starred_repos = {}
    repos = set()
    while cur_level < level:
        cur_level += 1
        temp = []
        for user in user_name:
            if user in user_starred_repos:
                continue
            try:
                starred_repo, starred_users = download_starred_repo(user)
            except Exception:
                print("Failed to parse user {}".format(user))
            
            user_starred_repos[user] = starred_repo
            temp.extend(starred_users)
            repos.update(starred_repo)

        user_name = set(temp)
        pprint.pprint("From Level 0 - Level {}, there are {} users, and {} repos".format(
            cur_level,len(user_starred_repos), len(repos)))
    
    # transform the dict into utility matrix, csv file.
    generate_utility_mat(user_starred_repos,level=level)


def download_starred_repo(user_name):
    starred_resp_list = []
    starred_repo = []
    last_resp = ''
    first_url_to_get = 'https://api.github.com/users/' + user_name + '/starred'
    first_url_resp = requests.get(first_url_to_get, auth=(myun, mypw))
    last_resp = first_url_resp
    starred_resp_list.append(json.loads(first_url_resp.text))

    while last_resp.links.get('next'):
        next_url_to_get = last_resp.links['next']['url']
        next_url_resp = requests.get(next_url_to_get, auth=(myun, mypw))
        last_resp = next_url_resp

    for resp in starred_resp_list:
        for repo in resp:
            sr = repo['html_url']
            starred_repo.append(sr)

    starred_users = []
    for ln in starred_repo:
        right_split = ln.split('.com/')[1]
        starred_usr = right_split.split('/')[0]
        starred_users.append(starred_usr)
    return starred_repo, starred_users

def bin_user_repo(repo_vocab, starred_repos):

    repo_to_ind = {}
    i = 0
    for v in repo_vocab:
        repo_to_ind[v] = i
        i += 1

    user_repo = {}
    for user in starred_repos.keys():
        user_repo[user] = [0] * len(repo_vocab)
        for val in starred_repos[user]:
            user_repo[user][repo_to_ind[val]] = 1
    return user_repo, repo_to_ind

def generate_utility_mat(starred_repos,file_name="starred_repos_level",level=1):

    # my_starred_users = get_starred_by_me()
    # starred_repos = {k: [] for k in set(my_starred_users)}
    # for usr in list(set(my_starred_users)):

    repo_vocab = [item for sl in list(starred_repos.values()) for item in sl]
    repo_set = list(set(repo_vocab))
    user_repo, repo_to_ind = bin_user_repo(repo_set, starred_repos)
    df = pd.DataFrame.from_dict(data=user_repo,orient='index')
    df.columns = repo_set
    df.to_csv(file_name+"_"+str(level)+".csv",index=True)


if __name__ == "__main__":
    get_starred_by_users([myun],level=3)
