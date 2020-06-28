from pymongo import MongoClient
from bson.objectid import ObjectId
import yaml
import random

with open('config.yaml', 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.BaseLoader)

client = MongoClient()
db = client[cfg['server']['db']]


docs = []
with open('data/mds_1.txt') as f:
    for line in f:
        texts = line.strip().split('|||||')
        doc = {'sources': texts[:-1],
               'semi-summary': texts[-1],
               'summary': "",
               'completed': bool(random.getrandbits(1)),
               'update_datetime': "",
               'category': "hjsong" if random.getrandbits(1) == 1 else "aykim"}
        docs.append(doc)

new_result = db.posts.insert_many(docs)
print('Multiple posts: {0}'.format(new_result.inserted_ids))

# retrieved_posts = posts.find({'category': 'sport'})
# for post in retrieved_posts:
#     post['date'] = datetime.datetime.now()
#     posts.update_one({'_id': post['_id']}, {"$set": post}, upsert=False)


# 5ef5b71dcb74b0b7fb7757ad
# 5ef5b71dcb74b0b7fb7757aa
# retrieved_posts = posts.find({'category': 'sport'})
# for post in retrieved_posts:
#     print(type(post['_id']))

# retrieved_posts = posts.find({"_id": ObjectId("5ef5b71dcb74b0b7fb7757aa")})
# print(retrieved_posts)
# for post in retrieved_posts:
#     print(post)

retrieved_posts = db.posts.find()
# print(retrieved_posts[0])
for post in retrieved_posts:
    print(post['sources'])


