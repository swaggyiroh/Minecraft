import random
import string
import requests
import concurrent.futures
import threading

lock = threading.Lock()  # Use threading.Lock for thread safety
usernames = []  # Define usernames at the module level

def generate_username():
    length = random.randint(2, 16)
    username = ''.join(random.choices(string.ascii_letters + string.digits + '_', k=length))
    
    # Ensure the username doesn't start or end with an underscore
    if username[0] == '_' or username[-1] == '_':
        return generate_username()
    
    return username

def get_uuid(username):
    url = f'https://api.mojang.com/users/profiles/minecraft/{username}'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data['id']  # UUID is stored in 'id'
        else:
            return None
    except requests.RequestException:
        return None

def check_username_exists(username):
    url = f'https://api.mojang.com/users/profiles/minecraft/{username}'
    try:
        response = requests.get(url)
        return response.status_code == 200
    except requests.RequestException:
        return False

def write_to_file(username, uuid):
    try:
        with open('valid_usernames.txt', 'a') as f:
            f.write(f"Username: {username}, UUID: {uuid}\n")
    except IOError as e:
        print(f"Failed to write to file: {e}")

def process_username():
    while len(usernames) < 20:  # Adjust as needed, to limit the number of valid usernames collected
        username = generate_username()
        
        if check_username_exists(username):
            uuid = get_uuid(username)
            if uuid:
                with lock:
                    usernames.append((username, uuid))
                write_to_file(username, uuid)
                print(f"Found! Valid username: {username}, UUID: {uuid}")
        else:
            print(f"Invalid Username: {username}")    
        

def main():
    num_threads = 5  # Number of threads to run concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(process_username) for _ in range(num_threads)]
        concurrent.futures.wait(futures)
    
    # Print valid usernames to console
    print("\nValid Usernames:")
    for username, uuid in usernames:
        print(f"Username: {username}, UUID: {uuid}")

if __name__ == "__main__":
    main()
