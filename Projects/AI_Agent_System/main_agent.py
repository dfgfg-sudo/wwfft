import os
import json
import subprocess
import time

class AgentManager:
    def __init__(self):
        self.config_path = "d:\\Projects\\AI_Agent_System\\config.json"
        self.service_path = "d:\\Projects\\AI_Agent_System\\integrated_service.py"
        self.start_script = "d:\\Projects\\AI_Agent_System\\start_service.bat"
    
    def check_service_status(self):
        """检查服务状态"""
        try:
            import requests
            response = requests.get("http://localhost:5000/", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def start_service(self):
        """启动服务"""
        if not self.check_service_status():
            print("启动集成服务...")
            subprocess.Popen(["cmd.exe", "/c", self.start_script], creationflags=subprocess.CREATE_NEW_CONSOLE)
            # 等待服务启动
            time.sleep(3)
            if self.check_service_status():
                print("服务启动成功！")
            else:
                print("服务启动失败，请检查日志。")
        else:
            print("服务已经在运行中。")
    
    def stop_service(self):
        """停止服务"""
        print("停止集成服务...")
        # 使用taskkill终止Python进程
        subprocess.run(["taskkill", "/F", "/IM", "python.exe", "/T"], capture_output=True)
        print("服务已停止。")
    
    def check_config(self):
        """检查配置文件"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print("配置文件检查:")
            print(f"DeepSeek API: {'已配置' if config['deepseek']['api_key'] != '' else '未配置'}")
            print(f"Coze API: {'已配置' if config['coze']['api_key'] != 'YOUR_COZE_API_KEY' else '未配置'}")
            print(f"服务地址: http://{config['server']['host']}:{config['server']['port']}")
            print(f"飞书webhook: http://{config['server']['host']}:{config['server']['port']}{config['feishu']['webhook']}")
            print(f"安全配置: {'已启用' if config['security']['enabled'] else '已禁用'}")
        else:
            print("配置文件不存在，将使用默认配置。")
    
    def setup_autostart(self):
        """设置自动启动"""
        print("设置自动启动...")
        # 创建快捷方式到启动文件夹
        startup_folder = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        shortcut_path = os.path.join(startup_folder, 'OpenClaw集成服务.lnk')
        
        # 使用PowerShell创建快捷方式
        ps_script = f'$WScriptShell = New-Object -ComObject WScript.Shell; $Shortcut = $WScriptShell.CreateShortcut("{shortcut_path}"); $Shortcut.TargetPath = "{self.start_script}"; $Shortcut.WorkingDirectory = "d:\\Projects\\AI_Agent_System"; $Shortcut.Save()'
        subprocess.run(["powershell.exe", "-Command", ps_script], capture_output=True)
        print(f"自动启动已设置: {shortcut_path}")
    
    def run(self):
        """运行管理流程"""
        print("OpenClaw集成服务管理器")
        print("=" * 60)
        print("1. 启动服务")
        print("2. 停止服务")
        print("3. 检查服务状态")
        print("4. 检查配置")
        print("5. 设置自动启动")
        print("6. 退出")
        print("=" * 60)
        
        while True:
            choice = input("请选择操作 (1-6): ")
            
            if choice == '1':
                self.start_service()
            elif choice == '2':
                self.stop_service()
            elif choice == '3':
                status = "运行中" if self.check_service_status() else "未运行"
                print(f"服务状态: {status}")
            elif choice == '4':
                self.check_config()
            elif choice == '5':
                self.setup_autostart()
            elif choice == '6':
                print("退出管理器。")
                break
            else:
                print("无效选择，请重新输入。")
            print()

if __name__ == "__main__":
    manager = AgentManager()
    manager.run()