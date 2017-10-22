import requests
import datetime
from decimal import Decimal
from flask import current_app
from flask_security.utils import send_mail


class Article:
    def __init__(self, attr_dict=None, **kwargs):
        args = attr_dict or kwargs
        # hash key
        self.url = args.get('url')

        self.domain = args.get('domain', None)
        self.title = args.get('title', None)
        self.content = args.get('content', None)
        self.date_published = args.get('date_published', None)
        self.image_url = args.get('image_url', None)
        raw_word_count = args.get('word_count', None)
        self.word_count = Decimal(raw_word_count) if raw_word_count else None
        self.excerpt = args.get('excerpt', None)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Share:
    def __init__(self, attr_dict=None, **kwargs):
        # required attributes for init: sender_email, receiver_email, url
        args = attr_dict or kwargs

        self.sender_email = args.get('sender_email')
        self.receiver_email = args.get('receiver_email')

        # hash key
        self.email_key = self.sender_email + ',' + self.receiver_email
        # range key
        self.url = args.get('url')

        self.share_date = args.get('share_date', datetime.datetime.utcnow())
        self.tags = args.get('tags', [])
        self.is_read = args.get('is_read', False)
        self.is_archived = args.get('is_archived', False)
        self.is_trash = args.get('is_trash', False)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def add_tag(self, tag):
        if tag not in self.tags:
            self.tags.append(tag)
            return tag

    def remove_tag(self, tag):
        try:
            self.tags.remove(tag)
            return tag
        except ValueError:
            pass


class ShareManager:
    def __init__(self, dynamo_conn):
        self._db = dynamo_conn

    @staticmethod
    def parse_url(url):
        """
        Hits the Postlight Labs Mercury API to parse article contents at a URL and return a json/dict object.

        :param url: clean URL (stripped of params by JS requesting client)
        :return: dict object of article properties
        """
        mercury_base = 'https://mercury.postlight.com/parser'
        mercury_key = current_app.config['MERCURY_KEY']
        key = {'x-api-key': mercury_key}
        share_url = {'url': url}

        parsed = requests.get(mercury_base, headers=key, params=share_url)
        if parsed.status_code == 200:
            return parsed.json()

    def generate_article(self, data):
        """
        Creates a new Article instance, using response from Mercury API.
        Saves the article to db.

        :param data: dict format article attributes
        :return: Article object, if successfully saved
        """
        new_article = Article(
            url=data['url'],
            domain=data['domain'],
            title=data['title'],
            content=data['content'],
            excerpt=data['excerpt'],
            image_url=data['lead_image_url'],
            word_count=data['word_count'],
            date_published=data['date_published'],
        )
        print("new article:", vars(new_article))
        return self._db.put_model(new_article)

    def generate_share(self, url, sender_email, receiver_email):
        """
        Given a sender, receiver, and URL, creates a Share instance (internally generates a unique Article
        instance if that URL hasn't yet been shared on GV). Send a notification to the receiver, saves the
        Share object to db.

        :param url: clean URL (stripped of params by JS requesting client)
        :param sender_email:
        :param receiver_email:
        :return: Share object, if successful
        """

        # returns an existing article, or None
        article = self._db.article_table.get_article(url)
        if not article:
            parsed = self.parse_url(url)
            if parsed:
                article = self.generate_article(parsed)

        new_share = Share(
            sender_email=sender_email,
            receiver_email=receiver_email,
            url=article.url
        )

        sender_user = self._db.user_table.get(sender_email)

        # send a notification to the receiver
        truncated_title = article.title if len(article.title) < 50 else article.title[:50] + '...'
        email_subject = current_app.config['EMAIL_SUBJECT_NEW_SHARE'].format(
            sender_user.first_name,
            truncated_title
        )
        template_string = 'new_share'
        send_mail(
            email_subject,
            receiver_email,
            template_string,
            user=sender_user,
            excerpt=article.excerpt
        )

        return self._db.put_model(new_share)

    def list_shares_with_articles(self, sender_email, receiver_email):
        shares = self._db.article_table.list_received_shares(sender_email, receiver_email)
        response_package = []
        for share in shares:
            article = self._db.article_table.get_article(share.url)
            response_package.append((share, article))

        return response_package








