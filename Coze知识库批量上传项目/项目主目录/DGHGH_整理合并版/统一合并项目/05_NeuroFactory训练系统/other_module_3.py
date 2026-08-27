def batch_merge_directory(directory_path: str, recursive: bool = True, output_dir: str = "merged_output") -> Dict[str, Any]:
    merger = UniversalFileMerger()
    all_files = []
    if recursive:
        for root, _, files in os.walk(directory_path):
            for f in files:
                all_files.append(os.path.join(root, f))
    else:
        for f in os.listdir(directory_path):
            fp = os.path.join(directory_path, f)
            if os.path.isfile(fp):
                all_files.append(fp)
    if not all_files:
        return {"success": False, "error": "目录中没有找到文件"}
    return merger.merge_files_by_extension(all_files, output_dir)

def merge_coze_plugins_directory(directory_path: str, recursive: bool = True, output_dir: str = "coze_merged") -> Dict[str, Any]:
    merger = CozePluginMerger()
    all_files = []
    if recursive:
        for root, _, files in os.walk(directory_path):
            for f in files:
                all_files.append(os.path.join(root, f))
    else:
        for f in os.listdir(directory_path):
            fp = os.path.join(directory_path, f)
            if os.path.isfile(fp):
                all_files.append(fp)
    if not all_files:
        return {"success": False, "error": "目录中没有找到文件"}
    return merger.merge_coze_plugins(all_files, output_dir)

def interactive_merge():
    print("=== 文件合并融合系统 ===")
    print("1. 通用文件合并（按文件类型）\n2. Coze插件专用合并\n3. 合并整个目录\n4. 合并Coze插件目录")
    choice = input("请选择 (1/2/3/4): ").strip()
    if choice == "1":
        paths = [p.strip() for p in input("请输入文件路径（逗号分隔）: ").split(',')]
        result = UniversalFileMerger().merge_files_by_extension(paths)
    elif choice == "2":
        paths = [p.strip() for p in input("请输入Coze插件文件路径（逗号分隔）: ").split(',')]
        result = CozePluginMerger().merge_coze_plugins(paths)
    elif choice == "3":
        dir_path = input("请输入目录路径: ").strip()
        if not os.path.exists(dir_path):
            print("目录不存在")
            return
        rec = input("是否递归子目录？(y/n): ").lower() == 'y'
        result = batch_merge_directory(dir_path, rec)
    elif choice == "4":
        dir_path = input("请输入Coze插件目录路径: ").strip()
        if not os.path.exists(dir_path):
            print("目录不存在")
            return
        rec = input("是否递归子目录？(y/n): ").lower() == 'y'
        result = merge_coze_plugins_directory(dir_path, rec)
    else:
        print("无效选择")
        return
    if result.get("success"):
        print("\n✅ 合并成功!")
        print(f"统计: {result.get('statistics', {})}")
        for ext, info in result.get("merge_results", {}).items():
            print(f"  {ext}: {info.get('merged_file')}")
    else:
        print(f"❌ 合并失败: {result.get('error','未知错误')}")