
from itsdangerous import URLSafeTimedSerializer

def generate_confirmation_token(email, config):
    serializer = URLSafeTimedSerializer(config['SECRET_KEY'])
    return serializer.dumps(email, salt=config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600, config=None):
    serializer = URLSafeTimedSerializer(config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email