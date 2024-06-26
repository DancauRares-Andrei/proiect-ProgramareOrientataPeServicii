# server.py
import grpc
import uuid
import jwt
from concurrent import futures
from datetime import datetime, timedelta
from user_pb2 import *
from user_pb2_grpc import *
from db import User,Role, db
blacklist = set()
class AuthService(AuthServiceServicer):
    def Authenticate(self, request, context):
        try:
            user = User.get((User.username == request.username) & (User.password == request.password))
            expiration_time = datetime.utcnow() + timedelta(hours=3)
            token_payload = {
                'iss': '[::]:50051',
                'sub': str(user.uid),
                'exp': expiration_time,
                'jti': str(uuid.uuid4()),
                'role': user.role.name
            }            
            token = jwt.encode(token_payload, 'your_secret_key', algorithm='HS256')
            print(f"Se autentifica {request.username} token:{token}")
            return AuthResponse(token=token)
        except User.DoesNotExist:
            print("A incercat sa se autentifice un utilizator care nu exista.")
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details("Invalid credentials.")
            return AuthResponse()
        except Exception as e:
            print(f"Exceptie in timpul autentificarii: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Internal server error.")
            return AuthResponse()

    def ValidateToken(self, request, context):
        global blacklist
        try:
            if request.token in blacklist:
                print("Token din blacklist:",request.token)
                context.set_code(grpc.StatusCode.OK)
                context.set_details("Token invalid.")
                return TokenResponse(valid=False, message="Invalid token.")
            decoded_token = jwt.decode(request.token, 'your_secret_key', algorithms=['HS256'])
            print(f'Token decodat: {decoded_token}')
            return TokenResponse(valid=True, sub=decoded_token['sub'], role=decoded_token['role'])
        except jwt.ExpiredSignatureError:
            context.set_code(grpc.StatusCode.OK)
            context.set_details("Token-ul a expirat.")
            blacklist.add(request.token)
            return TokenResponse(valid=False, message="Token-ul a expirat.")
        except jwt.InvalidTokenError:
            context.set_code(grpc.StatusCode.PERMISSION_DENIED)
            context.set_details("Token invalid.")
            blacklist.add(request.token)
            return TokenResponse(valid=False, message="Token invalid.")

    def DestroyToken(self, request, context):
        global blacklist     
        blacklist.add(request.token)
        print('Blacklisted:',request.token)
        return DestroyTokenResponse(success=True, message="Token distrus.")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_AuthServiceServicer_to_server(AuthService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()

