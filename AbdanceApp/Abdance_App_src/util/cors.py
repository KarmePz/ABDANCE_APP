from flask import jsonify, make_response


def apply_cors(response_tuple):
    # headers = {
    #     'Access-Control-Allow-Origin': 'http://localhost:5173',  # o '*' para todos
    #     'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    #     'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    # }
    data, status = response_tuple
    response = make_response(jsonify(data), status)
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
    return response
    # return (response_body, status, headers)