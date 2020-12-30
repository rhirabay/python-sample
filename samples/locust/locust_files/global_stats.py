from locust import HttpUser, TaskSet, task, constant_pacing, events
import slackweb
import os

class UserTaskSet(TaskSet):
    @task(1)
    def sample(self):
        self.client.get(url="/sample", verify=False, timeout=0.5)

class WebsiteUser(HttpUser):
    tasks = [UserTaskSet]
    wait_time = constant_pacing(1)

    host = 'http://localhost:8080'

@events.test_stop.add_listener
def test_stop(**kwargs):
    slack = slackweb.Slack(url="https://hooks.slack.com/services/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")

    # テストOKのカラー
    color_success = "#00ff00"
    # テストNGのカラー
    color_failed = "#cc3366"

    failure_threshold = int(os.environ.get("FAILURE_NG_THRESHOLD", 1))
    percentile_threshold = int(os.environ.get("PERCENTILE_NG_THRESHOLD", 10))

    for v in kwargs['environment'].stats.entries:
        item = kwargs['environment'].stats.get(v[0], v[1])

        is_failure_ok = item.num_failures < failure_threshold
        is_percentile_ok = item.get_response_time_percentile(99) < percentile_threshold
        mention = "<!here>\n" if not is_failure_ok or not is_percentile_ok else ""

        rps = {
            "title": "rps (info)",
            "color": color_success,
            "text": "{:.1f} r/s".format(item.total_rps),
            "mrkdwn_in": ["text"]}
        failure = {
            "title": "Failure",
            "color": color_success if is_failure_ok else color_failed,
            "text": "{} ( {}% )".format(item.num_failures, item.fail_ratio * 100),
            "mrkdwn_in": ["text"]}
        percentile = {
            "title": "99 Percentile",
            "color": color_success if is_percentile_ok else color_failed,
            "text": "{} ms".format(item.get_response_time_percentile(99)),
            "mrkdwn_in": ["text"]}
        slack.notify(
            text="{}Load test result of *{} {}*".format(mention, v[1], v[0]),
            attachments=[rps, failure, percentile])
