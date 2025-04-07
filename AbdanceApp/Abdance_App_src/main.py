import functions_framework 

@functions_framework.http
def main(request):
    if request.method == 'GET':
        return 'Hello World', 200 
    else:
        return 'Method not allowed', 405