import pymongo, sys
from pprint import pprint
import transfer_helpers as helpers
import helpers.pymongo_worker_threads as workers

# output file
output = open('watchers-transfer.txt', 'w')

# Define the source and target collections
client = pymongo.MongoClient (host="da0.eecs.utk.edu")
repos = client['ossfinder']['repositories_unique']
source = client['test']['watchers']
target = client['ossfinder']['watchers']

# full names of all of the repos
repo_full_names = helpers.get_repo_full_names(repos);
print('retrieved full names')

# Clear out the target collection to ensure a clean copy
target.delete_many({})
print('deleted from target')

def worker_function(chunk, target, repo_full_names, output):
  info = str(['chunk', len(chunk)])
  print(info)
  output.write(info)
  n_inserted = 0
  for doc in chunk:
    full_name = doc['owner'] + '/' + doc['repo']
    if full_name in repo_full_names:
      doc['full_name'] = full_name
      target.insert(doc)
      n_inserted += 1
    
  info = str(['watchers', n_inserted])
  print(info)
  output.write(info)

worker_args = {
  'target': target,
  'repo_full_names': repo_full_names,
  'output': output
}

workers.do_work(source_collection = source, worker_function = worker_function, worker_args = worker_args, num_docs_per_thread=10000)


'''
skip = 0
limit = 1000
count = 1
total = 0
fields = {"owner": 1, "repo": 1, "login": 1}
while count > 0:
	try:
		docs = source.find({}, fields).skip(skip).limit(limit)
		docs = list(docs)
		to_insert = []
		for doc in docs:
			full_name = doc['owner'] + '/' + doc['repo']
			if full_name in repo_full_names:
				doc['full_name'] = full_name
				to_insert.append(doc)
	
		if len(to_insert) > 0:
			target.insert_many(to_insert)
			
		skip += limit
		count = len(docs)
		total += len(to_insert)
		info = str(['watchers', count, len(to_insert), total])
		output.write(info)
		print(info)

	except:
		print("Unexpected error:", sys.exc_info()[0])
		raise SystemExit

info = 'COMPLETE: ' + str(total)
output.write(info)
print(info)
'''
