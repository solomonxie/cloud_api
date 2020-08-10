import json
import base64
from time import sleep

from tencentcloud.asr.v20190614 import models

from common.auth import get_asr_auth_client


class AudioRecognition:

    def __init__(self):
        self.client = get_asr_auth_client()

    def process_from_file(self, filepath):
        task = self.create_task_from_file(filepath)
        status = 0
        result = self.query_task(task['Data']['TaskId'])
        return result

    def create_task_from_file(self, filepath: str) -> dict:
        """
        Reply: {"Data": {"TaskId": 856184969}, "RequestId": "c7e76487-64bc-45b0-95da-756f7eb928d1"}
        """
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
        resp = self.client.CreateRecTask(req)
        reply = json.loads(resp.to_json_string())
        return reply

    def query_task(self, task_id: int) -> dict:
        status = 0
        while status in [0, 1]:
            print('Fetching result...')
            result = self.query_task_once(task_id)
            print('\t', result)
            status = result['Data']['Status']
            sleep(5)
        print('Fetched result:')
        return result

    def query_task_once(self, task_id: int) -> dict:
        """
        Reply:
        {
            "Data": {
                "Status": 2,
                "StatusStr": "success",
                "Result": "[0:0.000,0:1.540]  \u6885\u8d5b\u5fb7\u65af\u5954\u9a70\u3002\n",
                "TaskId": 737083613,
                "ErrorMsg": "",
                "ResultDetail": null
            },
            "RequestId": "4f87d14f-8b0f-4970-b517-eaf8c5df2e9d"
        }
        """
        req = models.DescribeTaskStatusRequest()
        req.from_json_string(json.dumps({'TaskId': task_id}))
        resp = self.client.DescribeTaskStatus(req)
        reply = json.loads(resp.to_json_string())
        return reply
