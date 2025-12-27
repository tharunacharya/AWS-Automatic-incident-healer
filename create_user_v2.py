import boto3
import time

USER_POOL_ID = "us-east-1_I88NADkOf"
CLIENT_ID = "3fqsha67hhnu8o88sp42miva20"
USERNAME = "admin@example.com"
PASSWORD = "Password123!"

client = boto3.client('cognito-idp', region_name='us-east-1')

def create_user():
    print(f"Creating user {USERNAME} in pool {USER_POOL_ID}...")
    try:
        # Create user
        client.admin_create_user(
            UserPoolId=USER_POOL_ID,
            Username=USERNAME,
            TemporaryPassword=PASSWORD,
            MessageAction='SUPPRESS'
        )
        print("User created.")
        
        # Set permanent password
        client.admin_set_user_password(
            UserPoolId=USER_POOL_ID,
            Username=USERNAME,
            Password=PASSWORD,
            Permanent=True
        )
        print("Password set permanently.")
        
    except client.exceptions.UsernameExistsException:
        print("User already exists. Reselling password...")
        client.admin_set_user_password(
            UserPoolId=USER_POOL_ID,
            Username=USERNAME,
            Password=PASSWORD,
            Permanent=True
        )
        print("Password reset.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_user()
