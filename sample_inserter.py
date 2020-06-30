from pymongo import MongoClient
import yaml
import random

with open('config.yaml', 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.BaseLoader)

client = MongoClient()
client.drop_database(cfg['server']['db'])
db = client[cfg['server']['db']]


workers = ['hjsong', 'songhyunje']
docs = []
with open('data/sample.txt') as f:
    for line in f:
        texts = line.strip().split('|||||')
        doc = {'sources': texts[:-1],
               'semi-summary': texts[-1],
               'summary': "",
               'completed': False, # bool(random.getrandbits(1)),
               'update_datetime': "",
               'worker': random.choice(workers)}
        docs.append(doc)

new_result = db.posts.insert_many(docs)
print('Multiple posts: {0}'.format(new_result.inserted_ids))

retrieved_posts = db.posts.find()
# print(retrieved_posts[0])
for post in retrieved_posts:
    print(post['sources'])

