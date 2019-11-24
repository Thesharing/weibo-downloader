from pyweibo import Auth, Client
from spiderutil.connector import Database, MongoDB
from spiderutil.path import PathGenerator, StoreByUserName
from spiderutil.typing import MediaType
from spiderutil.network import Session


class WeiboSpider:

    def __init__(self, db: Database = None,
                 path: PathGenerator = None,
                 session: Session = None):
        self.db = MongoDB('weibo',
                          primary_search_key='id') if db is None else db
        self.path = StoreByUserName('./download') if path is None else path
        self.session = Session(timeout=10, retry=5) \
            if session is None else session

        auth = Auth()
        self.token = auth.token.token
        self.client = Client()

    def list(self, page=1):
        running = True
        while running:
            data = self.client.favorites.get(access_token=self.token, page=page)
            if len(data.favorites) <= 0:
                break
            for item in data.favorites:
                if item.status.id not in self.db:
                    yield item.status
                else:
                    running = False
                    break
            page += 1

    def download(self, status):
        if 'deleted' not in status:
            user = status.user.name
            for item in status.pic_urls:
                url = item.thumbnail_pic.replace('thumbnail', 'large')
                path = self.path.generate(user_name=user,
                                          media_type=MediaType.image)
                r = self.session.get(url)
                with open(path, 'wb') as f:
                    f.write(r.content)
        self.db.add(status.id)
