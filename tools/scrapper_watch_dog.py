import time
import requests
from bs4 import BeautifulSoup


def _login(email, password):
    authentication_url = 'https://reservatic.com/cs/users/sign_in'
    response = requests.get(authentication_url)
    soup = BeautifulSoup(response.text)
    token = soup.find('input', {'name': 'authenticity_token'}).get('value')

    data = {
        'authenticity_token': token,
        'user[email]': email,
        'user[password]': password,
        'commit': 'Přihlásit'
    }

    session = requests.session()
    session.post(authentication_url, data=data)
    return session


def _parse(session, file, start: int, stop: int):
    base_url = 'https://reservatic.com/watchdogs/new?locale=cs&operation_id=5867&place_id=2905&service_id='

    for i in range(start, stop):
        service_url = base_url + str(i)
        soup = _open_url(session, service_url)
        label = soup.find('label', {'for': 'watchdog_service_id'})
        if label:
            firma = str(label.next_sibling.next_sibling.next_sibling).strip()
            _write(file, firma, i)


def _open_url(session, url: str):
    # workaround login
    session = requests.session()
    session.cookies.set('_reservatic_session2020_a', '<session value>')
    # workaround login

    response = session.get(url)
    soup = BeautifulSoup(response.text)
    time.sleep(1)
    return soup


def _write(file, firma, service_id):
    file.write(firma + ';' + str(service_id) + '\n')


if __name__ == "__main__":
    session = _login('<email>', '<password>') # not needed to fill, login doesn't work - use session from your web browser
    file = open("out.csv", "a", encoding="utf-8")
    _parse(session, file, 411400, 412100)
    file.close()