def share_resources(self, src_project, dst_project):
       # 自动创建符号链接或复制资源
       if platform.system() == "Windows":
           os.system(f'mklink /J "{dst_dir}" "{src_dir}"')
       else:
           os.symlink(src_dir, dst_dir)