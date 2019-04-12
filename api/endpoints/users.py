from flask import request
from flask_restplus import Resource, Api, fields, reqparse

import schemas
import models
from default_users import default_users
from utils import token_required

authorizations = {
    'token': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-TOKEN'
    }
}

api = Api(
    version='1.0',
    title='My Demo API',
    description="""ENDPOINTS:
* Create a Flask/SQLAlchemy project that implements the API endpoints described below (you may use your example framework from your github project).
* API endpoint 1: Perform a login sequence and return an authorization token.  Record the details of the login event in tracking table.  You may manually configure a few users however you wish (UI, pytest, etc.)
* API endpoint 2: Return login tracking details for all users or a specific user to the caller.
     """,
    authorizations=authorizations,
    security='token'
)

user_ns = api.namespace('users', description='Operations with `users` entity')


user_login_payload = api.model('Login payload', {
    'username': fields.String(
        required=True,
        description='`Username` of the registered user',
        example=default_users[0]['username']
    ),
    'password': fields.String(
        required=True,
        description='`Password` of the registered user',
        example=default_users[0]['password']
    ),
})


@user_ns.route('/login')
@user_ns.doc(True)
class UserAuthLogin(Resource):
    """ Login endpoints """
    @api.response(400, 'Validation data error')
    @api.response(404, 'Username does\'t exist')
    @api.response(422, 'Password is wrong')
    @api.response(200, 'Successfully logged in')
    @user_ns.doc(True)
    @api.expect(user_login_payload)
    def post(self):
        res, errs = schemas.UserLogin().load(request.json)
        if errs:
            return errs, 400

        user = models.User.get_by_username(res['username'])

        if user is None:
            return {}, 404

        sess = models.db.session
        if not user.password_verify(res['password']):
            sess.add(models.UserAuthLogs(
                user=user,
                auth_type=models.UserAuthLogs.AUTH_TYPE['TOKEN'],
                status=models.UserAuthLogs.STATUSES['FAIL'],
                ip=request.remote_addr,
            ))
            sess.commit()

            return {}, 422

        token = user.login()

        sess.add(models.UserAuthLogs(
            user_id=user.id,
            auth_type=models.UserAuthLogs.AUTH_TYPE['TOKEN'],
            status=models.UserAuthLogs.STATUSES['SUCCESS'],
            ip=request.remote_addr,
        ))
        sess.commit()

        return {'token': token}, 200


pagination_arguments = reqparse.RequestParser()

add_argument = pagination_arguments.add_argument

add_argument(
    'page', type=int, default=1,
)
add_argument('users', type=str)
add_argument(
    'per_page', type=int,
    choices=[5, 10, 20, 30, 40, 50], default=10
)


@user_ns.route('/auth/logs')
@user_ns.doc(True)
class UserAuthLogs(Resource):
    @api.response(200, 'Success')
    @api.response(401, 'Access denied')
    @api.response(404, 'No data found')
    @api.expect(pagination_arguments, validate=True)
    @token_required
    def get(self):
        args = pagination_arguments.parse_args()
        query = models.UserAuthLogs.query
        query = query.order_by(models.UserAuthLogs.created_at.desc())

        if args.get('users'):
            user = models.User.get_by_username(args.get('users'))
            if user:
                query = query.filter_by(user=user)

        limit = args['per_page']
        start = (args['page'] - 1) * limit

        query = query.offset(start).limit(limit)
        result = []
        for log in query.all():
            result.append(dict(
                username=log.user.username,
                created_at=log.created_at.isoformat(),
                status=log.status,
                ip=log.ip
            ))
        if not result:
            return [], 404

        return result
