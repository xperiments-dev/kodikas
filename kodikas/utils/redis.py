""" Redis related utility functions"""

import redis


class Redis:

    def __init__(self):
        self.host = "localhost"
        self.port = 6379
        self.password = ""

        self.connection = redis.StrictRedis(host=self.host, port=self.port,
                                            password=self.password, decode_responses=True)

    def list_rpush(self, list_name, *values):
        """ (list) data structure in redis """

        rpush = self.connection.rpush(list_name, *values)

        return rpush

    def list_range(self, list_name, start=0, end=-1):
        """ returns slice of list elements for a given range """

        list_range = self.connection.lrange(list_name, start=0, end=-1)

        return list_range

    def list_rpop(self, list_name):
        """ Remove and return the last item of the list name """
        last_element_list = self.connection.rpop(list_name)
        return last_element_list

    def list_length(self, list_name):
        """ returns the length/size of the (list) """

        list_length = self.connection.llen(list_name)

        return list_length

    def delete_key(self, list_name):
        """ deletes the key and its values """

        delete = self.connection.delete(list_name)

        return delete

    def hash_map_set(self, user_email, data):
        """ creates a hash-map in redis with key,value pairs """

        flush_redis = self.connection.delete(user_email)

        for key in data.keys():

            if isinstance(data[key], dict):
                for sub_key in data[key].keys():
                    # sets key,value as per input data order of labels
                    hset = self.connection.hset(
                        user_email, sub_key, data[key][sub_key])

            else:
                # sets key,value as per input data order of labels
                hset = self.connection.hset(user_email, key, data[key])

        return True

    def hash_map_getall(self, user_email):
        """ returns all key,value pairs stored in hashmap for a given hash"""

        hgetall_data = self.connection.hgetall(user_email)

        return hgetall_data

    def hash_map_delkey(self, user_email, data):
        """ deletes key or keys from a hash-map user_email """

        for hashkey in data:
            self.connection.hdel(user_email, hashkey)

        return True

    def hash_map_hget(self, user_email, data_key):
        """ Return the value of data-key within the hash name """

        hget_key = self.connection.hget(user_email, data_key)

        return hget_key

    def text_complete(self, list_name, filtered_data):

        # get all existing gpt priming examples from redis in (input/output) format
        redis_list_data = self.list_range(list_name, start=0, end=-1)

        # forming query to call gpt api
        form_query = "".join(redis_list_data) + \
            "input: " + filtered_data + "\n"

        return form_query
