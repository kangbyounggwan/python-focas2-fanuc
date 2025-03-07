#!/usr/bin/env python

import logging
import time

import pymongo


from pyfocas.Collector import Collector
from pyfocas.Machine import Machine
from FanucImplementation.DriverImplementations import Fanuc30iDriver
from pyfocas import Exceptions
import sys
import os
# 현재 실행 파일(aggregator.py)이 있는 디렉토리 기준으로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# FanucImplementation 폴더를 Python 모듈 검색 경로에 추가
sys.path.append(os.path.join(BASE_DIR, "FanucImplementation"))
# 현재 실행 중인 스크립트의 경로를 기준으로 'FanucImplementation' 폴더 경로 추가



KBG_FOCAS2 = "127.0.0.1"

LIB_PATH = os.path.abspath("./lib/Fwlib64.dll")
EXTRA_DLL_PATH1 = os.path.abspath("./lib/fwlibe64.dll")
EXTRA_DLL_PATH2 = os.path.abspath("./lib/fwlibNCG64.dll")
print(LIB_PATH)
print(EXTRA_DLL_PATH1)
print(EXTRA_DLL_PATH2)

def logging_reporter(machine):
    """
    The logging_reporter is a reporter function to be passed
    into a Collector object.
    logging_reporter is intended for debugging purposes,
    all machine datums will be logged to the default logger.

    Parameters: Machine machine

                The reporter expects to be passed a
                Machine object that it will report on.

    Return value: dict data
                The reporter will return a dictionary
                with key:value pairs representing the
                data handled by the reporter.
    """
    try:
        data = machine.createDatum()
        logging.info(data)
        return data
    except Exceptions.FocasConnectionException:
        machine.reconnect()


def clean_data(data):
    """
    Recursively cleans the dictionary:
    1. Converts keys and values from bytes to strings.
    2. Removes dictionary keys that contain NULL bytes ('\x00').
    """
    if isinstance(data, dict):
        cleaned_dict = {}
        for k, v in data.items():
            # ✅ 키 변환 (bytes → str)
            new_key = k.decode('utf-8', errors='ignore') if isinstance(k, bytes) else k

            # ✅ 값 변환 (bytes → str)
            new_value = clean_data(v)

            # ✅ NULL 바이트 포함 키 제거
            if isinstance(new_key, str) and '\x00' not in new_key:
                cleaned_dict[new_key] = new_value

        return cleaned_dict

    elif isinstance(data, list):
        return [clean_data(i) for i in data]

    elif isinstance(data, bytes):
        decoded_value = data.decode('utf-8', errors='ignore')  # ✅ bytes 값을 안전하게 문자열로 변환
        return decoded_value  # ✅ MongoDB 저장 가능하도록 변환

    else:
        return data



def mongo_reporter(collection, machine):

    """
    Collects CNC data from `machine` and inserts it into the MongoDB `collection`.
    """
    try:
        data = machine.createDatum()
        data = clean_data(data)

        collection.insert_one(data)
        # ✅ 로그 기록
        logging.info(f"✅ 데이터 저장 완료: {data}")
        return data
    except Exception as e:
        logging.error(f"❌ 데이터 저장 실패: {e}")
        machine.reconnect()
        return None


def main():
    """
    The main method of the program. Runs a Collector forever.
    """

    """ Setup logging """
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Starting Collector")

    """ Setup MongoDB logging client """
    client = pymongo.MongoClient(host='localhost', port=27017, document_class=dict, tz_aware=False, connect=True)
    db = client['test']
    collection = db['focas']

    def reporter(machine):
        return mongo_reporter(collection, machine)

    """ Instantiate Fanuc30iDriver """
    driver30i = Fanuc30iDriver(LIB_PATH,
                               extradlls=[EXTRA_DLL_PATH1, EXTRA_DLL_PATH2])

    """ List of Machine objects to initialize the Collector with """
    machines = [Machine(driver=driver30i, ip=KBG_FOCAS2, name="316"),]
    """ Create the Collector """

    collector = Collector(reporter=reporter, machines=machines)

    while True:
        """ Run the collector until the process is interrupted """
        collector.collect()
        time.sleep(.05)

if __name__ == "__main__":
    main()
