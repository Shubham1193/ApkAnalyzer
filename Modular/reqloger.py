from mitmproxy import http


def request(flow: http.HTTPFlow) -> None:
    """
    This function is called whenever a new HTTP request is intercepted.
    """

    # Open the log file in append mode
    with open("requests.log", "a") as logfile:
        # Write the request URL
        logfile.write(f"URL: {flow.request.url}\n")

        # Write the request headers
        logfile.write("Headers:\n")
        for key, value in flow.request.headers.items():
            logfile.write(f"\t{key}: {value}\n")

        # Optionally, write the request body (be aware of large bodies)
        if len(flow.request.content) < 1024:  # Limit body size for safety
            logfile.write(f"Body: {flow.request.text}\n")

        logfile.write("\n")  # Add a newline for better readability


def response(flow: http.HTTPFlow) -> None:
    """
    This function can be used to log response information if needed.
    """
    pass  # You can log responses here if needed


# No need to manually register functions with mitmproxy; it does this automatically
