from django.apps import AppConfig


class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'

    def ready(self):
        import news.signals

        # from .tasks import send_week_mails
        # from .scheduler import news_scheduler
        # print('START >>>')
        #
        # news_scheduler.add_job(
        #     id='send_newsweek_mail',
        #     func=send_week_mails,
        #     trigger='interval',
        #     seconds=10,
        # )
        # news_scheduler.start()
