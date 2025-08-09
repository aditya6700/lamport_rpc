import xmlrpc.client

proxy = xmlrpc.client.ServerProxy("http://localhost:8000/")
result = proxy.add(10, 5)
print("Result from remote 'add':", result)
