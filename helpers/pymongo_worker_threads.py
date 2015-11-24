from threading import Thread
import pymongo, sys, math
import aggregate_calculate as agcalc 

# The worker class defines an object that takes a portion of a mongo
# collection at one time and runs a passed function against it.
class Worker(Thread):

  ''' constructor arguments 
  source_collection: the pymongo collection,
  find_args: dict; key/value pairs represent the arguments passed to the pymongo .find() function,
  begin: int; the starting point in the collection for this thread
  limit: int; the ending point in the collection for this thread
  worker_function: function; the function to which the chunks of the pymongo collection will be passed as the first argument
  worker_args: dict; key/value pairs represent the named arguments passed to the pymongo .find() function
  '''
  def __init__(self, source_collection, find_args = {}, begin, end, limit, worker_function, worker_args = {}):
    Thread.__init__(self)
    self.source_collection = source_collection
    self.find_args = find_args
    self.begin = begin
    self.end = end
    self.limit = limit
    self.worker_function = worker_function
    self.worker_args = worker_args

  def run(self):

    # iterate over chunks of the source using the begin, end, and limit
    # properties. apply the worker function to each chunk
    count = 1
    skip = self.begin 
    while count != 0 and skip < self.end:
      chunk = self.source.find(**self.find_args).skip(skip).limit(self.limit)
      chunk = list(chunk)
      self.worker_args["chunk"] = chunk
      self.worker_function(**self.worker_args)
      count = len(chunk)
      skip += self.limit

def do_work(source_collection, find_args, worker_function, worker_args, num_docs_per_thread = 1000):
  # determine the number of threads to spawn
  num_docs = source_collection.find(**find_args).count()
  num_threads = math.ceil(num_docs / num_docs_per_thread)
  limit = min(500, num_docs)
 
  # spawn the workers
  for i in range(0, num_threads):
    begin = i * num_docs_per_thread
    end = (i + 1) * num_docs_per_thread
    thread = Worker(source_collection, find_args, begin, end, limit, worker_function, worker_args) 
    thread.start()