import json
import uuid
import base64
from time import sleep

from tencentcloud.tmt.v20180321 import models

import settings
from common.auth import get_tmt_auth_client


class AudioTranslation:

    def __init__(self, **kwargs):
        self.client = get_tmt_auth_client()
        self.task_id = str(uuid.uuid4().hex)
        self.project_id = kwargs.get('project_id') or 0
        self.region = kwargs.get('region') or settings.REGION
        self.inlang = kwargs.get('source') or 'zh'
        self.outlang = kwargs.get('target') or 'en'
        self.format = kwargs.get('format') or 83886080

    def process_from_file(self, filepath: str) -> dict:
        task = self.create_task_from_file(filepath)
        result = self.query_task(task['Data']['TaskId'])
        return result

    def create_task_from_file(self, filepath: str) -> dict:
        # Doc: https://cloud.tencent.com/document/api/551/16611
        with open(filepath, 'rb') as f:
            data = f.read()
            base64_dstr = base64.b64encode(data).decode()

        req = models.SpeechTranslateRequest()
        params = {
            'Action': 'SpeechTranslate',
            'Version': '2018-03-21',
            'SessionUuid': self.task_id,
            'ProjectId': self.project_id,
            'Region': self.region,
            'Source': self.inlang,
            'Target': self.outlang,
            'AudioFormat': self.format,
            'Seq': 0,
            'IsEnd': 1,
            "Data": base64_dstr,
        }
        req.from_json_string(json.dumps(params))
        print(f'Uploading file {filepath}...')
        resp = self.client.SpeechTranslate(req)
        reply = json.loads(resp.to_json_string())
        print(f'Crated a task {reply} for {filepath}')
        return reply

    def query_task(self) -> dict:
        status = 0
        while status in [0, 1]:
            print('Fetching result...')
            try:
                result = self.query_task_once(self.task_id)
            except Exception as ex:
                print(ex)
                continue
            status = result['Data']['Status']
            sleep(5)
        print('Fetched result:')
        return result

    def query_task_once(self) -> dict:
        req = models.DescribeTaskStatusRequest()
        req.from_json_string(json.dumps({'TaskId': self.task_id}))
        resp = self.client.DescribeTaskStatus(req)
        reply = json.loads(resp.to_json_string())
        return reply


def main():
    # From local file
    result = AudioTranslation().process_from_file('./samples/sample.mp3')
    print(result)
    with open('/tmp/transcript.txt', 'w') as f:
        f.write(json.dumps(result))
    print('[ OK ]')


if __name__ == '__main__':
    main()
