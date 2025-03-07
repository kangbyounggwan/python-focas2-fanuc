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


import ctypes
import os

# # 📌 DLL 파일이 위치한 경로 (현재 실행 파일과 같은 경로에 있을 경우)
# DLL_PATH = "./lib/Fwlib64.dll"
# EXTRA_DLLS = ["./lib/fwlibe64.dll", "./lib/fwlibNCG64.dll"]
#
# # 📌 FOCAS2 라이브러리 로드
# try:
#     focas2 = ctypes.WinDLL(DLL_PATH)
#     for dll in EXTRA_DLLS:
#         ctypes.WinDLL(dll)
#     print("✅ FANUC FOCAS2 라이브러리 로드 성공!")
# except Exception as e:
#     print(f"❌ DLL 로드 실패: {e}")
#     exit(1)
#
# # 📌 CNC 핸들 저장 변수
# handle = ctypes.c_ushort(0)
#
# # 📌 CNC GUIDE 연결을 위한 IP 및 포트 설정
# CNC_IP = b"127.0.0.1"  # CNC IP 주소 입력
# PORT = ctypes.c_uint16(8193)  # 기본 FANUC 포트
# TIMEOUT = ctypes.c_uint16(10)  # 타임아웃 설정 (초)
#
# # 📌 CNC GUIDE와 연결
# result = focas2.cnc_allclibhndl3(CNC_IP, PORT, TIMEOUT, ctypes.byref(handle))
#
# if result == 0:
#     print(f"✅ CNC GUIDE 연결 성공! 핸들: {handle.value}")
#
#     # 📌 CNC 시스템 정보 가져오기
#     cnc_info = ctypes.create_string_buffer(256)
#     focas2.cnc_sysinfo(handle, ctypes.byref(cnc_info))
#     print(f"CNC 시스템 정보: {cnc_info.value.decode('utf-8')}")
#
#     # 📌 CNC 핸들 해제 (연결 종료)
#     focas2.cnc_freelibhndl(handle)
#     print("🔌 CNC 연결 종료 완료")
# else:
#     print(f"❌ CNC GUIDE 연결 실패! 오류 코드: {result}")


import pymongo

# ✅ MongoDB 연결
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["test"]  # 데이터베이스 선택
collection = db["focas"]  # 컬렉션 선택

# ✅ 저장된 데이터 조회
documents = collection.find().limit(5)  # 최근 5개 데이터 조회

# ✅ 데이터 출력
for doc in documents:
    print(doc)
