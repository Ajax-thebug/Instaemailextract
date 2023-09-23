import csv
import time
import random
from instagpy import InstaGPy
from requests.exceptions import HTTPError

def main():
    # Initialize InstaGPy
    insta = InstaGPy(use_mutiple_account=False, session_ids=None,
                     min_requests=None, max_requests=None)

    # Replace 'your_username' and 'your_password' with your Instagram credentials
    username = 'your_username'
    password = 'your_password'

    # List of usernames you provided
    target_usernames_or_user_ids = [
    'quick.bits',
    ]

    # Generate a random unique number
    unique_number = random.randint(1000, 9999)

    # List to keep track of processed profiles
    processed_profiles = []

    try:
        # Log in to Instagram
        logged_in = False
        retries = 0
        while not logged_in and retries < 3:  # Retry login up to 3 times
            insta.login(username=username, password=password, show_saved_sessions=False, save_session=True)
            if insta.logged_in():
                logged_in = True
            else:
                print(f"Couldn't log in. Retrying in 60 seconds...")
                time.sleep(60)
                retries += 1

        if not logged_in:
            print("Login failed after multiple retries.")
            return

        # Check if logged in
        if insta.logged_in():
            # Create a CSV file with a random unique number combined with the first username
            csv_filename = f'user_data_{target_usernames_or_user_ids[0]}_{unique_number}.csv'
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(['Username', 'Email', 'Followers'])

                for target in target_usernames_or_user_ids:
                    if target in processed_profiles:
                        print(f"Skipping {target} as it has already been processed.")
                        continue

                    try:
                        # Get user details with contact information
                        user_data = None
                        retries = 0
                        while user_data is None and retries < 3:  # Retry profile request up to 3 times
                            user_data = insta.get_user_data(target)
                            if user_data is None:
                                print(f"Failed to retrieve data for {target}. Retrying in 60 seconds...")
                                time.sleep(60)
                                retries += 1

                        if user_data is not None:
                            # Extract relevant information
                            username = user_data['user']['username']
                            email = user_data['user']['public_email']
                            followers = user_data['user']['follower_count']
                            
                            # Write the data to the CSV file
                            csv_writer.writerow([username, email, followers])

                            # Add the profile to the list of processed profiles
                            processed_profiles.append(target)
                        else:
                            print(f"{target} not found on Instagram - Writing to CSV")
                            csv_writer.writerow([target, "Not found on Instagram", "N/A"])
                    except HTTPError as e:
                        if e.response.status_code == 429:
                            print(f"Rate-limit error for {target}. Waiting and retrying...")
                            time.sleep(600)  # Wait for 10 minutes before retrying
                            continue  # Retry the same profile after waiting
                        elif e.response.status_code == 404:
                            print(f"{target} not found on Instagram - Writing to CSV")
                            csv_writer.writerow([target, "Not found on Instagram", "N/A"])
                        else:
                            print(f"An error occurred for {target}: {e}")
                            continue  # Skip to the next account on error
                    except Exception as e:
                        print(f"An error occurred for {target}: {e}")
                        continue  # Skip to the next account on error

                    # Add a delay of 6 seconds between requests
                    time.sleep(6)

            print(f"User data saved to {csv_filename}")
        else:
            print("Login failed.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
