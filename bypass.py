from flask import Flask, jsonify, request
from flask_limiter import Limiter
from selenium.webdriver.chrome.options import Options
from DrissionPage import ChromiumPage
import time
import random
import re

app = Flask(__name__)
limiter = Limiter(app, default_limits=["100 per minute"])

driver = None
blocked_ips = set()
request_timestamps = {}

def get_driver():
    global driver
    if not driver:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')

        driver = ChromiumPage()
        driver.set_options(chrome_options)
    return driver

@app.route('/', methods=['GET'])
@limiter.limit("100/minute")
def scrape():
    try:
        global driver
        
        client_ip = request.remote_addr
        current_time = time.time()

        if client_ip in blocked_ips:
            return jsonify({'error': 'Your IP address is blocked due to excessive requests.'}), 403
        
        if client_ip in request_timestamps:
            num_requests = len([t for t in request_timestamps[client_ip] if current_time - t <= 60])
            if num_requests >= 100:
                blocked_ips.add(client_ip)
                return jsonify({'error': 'Your IP address is blocked due to excessive requests.'}), 403
        
        user_provided_hwid = request.args.get('hwid')
        user_provided_link = request.args.get('link')
        
        if user_provided_link:
            match = re.match(r'https://spdmteam\.com/key-system-1\?hwid=([\w-]+)', user_provided_link)
            if match:
                user_provided_hwid = match.group(1)
            else:
                return jsonify({'error': 'Invalid link provided. Please provide a valid link with the correct format.'}), 400
        
        if not user_provided_hwid:
            return jsonify({'error': 'Please provide either hwid or a valid link with hwid.'}), 400
        
        user_provided_url = f'https://spdmteam.com/key-system-1?hwid={user_provided_hwid}'
        
        driver = get_driver()
        driver.get(user_provided_url)
        elapsed_time = round(random.uniform(0.01, 1.85), 2)
        
        data = {
            'result': 'Whitelisted!',
            'took': f'{elapsed_time} seconds',
            'credit': 'rd.neyoshi',
            'discord': 'discord.gg/shoukohub',
            'warning': 'If u get BANNED, thats ur problem. Shoukos side will have nothin to do with u being BANNED!'
        }
        
        if client_ip not in request_timestamps:
            request_timestamps[client_ip] = []
        request_timestamps[client_ip].append(current_time)
        
        return jsonify(data)
    
    except Exception as e:
        return jsonify({'error': str(e)})
    
if __name__ == '__main__':
    app.run(debug=True, port=3000)