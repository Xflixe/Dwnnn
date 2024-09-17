# Import necessary libraries
import imaplib
from email.header import decode_header
from email import policy
from email.parser import BytesParser
import requests
import time
import re
from colorama import Fore, Style, init
from faker import Faker
import random
import string
import urllib.request

# Initialize colorama and Faker
init(autoreset=True)
fake = Faker()

# Replace with your actual credentials
imap_username = "linkinajak@hotmail.com"
imap_password = "Cepiring123"

# Function to generate email addresses
def generate_email1(email):
    username, domain = email.split('@')
    random_text = ''.join(random.choices(string.ascii_letters, k=8))  # Generate random text of length 8
    return f"{username}+{random_text}@{domain}"

# Function to choose a random proxy from proxy.txt file
def choose_random_proxy():
    with open('proxy.txt', 'r') as file:
        proxies = file.read().strip().split('\n')
    return {'http': random.choice(proxies)}

# Function to perform HTTP request with a random proxy
def http_request_with_random_proxy(method, url, **kwargs):
    while True:
        proxy = choose_random_proxy()
        try:
            response = requests.request(method, url, proxies=proxy, **kwargs)
            return response
        except requests.exceptions.RequestException as e:
            print(f"Gagal menggunakan proxy {proxy}: {str(e)}")
            continue

# Function to extract OTP from email body
def extract_otp(body):
    otp_match = re.search(r'Here is your Pixelverse OTP: (\d+)', body)
    if otp_match:
        return otp_match.group(1)
    return None

# Function to request OTP
def request_otp(email_address):
    response = http_request_with_random_proxy('POST', 'https://api.pixelverse.xyz/api/otp/request', json={'email': email_address})
    return response.status_code == 200

# Function to verify OTP
def verify_otp(email_address, otp):
    response = http_request_with_random_proxy('POST', 'https://api.pixelverse.xyz/api/auth/otp', json={'email': email_address, 'otpCode': otp})
    if response.status_code in [200, 201]:
        refresh_token_cookie = response.cookies.get('refresh-token')
        try:
            data = response.json()
        except ValueError:
            print(f"Respon JSON tidak valid untuk {email_address}. Status: {response.status_code}, Respon: {response.text}")
            return None

        data['refresh_token'] = refresh_token_cookie
        if 'tokens' in data and 'access' in data['tokens']:
            data['access_token'] = data['tokens']['access']
            return data
        else:
            print(f"Respon tidak mengandung tokens['access'] untuk {email_address}. Respon: {data}")
    else:
        print(f"Verifikasi OTP gagal. Status: {response.status_code}, Respon: {response.text}")
    return None

# Function to set referral
def set_referral(referral_code, access_token):
    headers = {
        'Authorization': access_token,
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Origin': 'https://dashboard.pixelverse.xyz',
        'Referer': 'https://dashboard.pixelverse.xyz/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, seperti Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
    referral_url = f'https://api.pixelverse.xyz/api/referrals/set-referer/{referral_code}'
    response = http_request_with_random_proxy('PUT', referral_url, headers=headers)
    try:
        response_json = response.json()
    except ValueError:
        response_json = None
    return response.status_code, response_json

# Function to claim daily reward
def claim_daily_reward(access_token):
    url = "https://api.pixelverse.xyz/api/daily-reward/complete"
    headers = {
        'Authorization': access_token1,
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Origin': 'https://dashboard.pixelverse.xyz',
        'Referer': 'https://dashboard.pixelverse.xyz/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, seperti Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
    try:
        response = requests.post(url, headers=headers)
        if response.status_code in [200, 201]:
            print(Fore.GREEN + Style.BRIGHT + "Daily reward berhasil diklaim!")
            return True
        else:
            print(Fore.RED + Style.BRIGHT + f"Gagal mengklaim daily reward. Status: {response.status_code}, Respon: {response.text}")
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"Gagal mengklaim daily reward: {str(e)}")
    return False

# Function to select pet
def select_pet(access_token, pet_data):
    pet_id = pet_data['id']
    url = f"https://api.pixelverse.xyz/api/pets/user-pets/{pet_id}/select"
    headers = {
        'Authorization': access_token,
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Origin': 'https://dashboard.pixelverse.xyz',
        'Referer': 'https://dashboard.pixelverse.xyz/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, seperti Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        print(Fore.GREEN + Style.BRIGHT + "Pet berhasil dipilih!")
        return True
    elif response.status_code == 201:
        print(Fore.GREEN + Style.BRIGHT + "Pet sudah dipilih sebelumnya.")
        return True
    elif response.status_code == 400 and response.json().get('message') == "You have already selected this pet":
        print(Fore.GREEN + Style.BRIGHT + "Pet berhasil dipilih!")
        return True
    else:
        print(Fore.RED + Style.BRIGHT + f"Gagal memilih pet. Status: {response.status_code}, Respon: {response.text}")
    return False

# Function to buy a pet using the access token
def buy_pet(access_token, pet_id):
    url = f"https://api.pixelverse.xyz/api/pets/{pet_id}/buy"
    headers = {
        'Authorization': access_token,
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Origin': 'https://dashboard.pixelverse.xyz',
        'Referer': 'https://dashboard.pixelverse.xyz/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, seperti Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
    response = http_request_with_random_proxy('POST', url, headers=headers)
    try:
        response_json = response.json()
    except ValueError:
        response_json = None
    return response.status_code, response_json

# Function to update username and biography
def update_username_and_bio(access_token):
    url = "https://api.pixelverse.xyz/api/users/@me"
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'Authorization': access_token,
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
        'Origin': 'https://dashboard.pixelverse.xyz',
        'Referer': 'https://dashboard.pixelverse.xyz/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, seperti Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
    username = fake.user_name()
    biography = fake.sentence()
    payload = {
        "updateProfileOptions": {
            "username": username,
            "biography": biography
        }
    }
    response = http_request_with_random_proxy('PATCH', url, headers=headers, json=payload)
    if response.status_code == 200:
        print(Fore.GREEN + Style.BRIGHT + f"Username berhasil diperbarui menjadi: {username}")
        print(Fore.GREEN + Style.BRIGHT + f"Bio berhasil diperbarui menjadi: {biography}")
    else:
        print(Fore.RED + Style.BRIGHT + f"Gagal memperbarui username. Status: {response.status_code}, Respon: {response.text}")
    return response.status_code == 200

# Function to connect and login to IMAP with proxy without authentication
def connect_imap(username, password):
    proxy = choose_random_proxy()
    proxy_handler = urllib.request.ProxyHandler(proxy)
    opener = urllib.request.build_opener(proxy_handler)
    urllib.request.install_opener(opener)

    mail = imaplib.IMAP4_SSL("imap-mail.outlook.com", 993)
    mail.login(username, password)
    return mail

# Function to search unread email with a specific subject using proxy
def search_unseen_email(mail, subject, username, password):
    folders = ["inbox", "junk"]
    for folder in folders:
        try:
            mail.select(folder)
        except (imaplib.IMAP4.abort, imaplib.IMAP4.error):
            # Reconnect if connection is lost
            print("Koneksi IMAP terputus, mencoba menghubungkan kembali...")
            mail = connect_imap(username, password)
            mail.select(folder)
        
        status, messages = mail.search(None, 'UNSEEN')
        email_ids = messages[0].split()

        for email_id in reversed(email_ids):
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = BytesParser(policy=policy.default).parsebytes(response_part[1])
                    msg_subject = decode_header(msg["Subject"])[0][0]
                    if isinstance(msg_subject, bytes):
                        msg_subject = msg_subject.decode()
                    if subject in msg_subject:
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                if content_type == "text/plain":
                                    body = part.get_payload(decode=True).decode()
                                    return body
                        else:
                            body = msg.get_payload(decode=True).decode()
                            return body
    return None

# Function to run the bot
def main():
    while True:
        try:
            choice = 2  # Assuming you want to proceed with the referral process

            if choice == 1:
                count = 100
                email_prefix = imap_username
                emails = [generate_email1(email_prefix) for _ in range(count)]

                continue_choice = input("Email berhasil di-generate. Apakah Anda ingin melanjutkan ke referral? (Y/N): ").strip().upper()
                if continue_choice == 'Y':
                    choice = 2
                else:
                    print(Fore.GREEN + Style.BRIGHT + "Proses dihentikan.")
                    break

            if choice == 2:
                print(Fore.YELLOW + "Menghubungkan ke server email...")
                mail = connect_imap(imap_username, imap_password)
                print(Fore.GREEN + "Berhasil terhubung ke server email.")

                email_prefix = imap_username
                desired_referrals = 100
                emails = [generate_email1(email_prefix) for _ in range(desired_referrals)]
                
                with open('reff.txt', 'r') as file:
                    referral_code = file.read().strip()

                successful_emails = []
                for index, email_address in enumerate(emails, start=1):
                    if len(successful_emails) >= desired_referrals:
                        break
                    print(Fore.CYAN + Style.BRIGHT + f"Proses email Ke-{index}: {email_address}")
                    if request_otp(email_address):
                        print(Fore.YELLOW + Style.BRIGHT + f"OTP diminta untuk {email_address}. Tunggu beberapa detik...")
                        time.sleep(10)  # Wait a few seconds to receive the OTP email

                        otp_subject = "Pixelverse Authorization"  # Sesuaikan dengan subjek email OTP
                        otp_body = search_unseen_email(mail, otp_subject, imap_username, imap_password)

                        if otp_body:
                            otp_code = extract_otp(otp_body)
                            if otp_code:
                                print(Fore.GREEN + Style.BRIGHT + f"OTP diterima: {otp_code}")
                                auth_data = verify_otp(email_address, otp_code)

                                if auth_data and 'access_token' in auth_data:
                                    access_token = auth_data['access_token']
                                    print(Fore.GREEN + Style.BRIGHT + f"Token akses diterima")
                                    status_code, response_json = set_referral(referral_code, access_token)
                                    if status_code in [200, 201]:
                                        print(Fore.GREEN + Style.BRIGHT + "Referral set berhasil.")
                                        if update_username_and_bio(access_token):
                                            pet_id = "27977f52-997c-45ce-9564-a2f585135ff5"  # Ganti dengan ID hewan peliharaan yang sebenarnya
                                            pet_status, pet_data = buy_pet(access_token, pet_id)
                                            if pet_status in [200, 201]:
                                                if select_pet(access_token, pet_data):
                                                    if claim_daily_reward(access_token):
                                                        print(Fore.BLUE + Style.BRIGHT + f"Referral Ke-{index} Berhasil")
                                                        successful_emails.append(email_address)
                                                        with open('sukses.txt', 'a') as success_file:
                                                            success_file.write(email_address + '\n')
                                                else:
                                                    print(Fore.RED + Style.BRIGHT + f"Referral Ke-{index} Gagal: Gagal memilih hewan peliharaan.")
                                            else:
                                                print(Fore.RED + Style.BRIGHT + f"Referral Ke-{index} Gagal: Gagal membeli hewan peliharaan.")
                                        else:
                                            print(Fore.RED + Style.BRIGHT + f"Referral Ke-{index} Gagal: Gagal memperbarui nama pengguna dan bio.")
                                    else:
                                        print(Fore.RED + Style.BRIGHT + f"Referral set gagal untuk {email_address}. Status: {status_code}, Respon: {response_json}")
                                        print(Fore.RED + Style.BRIGHT + f"Referral Ke-{index} Gagal")
                                else:
                                    print(Fore.RED + Style.BRIGHT + f"Verifikasi OTP gagal untuk {email_address}. Tidak ada access_token dalam respon.")
                                    print(Fore.RED + Style.BRIGHT + f"Referral Ke-{index} Gagal")
                            else:
                                print(Fore.RED + Style.BRIGHT + f"Tidak dapat mengekstrak OTP untuk {email_address}.")
                                print(Fore.RED + Style.BRIGHT + f"Referral Ke-{index} Gagal")
                        else:
                            print(Fore.RED + Style.BRIGHT + f"Tidak dapat menemukan email OTP untuk {email_address}.")
                            print(Fore.RED + Style.BRIGHT + f"Referral Ke-{index} Gagal")
                    else:
                        print(Fore.RED + Style.BRIGHT + f"Permintaan OTP gagal untuk {email_address}.")
                        time.sleep(60)
                        print(Fore.RED + Style.BRIGHT + f"Referral Ke-{index} Gagal")

                failed_emails = [email_address for email_address in emails if email_address not in successful_emails]

                with open('data2.txt', 'w') as file:
                    for email_address in failed_emails:
                        file.write(email_address + '\n')

                mail.logout()  # This ends the IMAP session

            else:
                print(Fore.RED + Style.BRIGHT + "Pilihan tidak valid.")
                break  # Stop the loop if choice is not valid

        except Exception as e:
            print(Fore.RED + f"Terjadi kesalahan: {e}")
            print(Fore.YELLOW + "Mengulangi koneksi dalam 5 detik...")
            time.sleep(5)  # Menunggu 5 detik sebelum mencoba koneksi kembali

if __name__ == "__main__":
    main()
