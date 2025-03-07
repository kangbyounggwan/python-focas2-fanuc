import sys
import os

# 현재 파일이 있는 폴더를 기준으로 FanucImplementation 폴더 경로를 추가
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# 정상적으로 import 되는지 확인
try:
    from Fwlib32_h import *
    print("✅ Fwlib32_h 모듈이 정상적으로 로드되었습니다!")
except ModuleNotFoundError as e:
    print(f"❌ 모듈을 찾을 수 없습니다: {e}")
