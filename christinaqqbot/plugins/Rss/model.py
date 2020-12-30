
class Rss:
    def __init__(self,
            name:str,
            url:str,
            user_id:int,
            type:str,
            group_id:int,
            id=-1
    ):
        self.id=id
        self.name=name
        self.url=url
        self.user_id=user_id
        self.type=type
        self.group_id=group_id

class Item:
    def __init__(self,
            rss_name:str,
            rss_id:str,
            title:str,
            link:str,
            id=-1
    ):
        self.id=id
        self.rss_name=rss_name
        self.rss_id=rss_id
        self.title=title
        self.link=link
