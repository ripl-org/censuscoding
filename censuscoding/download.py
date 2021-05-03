E911_URLS = {
  "RI": "..."
}
TIGER_URLS = {
  "RI": "..."
}

class Downloader(obj):
  
  def __init__(e911_url, tiger_url):
    

def state_exists(state):
  return state in E911_URLS and state in TIGER_URLS

def DownloadFactory(state):
  return Downloader(E911_URLS[state], TIGER_URLS[state])
