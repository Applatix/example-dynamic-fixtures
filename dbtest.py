#!/usr/bin/env python

"""
Example application which will perform key/value insertion and retrieval tests against MongoDB and Redis
"""

import argparse
import logging
import time
import random
import string
import sys

import pymongo
import redis

logger = logging.getLogger('dbtest')

DEFAULT_ITERATIONS = 100000

rand_string = lambda length: ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))

def _print_progress(start_time, iteration, prefix=''):
    elapsed = time.time() - start_time
    rate = iteration / elapsed
    logger.info("%s%s iterations in %ss (%s/sec)", prefix, iteration, elapsed, rate)
    return elapsed

def mongodb_insert_test(test_collection, iterations):
    logger.info("Starting mongodb insertion test (%s iterations)", iterations)
    start_time = time.time()
    for key in range(1, iterations+1):
        if key % 1000 == 0:
            _print_progress(start_time, key, prefix='mongodb insert: ')
        value = rand_string(1024)
        test_collection.insert_one({'_id' : key, 'v' : value})
    elapsed = time.time() - start_time
    return elapsed

def mongodb_read_test(test_collection, iterations):
    logger.info("Starting mongodb read test (%s iterations)", iterations)
    randomized_keys = list(range(1, iterations+1))
    random.shuffle(randomized_keys)
    start_time = time.time()
    i = 1
    for rand_key in randomized_keys:
        if i % 1000 == 0:
            _print_progress(start_time, i, prefix='mongodb read: ')
        test_collection.find_one({'_id' : rand_key})
        i += 1
    elapsed = time.time() - start_time
    return elapsed

def redis_insert_test(redis_client, iterations):
    logger.info("Starting redis insertion test (%s iterations)", iterations)
    start_time = time.time()
    for key in range(1, iterations+1):
        if key % 1000 == 0:
            _print_progress(start_time, key, prefix='redis insert: ')
        value = rand_string(1024)
        redis_client.set(key, value)
    elapsed = time.time() - start_time
    return elapsed

def redis_read_test(redis_client, iterations):
    logger.info("Starting redis read test (%s iterations)", iterations)
    randomized_keys = list(range(1, iterations+1))
    random.shuffle(randomized_keys)
    start_time = time.time()
    i = 1
    for rand_key in randomized_keys:
        if i % 1000 == 0:
            _print_progress(start_time, i, prefix='redis read: ')
        redis_client.get(rand_key)
        i += 1
    elapsed = time.time() - start_time
    return elapsed

def main():
    parser = argparse.ArgumentParser(description="Perform key/value insertion and retrieval ")
    parser.add_argument('--redis', required=True)
    parser.add_argument('--mongodb', required=True)
    parser.add_argument('--iterations', default=DEFAULT_ITERATIONS, type=int)
    args = parser.parse_args()

    logging.basicConfig(stream=sys.stdout,
                        level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
                        datefmt="%Y-%m-%dT%H:%M:%S")

    mongo_client = pymongo.MongoClient(host=args.mongodb)
    test_collection = mongo_client.dbtest.test_collection
    test_collection.drop()

    redis_client = redis.StrictRedis(host=args.redis)
    redis_client.flushdb()

    results = {}
    results['redis_insert'] = redis_insert_test(redis_client, args.iterations)
    results['mongodb_insert'] = mongodb_insert_test(test_collection, args.iterations)
    results['redis_read'] = redis_read_test(redis_client, args.iterations)
    results['mongodb_read'] = mongodb_read_test(test_collection, args.iterations)
    print("\nSummary ({} iterations):".format(args.iterations))
    format_str = "{test_name:<20} {elapsed:<20} {rate:<20}"
    print(format_str.format(test_name="Test", elapsed="Elapsed", rate="Rate (ops/sec)"))
    print('=' * 60)
    for test_name, elapsed in results.items():
        print(format_str.format(test_name=test_name, elapsed=elapsed, rate=args.iterations/elapsed))

if __name__ == '__main__':
    main()
