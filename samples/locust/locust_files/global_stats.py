from locust import HttpUser, TaskSet, task, constant_pacing, events
# from locust.stats import RequestStats
# from locust.stats import global_stats

class UserTaskSet(TaskSet):
    @task(1)
    def test(self):
        self.client.get(url="/sample", verify=False)

@events.test_stop.add_listener
def test_stop(**kwargs):
    # global_stats = RequestStats()
    # print(vars(kwargs['environment']))
    item = kwargs['environment'].stats.get('/sample', 'GET')
    print(item)
    print(vars(item))
    # print(global_stats.get('/sample', 'GET'))

class WebsiteUser(HttpUser):
    tasks = [UserTaskSet]
    wait_time = constant_pacing(1)

    host = 'http://localhost:8080'
