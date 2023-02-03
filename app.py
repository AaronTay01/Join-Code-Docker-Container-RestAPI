from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class JoinCodeModel(db.Model):
    joinCode = db.Column(db.String(30), primary_key=True)
    allocationID = db.Column(db.String(100), nullable=False)

    def __repr__(self, joinCode=None, allocationID=None):
        return f"Join Code(joinCode = {joinCode}, allocationID = {allocationID})"


db.create_all()

joinCode_put_args = reqparse.RequestParser()
joinCode_put_args.add_argument("allocationID", type=str, help="Enter allocation ID", required=True)

resource_fields = {
    'joinCode': fields.String,
    'allocationID': fields.String
}


# def abort_if_joinCode_not_exist(joinCode):
#     if joinCode not in relayInfo:
#         abort(404, message="join code does not exist")
#
#
# def abort_if_joinCode_exist(joinCode):
#     if joinCode in relayInfo:
#         abort(409, message="join code already exist")

class JoinCode(Resource):
    @marshal_with(resource_fields)
    def get(self, joinCode):
        result = JoinCodeModel.query.filter_by(joinCode=joinCode).first()
        if not result:
            abort(408, message="join code doesn't exist")
        return result

    @marshal_with(resource_fields)
    def put(self, joinCode):
        args = joinCode_put_args.parse_args()
        result = JoinCodeModel.query.filter_by(joinCode=joinCode).first()
        if result:
            abort(409, message="join code exist")

        join_code = JoinCodeModel(joinCode=joinCode, allocationID=args['allocationID'])
        db.session.add(join_code)
        db.session.commit()
        return join_code, 201

    @marshal_with(resource_fields)
    def delete(self, joinCode):
        result = JoinCodeModel.query.filter_by(joinCode=joinCode).first()
        if not result:
            abort(405, message="join code doesn't exist, cannot delete")
        db.session.delete(result)
        db.session.commit()
        return result, 201


class JoinCodes(Resource):
    @marshal_with(resource_fields)
    def get(self):
        result = JoinCodeModel.query.all()
        return result

    def delete(self):
        try:
            num_rows_deleted = db.session.query(JoinCodeModel).delete()
            db.session.commit()
        except:
            db.session.rollback()
        result = JoinCodeModel.query.all()
        return result

@app.route('/')
def hello_world():
    return 'Hello World'


api.add_resource(JoinCode, "/joinCode/<string:joinCode>")
api.add_resource(JoinCodes, "/joinCodes")

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)