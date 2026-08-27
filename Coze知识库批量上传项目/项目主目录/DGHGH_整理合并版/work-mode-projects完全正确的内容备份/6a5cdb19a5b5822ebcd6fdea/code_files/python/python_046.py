class BatchFileRepairTool:
    """批量文件修复工具"""
    
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.supported_extensions = ['.txt', '.json', '.yaml', '.yml', '.md', '.py', '.js', '.ts', '.java']
        self.processed_files = []
        self.failed_files = []
        
    def scan_folder(self):
        """扫描文件夹中的所有支持文件"""
        all_files = []
        for root, dirs, files in os.walk(self.folder_path):
            for file in files:
                if any(file.endswith(ext) for ext in self.supported_extensions):
                    file_path = os.path.join(root, file)
                    all_files.append(file_path)
        return all_files
    
    def detect_file_type(self, file_path):
        """检测文件类型"""
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ['.json']:
            return 'json'
        elif ext in ['.yaml', '.yml']:
            return 'yaml'
        elif ext in ['.py', '.js', '.ts', '.java']:
            return 'code'
        else:
            return 'text'
    
    def repair_all_files(self, mode='auto'):
        """修复所有文件"""
        files = self.scan_folder()
        print(f"找到 {len(files)} 个支持的文件")
        
        for file_path in files:
            print(f"\n处理文件: {file_path}")
            try:
                file_type = self.detect_file_type(file_path)
                
                if file_type in ['json', 'yaml']:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    lines = content.split('\n')
                    unique_lines = list(OrderedDict.fromkeys(lines))
                    cleaned_content = '\n'.join(unique_lines)
                    
                    output_path = os.path.splitext(file_path)[0] + "_cleaned" + os.path.splitext(file_path)[1]
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(cleaned_content)
                    
                    self.processed_files.append({
                        'original': file_path,
                        'cleaned': output_path,
                        'type': file_type
                    })
                    
                else:
                    tool = AdvancedTXTRepairTool(file_path)
                    if tool.repair_process(mode=mode):
                        self.processed_files.append({
                            'original': file_path,
                            'cleaned': tool.output_path,
                            'type': file_type
                        })
                    else:
                        self.failed_files.append(file_path)
                        
            except Exception as e:
                print(f"处理失败: {str(e)}")
                self.failed_files.append(file_path)
        
        self._generate_batch_report()
    
    def _generate_batch_report(self):
        """生成批量处理报告"""
        report_path = os.path.join(self.folder_path, "batch_repair_report.txt")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("批量文件修复处理报告\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"处理文件夹: {self.folder_path}\n")
            f.write(f"成功处理文件: {len(self.processed_files)} 个\n")
            f.write(f"失败文件: {len(self.failed_files)} 个\n\n")
            
            if self.processed_files:
                f.write("成功处理文件列表:\n")
                f.write("-" * 40 + "\n")
                for item in self.processed_files:
                    f.write(f"原始: {item['original']}\n")
                    f.write(f"清理后: {item['cleaned']}\n")
                    f.write(f"类型: {item['type']}\n")
                    f.write("-" * 40 + "\n")
            
            if self.failed_files:
                f.write("\n失败文件列表:\n")
                f.write("-" * 40 + "\n")
                for file in self.failed_files:
                    f.write(f"{file}\n")
        
        print(f"\n批量处理报告已保存至: {report_path}")


def main():
    print("\n" + "="*60)
    print("    TXT文件自动化修复整合工具 - 最终增强版")
    print("="*60)
    print("\n支持功能：")
    print("✅ 移除所有重复行和重复段落")
    print("✅ 智能识别并去除相似内容")
    print("✅ 代码文件专用去重（保留导入和注释）")
    print("✅ 版本块智能去重（保留最新版本）")
    print("✅ 缺失内容检测和提示")
    print("✅ 文档结构自动修复")
    print("✅ 批量文件夹处理")
    print("✅ 详细处理报告生成")
    
    print("\n请选择处理模式：")
    print("1. 一键式全自动去重（推荐）")
    print("2. 代码文件专用去重")
    print("3. 自定义相似度去重")
    print("4. 仅基础去重（行+段落）")
    print("5. 批量处理整个文件夹")
    
    mode_choice = input("\n请选择模式编号 (1-5, 默认1): ").strip() or '1'
    
    if mode_choice == '5':
        folder_path = input("\n请输入要处理的文件夹路径: ").strip()
        if not os.path.isdir(folder_path):
            print(f"❌ 错误：文件夹 '{folder_path}' 不存在")
            return
        
        batch_tool = BatchFileRepairTool(folder_path)
        batch_tool.repair_all_files()
        
    else:
        file_path = input("\n请输入要处理的文件路径: ").strip()
        
        if not os.path.exists(file_path):
            print(f"❌ 错误：文件 '{file_path}' 不存在")
            return
        
        mode_map = {
            '1': 'auto',
            '2': 'code', 
            '3': 'similar',
            '4': 'basic'
        }
        
        tool = AdvancedTXTRepairTool(file_path)
        
        try:
            if mode_choice == '3':
                threshold_input = input("请输入相似度阈值 (0.1-1.0, 默认0.85): ").strip()
                threshold = float(threshold_input) if threshold_input else 0.85
                success = tool.repair_process(mode='similar', threshold=threshold)
            else:
                success = tool.repair_process(mode=mode_map.get(mode_choice, 'auto'))
            
            if success:
                print(f"\n🎉 处理完成！清理后的文件已保存至: {tool.output_path}")
                print(f"📊 详细报告请查看: {tool.report_path}")
            else:
                print("\n❌ 处理失败，请检查文件格式或路径。")
                
        except Exception as e:
            print(f"\n❌ 处理过程中出现错误: {str(e)}")
            print("请检查文件格式或尝试其他处理模式。")

if __name__ == "__main__":
    main()