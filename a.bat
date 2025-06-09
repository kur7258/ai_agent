@REM Author : carrier1269@github.com

@REM 콘솔 로그 비활성화
@echo off

@REM 현재 디렉토리 변수 저장
set INITIAL_PATH=%cd%

@REM 경로 폴더 이동
cd .venv/Scripts

@REM 파이썬 가상환경 실행
call Activate

@REM 초기 파일 경로로 이동
cd %INITIAL_PATH%