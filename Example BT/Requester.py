import collections

import requests
from io import BytesIO
from PIL import Image


url = 'https://parsemachine.com/b2b/parsing/'
url2 = 'https://wallpaper.forfun.com/fetch/e4/e4fac1b5f1d94ae90c6f2616841e1076.jpeg?h=900&r=0.5'
response = requests.get(url)

print(response.raw)

print(response.headers)
print(response.cookies)





