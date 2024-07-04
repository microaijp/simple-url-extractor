import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.getcwd(), '.env')
dotenv_local_path = os.path.join(os.getcwd(), '.env.local')


print(f"dotenv_path: {dotenv_path}")
print(f"dotenv_local_path: {dotenv_local_path}")

load_dotenv(dotenv_path=dotenv_local_path, override=True)
load_dotenv(dotenv_path=dotenv_path)