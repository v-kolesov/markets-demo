from flask_redis import FlaskRedis


class RedisStore(FlaskRedis):

    def set_token(self, token, data):
        self.set(f'api-token:{token}', data)

    def get_token_data(self, token):
        return self.get(f'api-token:{token}').decode()


store = RedisStore()

