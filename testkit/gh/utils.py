def iter_connection(conn: dict):
    """
    Iterate over a GraphQL Relay-style connection.
    """
    for i in conn["edges"]:
        yield i["node"]
