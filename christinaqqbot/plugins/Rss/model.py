class Rss:
    def __init__(self,
            name='',
            url='',
            user_id=-1,
            type='',
            group_id=-1,
            id=-1,
            describe='',
            activate=True
    ):
        self.id=id
        self.name=name
        self.url=url
        self.user_id=user_id
        self.type=type
        self.group_id=group_id
        self.describe=describe
        self.activate=activate

class Item:
    def __init__(self,
            rss_id:str,
            title:str,
            link:str,
            id=-1
    ):
        self.id=id
        self.rss_id=rss_id
        self.title=title
        self.link=link
