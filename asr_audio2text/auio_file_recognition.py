import sys
import json
import base64
from time import sleep

from tencentcloud.asr.v20190614 import models

from common.auth import get_asr_auth_client

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


class AudioRecognition:

    def __init__(self, **kwargs):
        self.client = get_asr_auth_client()

    def process_from_file(self, filepath: str, **specified) -> dict:
        task = self.create_task_from_file(filepath, specified)
        result = self.query_task(task['Data']['TaskId'])
        return result

    def process_from_url(self, url: str, **specified) -> dict:
        task = self.create_task_from_url(url, specified)
        result = self.query_task(task['Data']['TaskId'])
        return result

    def create_task_from_file(self, filepath: str, specified: dict) -> dict:
        # Doc: https://cloud.tencent.com/document/product/1093/35799
        with open(filepath, 'rb') as f:
            data = f.read()
            data_len = len(data)
            base64_wav = base64.b64encode(data).decode()

        req = models.CreateRecTaskRequest()
        params = {
            "EngineModelType": '16k_zh',
            "ChannelNum": 1,
            "ResTextFormat": 0,
            "SourceType": 1,
            "Data": base64_wav,
            "DataLen": data_len,
            # Per audio settings
            "SpeakerDiarization": 1,
            "SpeakerNumber": 2,
            "FilterPunc": 1,
            "FilterModal": 2,
            "ConvertNumMode": 1,
        }
        params.update(specified)
        print(f'Task request: {params}')
        req._deserialize(params)
        resp = self.client.CreateRecTask(req)
        reply = json.loads(resp.to_json_string())
        print(f'Created a task {reply} for {filepath}')
        return reply

    def create_task_from_url(self, url: str, specified: dict) -> dict:
        # Doc: https://cloud.tencent.com/document/product/1093/35799
        req = models.CreateRecTaskRequest()
        params = {
            "EngineModelType": '16k_zh',
            "ChannelNum": 1,
            "ResTextFormat": 0,
            "SourceType": 0,
            "Url": url,
            # Per audio settings
            "SpeakerDiarization": 1,
            "SpeakerNumber": 2,
            "FilterPunc": 1,
            "FilterModal": 2,
            "ConvertNumMode": 1,
        }
        params.update(specified)
        print(f'Task request: {params}')
        req._deserialize(params)
        resp = self.client.CreateRecTask(req)
        reply = json.loads(resp.to_json_string())
        print(f'Created a task {reply} for {url}')
        return reply

    def query_task(self, task_id: int) -> dict:
        status = 0
        while status in [0, 1]:
            print('Fetching result...')
            try:
                result = self.query_task_once(task_id)
            except Exception as ex:
                print(ex)
                continue
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
    if len(sys.argv) < 3:
        raise RuntimeError('Please specify 1) method: local|url|query  2) source: local_path|url|task_id')

    method, source = sys.argv[1:3]
    if method == 'local':
        # path = './samples/genesis.001.mp3'
        result = AudioRecognition().process_from_file(source)
    elif method == 'url':
        # url = 'https://public-1300134733.cos.ap-beijing.myqcloud.com/%E5%88%9B%E4%B8%96%E8%AE%B0039-1.mp3'
        result = AudioRecognition().process_from_url(source, EngineModelType='16k_en', SpeakerDiarization=0)
    elif method == 'query':
        result = AudioRecognition().query_task(867064529)

    # Save result
    print(result)
    with open('/tmp/transcript.json', 'w') as f:
        f.write(json.dumps(result))
    with open('/tmp/transcript.txt', 'w') as f:
        f.write(result['Data']['Result'])


if __name__ == '__main__':
    main()
