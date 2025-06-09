#!/bin/zsh

echo "Starting virtual environment activation..."

# 현재 디렉토리 변수 저장
INITIAL_PATH=$(pwd)
echo "Current directory: $INITIAL_PATH"

# 경로 폴더 이동
cd .venv/bin
echo "Changed to virtual environment bin directory"

# 파이썬 가상환경 실행
source activate
echo "Virtual environment activated"

# 초기 파일 경로로 이동
cd "$INITIAL_PATH"
echo "Returned to initial directory"

# 가상환경이 활성화되었는지 확인
if [[ -n "$VIRTUAL_ENV" ]]; then
    echo "Virtual environment is active: $VIRTUAL_ENV"
    echo "Python path: $(which python)"
else
    echo "Warning: Virtual environment might not be active"
fi 