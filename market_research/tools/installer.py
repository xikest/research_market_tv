import subprocess
import os
import platform
class Installer:
    @staticmethod
    def install_chrome_and_driver():
        current_os = platform.system()
        chrome_dict = None
        if current_os == "Linux":
            chrome_dict = Installer._install_chrome_and_driver_linux()
        elif current_os == "Windows":
            print("windows")
            chrome_dict = Installer._install_chrome_and_driver_win()
        else:
            print("지원하지 않는 운영체제입니다.")
        return chrome_dict


    @staticmethod
    def _install_chrome_and_driver_linux() -> dict:
        # 쉘 스크립트 내용
        shell_script_content = """
        #!/bin/bash
    
        # Download and setup Chrome
        wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/119.0.6045.105/linux64/chrome-linux64.zip
        unzip chrome-linux64.zip
        rm chrome-linux64.zip
        mv chrome-linux64 chrome
        rm chrome-linux64
    
        # Download and setup ChromeDriver
        wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/119.0.6045.105/linux64/chromedriver-linux64.zip
        unzip chromedriver-linux64.zip
        rm chromedriver-linux64.zip
        mv chromedriver-linux64 chromedriver
        rm chromedriver-linux64
    
        # Return Chrome installation path and ChromeDriver path
        echo $(pwd)/chrome
        echo $(pwd)/chromedriver
        """

        script_file_path = "set_chrome.sh"
        with open(script_file_path, "w") as script_file:
            script_file.write(shell_script_content)

        # 쉘 스크립트 실행
        result = subprocess.run(["bash", script_file_path], capture_output=True, text=True)

        # 쉘 스크립트 파일 삭제 (선택 사항)
        os.remove(script_file_path)

        current_dir = os.path.abspath(os.getcwd())
        return {"chrome_path": os.path.join(current_dir, "chrome"),
                "driver_path": os.path.join(current_dir, "chromedriver")}


    @staticmethod
    def _install_chrome_and_driver_win() -> dict:
        # Windows에서 사용되는 배치 파일 내용
        batch_script_content = """
            @echo off
    
            :: Download and setup Chrome
            powershell -Command "& {Invoke-WebRequest -Uri 'https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/119.0.6045.105/win64/ChromeSetup.exe' -OutFile 'chrome_installer.exe'}"
            Start-Process -Wait -FilePath 'chrome_installer.exe' -ArgumentList '/silent /install'
            del 'chrome_installer.exe'
    
            :: Download and setup ChromeDriver
            powershell -Command "& {Invoke-WebRequest -Uri 'https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/119.0.6045.105/win64/chromedriver_win64.zip' -OutFile 'chromedriver.zip'}"
            Expand-Archive -Path 'chromedriver.zip' -DestinationPath 'chromedriver'
            del 'chromedriver.zip'
    
            :: Return Chrome installation path and ChromeDriver path
            echo %cd%\chrome
            echo %cd%\chromedriver
            """

        # 배치 파일에 내용 쓰기
        script_file_path = "set_chrome.bat"
        with open(script_file_path, "w") as script_file:
            script_file.write(batch_script_content)

        # 배치 파일 실행
        result = subprocess.run([script_file_path], shell=True, capture_output=True, text=True)

        # 배치 파일 삭제 (선택 사항)
        os.remove(script_file_path)

        # 반환된 결과에서 경로 추출
        current_dir = os.path.abspath(os.getcwd())
        return {"chrome_path": os.path.join(current_dir, "chrome"),
                "driver_path": os.path.join(current_dir, "chromedriver")}
