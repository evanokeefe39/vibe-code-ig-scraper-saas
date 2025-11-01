#!/usr/bin/env python
import os
import django
import sys

# Add the project directory to the Python path
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vibe_scraper.settings')
django.setup()

from core.models import UserList, ListRow

def add_sample_data():
    try:
        l = UserList.objects.get(pk=12)
        print(f'List: {l.name}')
        print(f'Current rows: {l.rows.count()}')

        # Sample data
        sample_data = [
            {
                'Source': 'Instagram',
                'Created At': '2024-11-01',
                'profile URL': 'https://instagram.com/user1',
                'Post URL': 'https://instagram.com/p/123',
                'Post Caption': 'Beautiful sunset!',
                'Post Transcript': 'A stunning view of the sunset over the mountains',
                'Post Tags': '#sunset #nature #photography'
            },
            {
                'Source': 'Instagram',
                'Created At': '2024-11-02',
                'profile URL': 'https://instagram.com/user2',
                'Post URL': 'https://instagram.com/p/456',
                'Post Caption': 'Coffee time ☕',
                'Post Transcript': 'Enjoying my morning coffee at the local cafe',
                'Post Tags': '#coffee #morning #cafe'
            },
            {
                'Source': 'Instagram',
                'Created At': '2024-11-03',
                'profile URL': 'https://instagram.com/user3',
                'Post URL': 'https://instagram.com/p/789',
                'Post Caption': 'Workout complete!',
                'Post Transcript': 'Finished an intense workout session today',
                'Post Tags': '#fitness #workout #health'
            }
        ]

        created_count = 0
        for data in sample_data:
            row = ListRow.objects.create(user_list=l, data=data)
            print(f'Created row {row.pk}: {data["Post Caption"]}')
            created_count += 1

        print(f'Total created: {created_count}')
        print(f'Final count: {l.rows.count()}')

    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    add_sample_data()