import json
import logging


def lambda_handler(event: dict, context: dict) -> dict:
    """
    AWS Lambda function handler.

    Args:
        event (dict): The event data passed to the function.
        context (dict): The context object containing runtime information.

    Returns:
        dict: A response dictionary with a status code and message.
    """
    logging.info("Event: %s", json.dumps(event))

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/plain"},
        "body": f"Hello from Lambda! {event['path']}",
    }
