import redis
import json
import os

class RedisUtil:
    redis_client=None
    @classmethod
    def init_redis(cls,host=os.getenv('REDIS_HOST','redis'),port=os.getenv('REDIS_PORT',6379),decode_response=True):
        cls._redis_client=redis.Redis(host=host,port=port,decode_responses=decode_response)

    @classmethod
    def get_redis_client(cls):
        if cls._redis_client is None:
            cls.init_redis()
        return cls._redis_client
    
    @classmethod
    def set_data_redis(cls,key:str ,value,ttl:int=None):
        client=cls.get_redis_client()
        if isinstance(value,(dict,list)):
            value=json.dumps(value)
        if ttl is None:
            client.set(key,value)
        else:
            client.set(key,value,ex=ttl)

    @classmethod
    def get_data_redis(cls,key:str):
        client = cls.get_redis_client()
        value=client.get(key)
        try:
            value=client.get(key)
        except redis.RedisError as e:
            print(f'Redis get error {e}')

        if not value:
            return None
        
        if isinstance(value,str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass
        return value
