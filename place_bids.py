import os
import time

import requests
from freelancersdk.resources.projects.exceptions import \
    BidsNotFoundException
from freelancersdk.resources.projects.exceptions import \
    ProjectsNotFoundException
from freelancersdk.resources.projects.helpers import (
    create_search_projects_filter,
)
from freelancersdk.resources.projects.projects import get_bids, place_project_bid
from freelancersdk.resources.projects.projects import search_projects
from freelancersdk.resources.users \
    import get_self_user_id
from freelancersdk.session import Session

freelancer_oauth_token = "rH3YHjcxedYAaG1rPvds78055lIRdq"
chat_id = "-870300319"

BOT_TOKEN = "5677829197:AAG77ldfVFcGSMUFD8_TY62ut2eIkG9Jlo4"
base_url = "https://api.telegram.org/bot" + BOT_TOKEN
offset = 0

time_interval = 60  # (in seconds) Specify the frequency of code execution

url = os.environ.get('FLN_URL')
bid_description = '''
★★★ Kotlin / Android Expert ★★★ 4+ Years of Experience ★★★
I have thoroughly been to your job posting news and I’m highly interested to apply for this job.

I am experienced in creating and developing new features of android apps and also very much skillful in shipping them in different groups with high satisfaction.

I have been in this sector for like 4 years now and pretty experienced in creating apps with using the proper app languages. I have highly proficiency in coding and programming as I have a bachelor degree in Software Engineering. Some of the technologies that I use are Kotlin, Clean Architecture, Coroutines, Room, Retrofit, Dependency Injection, and Jetpack Compose.
Highly skilled in building quality, feature-rich applications that are scalable, fast, and high-performing using industry best practices. Capable of building, testing, and releasing production-ready code independently with minimal supervision.

Also I can initiate a project skillfully and maintain the consistency diplomatically. I work collaborated with Cross-Functional groups and this experience has taught me about commercialism and tactful movement. As an Android Developer, I have created a technical group from where I can learn my mistakes and errors.

And I am content with the amount you have mentioned for the project so pick me up if you think I am worth the job.

Thank you.

Best regards
Igor Stevanovic
'''


def sample_search_projects():
    session = Session(oauth_token=freelancer_oauth_token, url=url)

    query = 'android'
    search_filter = create_search_projects_filter(
        sort_field='time_updated',
        min_avg_hourly_rate=20,
        project_types='hourly',
        or_search_query=True,
    )

    try:
        projects = search_projects(
            session,
            query=query,
            search_filter=search_filter,
            active_only=True
        )

    except ProjectsNotFoundException as e:
        print('Error message: {}'.format(e.message))
        print('Server response: {}'.format(e.error_code))
        return None
    else:
        return projects


while True:
    projects = sample_search_projects()
    time.sleep(time_interval)

    if projects:
        for project in projects.get('projects'):
            print("-------------------------------------------")
            print(project)
            title = project.get('title')

            project_id = project.get('id')

            session = Session(oauth_token=freelancer_oauth_token, url=url)
            my_user_id = get_self_user_id(session)

            get_bids_data = {
                'project_ids': [project_id],
                'limit': 25,
                'offset': 0,
            }

            maximum = project.get('budget').get('maximum')
            minimum = project.get('budget').get('minimum')
            minimum = 0 if minimum is None else minimum
            maximum = minimum if maximum is None else maximum
            amount = int((maximum + minimum) / 2)
            amount = amount if amount > 0 else 45

            try:
                bid = get_bids(session, **get_bids_data)
                if bid and project.get('status') == 'active' and (
                        project.get('currency').get('code') == 'USD'
                        or project.get('currency').get('code') == 'AUD'
                        or project.get('currency').get('code') == 'EUR'
                        or project.get('currency').get('code') == 'GBP'
                ):
                    print('Found bids: {}'.format(len(bid['bids'])))
                    if len(bid['bids']) < 15:
                        bid_data = {
                            'project_id': int(project_id),
                            'bidder_id': my_user_id,
                            'amount': amount,
                            'period': 7,
                            'milestone_percentage': 20,
                            'description': bid_description,
                        }

                        print(bid_data)
                        print('https://www.freelancer.com/projects/' + project.get('seo_url'))
                        message = 'https://www.freelancer.com/projects/' + project.get('seo_url')
                        b = place_project_bid(session, **bid_data)
                        if b:
                            print('*********************')
                            print(("Bid placed: %s" % b))
                            parameters = {
                                "chat_id": chat_id,
                                "text": message,
                            }
                            resp = requests.get(base_url + "/sendMessage", data=parameters)
            except BidsNotFoundException as e:
                print('Error message: {}'.format(e.message))
                print('Server response: {}'.format(e.error_code))
                continue
            except:
                continue
