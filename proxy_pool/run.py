from os import path, system

config_path = path.join(path.dirname(__file__), "xray_config_generator", "config.json")

xray_exe_path = path.join(path.dirname(__file__), "Xray-windows-64", "xray.exe")

if path.exists(xray_exe_path) and path.exists(config_path):
    # print("Xray and config file found.")
    pass
else:
    raise FileNotFoundError("Xray or config file not found.")

if __name__ == "__main__":

    # start cmd /k "cd /d D:\EdgeDownload\Xray-windows-64 && xray run -c xray_config_generator/config.json"

    command = f'start cmd /k "{xray_exe_path} run -c {config_path}"'

    system(command)
