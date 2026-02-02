import flask


Scanner_bp = flask.Blueprint("Scanner", __name__)

@Scanner_bp.route("/getApproved",methods=['GET'])
def getApproved():
    return "hello"
@Scanner_bp.route("/getRejected", methods=['GET'])
def getRejected():
    return "world"
@Scanner_bp.route("/addApproved", methods=['POST'])
def addApproved():
    return "!"
@Scanner_bp.route("/updateApproved", methods=['PUT'])
def updateApproved():
    return "!#¤¤"
@Scanner_bp.route("/updateUnApproved", methods=['PUT'])
def updateUnApproved():
    return "!782346"
@Scanner_bp.route("/removeApproved", methods=['DELETE'])
def removeApproved():
    return "removed"
