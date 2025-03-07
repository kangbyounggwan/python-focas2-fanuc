# from pymongo import MongoClient
#
# # 방법1 - URI
# # mongodb_URI = "mongodb://localhost:27017/"
# # client = MongoClient(mongodb_URI)
#
# # 방법2 - HOST, PORT
# client = MongoClient(host='localhost', port=27017)
# db = client['test']
# print(db)
# # print(client.list_database_names())
import time

import ctypes
import os

# 📌 DLL 파일이 위치한 경로 (현재 실행 파일과 같은 경로에 있을 경우)
DLL_PATH = "./lib/Fwlib64.dll"
EXTRA_DLLS = ["./lib/fwlibe64.dll", "./lib/fwlibNCG64.dll"]

# 📌 FOCAS2 라이브러리 로드
try:
    focas2 = ctypes.WinDLL(DLL_PATH)
    for dll in EXTRA_DLLS:
        ctypes.WinDLL(dll)
    print("✅ FANUC FOCAS2 라이브러리 로드 성공!")
except Exception as e:
    print(f"❌ DLL 로드 실패: {e}")
    exit(1)

# 📌 CNC 핸들 저장 변수
handle = ctypes.c_ushort(0)
#
# 📌 CNC GUIDE 연결을 위한 IP 및 포트 설정
CNC_IP = b"127.0.0.1"  # CNC IP 주소 입력
PORT = ctypes.c_uint16(8193)  # 기본 FANUC 포트
TIMEOUT = ctypes.c_uint16(10)  # 타임아웃 설정 (초)

# 📌 CNC GUIDE와 연결
result = focas2.cnc_allclibhndl3(CNC_IP, PORT, TIMEOUT, ctypes.byref(handle))

if result == 0:
    print(f"✅ CNC GUIDE 연결 성공! 핸들: {handle.value}")

    # 📌 CNC 시스템 정보 가져오기
    cnc_info = ctypes.create_string_buffer(256)
    focas2.cnc_sysinfo(handle, ctypes.byref(cnc_info))
    print(f"CNC 시스템 정보: {cnc_info.value.decode('utf-8')}")

    # 📌 CNC 핸들 해제 (연결 종료)
    focas2.cnc_freelibhndl(handle)
    print("🔌 CNC 연결 종료 완료")
else:
    print(f"❌ CNC GUIDE 연결 실패! 오류 코드: {result}")


def read_cnc_param(param_no):
    """
    CNC 파라미터 값 읽기
    """
    param = (ctypes.c_short * 8)()  # 파라미터 데이터 저장 변수
    length = ctypes.c_short(8)  # 데이터 길이 설정
    result = focas2.cnc_rdparam(handle, param_no, 0, ctypes.byref(length), ctypes.byref(param))

    if result == 0:
        return param[0]  # 첫 번째 값 반환 (단일 값일 경우)
    else:
        print(f"❌ 파라미터 {param_no} 읽기 실패! 오류 코드: {result}")
        return None

def write_cnc_param(param_no, value):
    """
    CNC 파라미터 값 변경
    """
    param = (ctypes.c_short * 8)()  # 파라미터 데이터 저장 변수
    param[0] = value
    length = ctypes.c_short(8)  # 데이터 길이 설정

    result = focas2.cnc_wrparam(handle, param_no, 0, ctypes.byref(length), ctypes.byref(param))

    if result == 0:
        print(f"✅ 파라미터 {param_no} 값이 {value}로 변경됨.")
    else:
        print(f"❌ 파라미터 {param_no} 변경 실패! 오류 코드: {result}")

def trigger_alarm():
    """
    CNC 알람 강제 발생
    """
    alarm_data = (ctypes.c_short * 4)()
    alarm_data[0] = 1  # 알람 유형 설정 (1: 경고, 2: 에러)
    result = focas2.pmc_wrpmcrng(handle, 0, 0, 100, 100, 4, ctypes.byref(alarm_data))

    if result == 0:
        print("🚨 CNC 알람 발생! 🚨")
    else:
        print(f"❌ 알람 발생 실패! 오류 코드: {result}")

# 초기 파라미터 값 저장
PARAM_NO = 1825  # 예제 파라미터 번호 (실제 CNC 설정에 맞게 변경)
previous_value = read_cnc_param(PARAM_NO)

if previous_value is not None:
    print(f"✅ 초기 파라미터 값: {previous_value}")

# 일정 시간 간격으로 CNC 파라미터 감지


while True:
    time.sleep(5)  # 5초마다 체크

    current_value = read_cnc_param(PARAM_NO)

    if current_value is not None and current_value != previous_value:
        print(f"⚠️ 파라미터 {PARAM_NO} 값 변경 감지! {previous_value} → {current_value}")
        trigger_alarm()  # CNC 알람 발생
        previous_value = current_value  # 최신 값 업데이트

