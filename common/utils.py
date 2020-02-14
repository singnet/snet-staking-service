import json

import requests


class Utils:
    def __init__(self):
        pass

    def report_slack(self, slack_msg, SLACK_HOOK):
        url = SLACK_HOOK['hostname'] + SLACK_HOOK['path']
        slack_channel = SLACK_HOOK.get("channel", "contract-index-alerts")
        payload = {"channel": f"#{slack_channel}",
                   "username": "webhookbot",
                   "text": slack_msg,
                   "icon_emoji": ":ghost:"
                   }

        response = requests.post(url=url, data=json.dumps(payload))
        return response

    def remove_http_https_prefix(self, url):
        url = url.replace("https://", "")
        url = url.replace("http://", "")
        return url

    def make_response(status_code, body, header=None):
        return {
            "statusCode": status_code,
            "headers": header,
            "body": body
        }

    def validate_dict(self, data_dict, required_keys):
        for key in required_keys:
            if key not in data_dict:
                return False
        return True

    def make_response_body(status, data, error):
        return {
            "status": status,
            "data": data,
            "error": error
        }

    def generate_lambda_response(self, status_code, message, headers=None, cors_enabled=False):
        response = {
            "statusCode": status_code,
            "body": json.dumps(message),
            "headers": {"Content-Type": "application/json"}
        }
        if cors_enabled:
            response["headers"].update({
                "X-Requested-With": "*",
                "Access-Control-Allow-Headers": "Access-Control-Allow-Origin, Content-Type, X-Amz-Date, Authorization,"
                                                "X-Api-Key,x-requested-with",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET,OPTIONS,POST"
            })
        if headers is not None:
            response["headers"].update(headers)
        return response

    def extract_payload(self, method, event):
        method_found = True
        payload_dict = None
        path_parameters = event.get("pathParameters", None)
        if method == "POST":
            payload_dict = json.loads(event["body"])
        elif method == "GET":
            payload_dict = event.get("queryStringParameters", {})
        else:
            method_found = False
        return method_found, path_parameters, payload_dict

    def format_error_message(self, status, error, payload, net_id, handler=None, resource=None, trace_id=None):
        return json.dumps(
            {"status": status, "error": error, "resource": resource, "trace_id": trace_id, "payload": payload,
             "network_id": net_id,
             "handler": handler})

    def bits_to_integer(self, value):
        if value == b'\x01':
            return 1
        elif value == b'\x00':
            return 0
        else:
            raise Exception("Invalid parameter value")
