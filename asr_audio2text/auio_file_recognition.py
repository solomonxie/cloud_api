"""
EngineModelType (Scenarios):
- Phone:
    • 8k_zh：电话 8k 中文普通话通用；
    • 8k_zh_finance：电话 8k 金融领域模型；
- Non-phone:
    • 16k_zh：16k 中文普通话通用；
    • 16k_en：16k 英语；
    • 16k_ca：16k 粤语；
    • 16k_ko：16k 韩语；
    • 16k_zh-TW：16k 中文普通话繁体；
    • 16k_ja：16k 日语。

Create task POST body:
    {
        "EngineModelType": "16k_0",
        "ChannelNum": 1,
        "ResTextFormat": 0,
        "SourceType": 1,
        "Data": "base64_data_string",
        "DataLen": data_binary_length
    }

Reply of creating task:
    {
        "Data": {"TaskId": 856184969},
        "RequestId": "c7e76487-64bc-45b0-95da-756f7eb928d1"
    }

Reply of query task:
    {
        "Data": {
            "Status": 2,
            "StatusStr": "success",
            "Result": "[0:0.000,0:1.540]  first_line\n",
            "TaskId": 737083613,
            "ErrorMsg": "",
            "ResultDetail": null
        },
        "RequestId": "4f87d14f-8b0f-4970-b517-eaf8c5df2e9d"
    }
"""
import json
import base64
from time import sleep

from tencentcloud.asr.v20190614 import models

from common.auth import get_asr_auth_client


class AudioRecognition:

    def __init__(self, **kwargs):
        self.client = get_asr_auth_client()
        self.scenario = kwargs.get('scenario') or '16k_zh'

    def process_from_file(self, filepath):
        task = self.create_task_from_file(filepath)
        result = self.query_task(task['Data']['TaskId'])
        return result

    def create_task_from_file(self, filepath: str) -> dict:
        # Doc: https://cloud.tencent.com/document/product/1093/35799
        with open(filepath, 'rb') as f:
            data = f.read()
            data_len = len(data)
            base64_wav = base64.b64encode(data).decode()

        req = models.CreateRecTaskRequest()
        params = {
            "EngineModelType": "16k_0",
            "ChannelNum": 1,
            "ResTextFormat": 0,
            "SourceType": 1,
            "Data": base64_wav,
            "DataLen": data_len,
        }
        req._deserialize(params)
        req.EngineModelType = self.scenario
        resp = self.client.CreateRecTask(req)
        reply = json.loads(resp.to_json_string())
        return reply

    def query_task(self, task_id: int) -> dict:
        status = 0
        while status in [0, 1]:
            print('Fetching result...')
            result = self.query_task_once(task_id)
            status = result['Data']['Status']
            sleep(5)
        print('Fetched result:')
        return result

    def query_task_once(self, task_id: int) -> dict:
        req = models.DescribeTaskStatusRequest()
        req.from_json_string(json.dumps({'TaskId': task_id}))
        resp = self.client.DescribeTaskStatus(req)
        reply = json.loads(resp.to_json_string())
        return reply


def main():
    result = AudioRecognition().process_from_file('./samples/sample_en.mp3')
    print(result)


if __name__ == '__main__':
    main()
