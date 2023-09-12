import datetime
import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from datetime import timedelta

from ...models import Category, Post

logger = logging.getLogger(__name__)


def sending_weekly_news():
    categories = Category.objects.all()
    posts = Post.objects.all()
    start_date = datetime.date.today() - timedelta(days=6)
    subs_news_result_list = {}

    for cat in categories:
        subscribers = cat.subscribers.all()
        if len(subscribers) > 0:
            weekly_news = posts.filter(
                postCategory__name=cat,
                dateCreation__gte=start_date,
            )

            for sub in subscribers:
                if sub not in subs_news_result_list:
                    subs_news_result_list[sub] = []
                subs_news_result_list[sub].extend(weekly_news)

    subs_news_result_list[sub] = set(subs_news_result_list[sub])

    for sub, posts in subs_news_result_list.items():
        html_content = render_to_string(
            template_name='mail/weeklynews.html',
            context={
                'user': sub,
                'posts': posts,
            },
        )
        msg = EmailMultiAlternatives(
            subject=f'!weekly news',
            body='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[sub.email],
        )
        msg.attach_alternative(html_content, 'text/html')
        msg.send()


# функция которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем работу нашему задачнику
        scheduler.add_job(
            sending_weekly_news,
            trigger=CronTrigger(second="*/10"),
            # Тоже самое что и интервал, но задача тригера таким образом более понятна django
            id="my_job",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить, либо уже выполнять не надо.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
