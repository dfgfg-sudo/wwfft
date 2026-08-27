class CozePluginMerger(UniversalFileMerger):
    """专门处理 Coze 插件和 OpenAPI 文件的合并器"""

    def __init__(self):
        super().__init__()
        self.coze_specific_stats = {
            "plugins_merged": 0,
            "tools_merged": 0,
            "endpoints_merged": 0,
            "schemas_merged": 0,
            "openapi_specs_merged": 0
        }

    def merge_coze_plugins(self, file_paths: List[str], output_dir: str = "coze_merged") -> Dict[str, Any]:
        try:
            plugin_files, openapi_files, other_files = [], [], []
            for fp in file_paths:
                ext = Path(fp).suffix.lower()
                content = self._read_file_with_detected_encoding(fp)
                if self._is_coze_plugin_file(content, ext):
                    plugin_files.append(fp)
                elif self._is_openapi_file(content, ext):
                    openapi_files.append(fp)
                else:
                    other_files.append(fp)
            results = {}
            if plugin_files:
                results["plugins"] = self._merge_coze_plugin_files(plugin_files, output_dir)
                self.coze_specific_stats["plugins_merged"] = len(plugin_files)
            if openapi_files:
                results["openapi"] = self._merge_openapi_files(openapi_files, output_dir)
                self.coze_specific_stats["openapi_specs_merged"] = len(openapi_files)
            if other_files:
                results["other_files"] = super().merge_files_by_extension(other_files, Path(output_dir)/"other_files")
            unified = self._generate_unified_coze_output(results, output_dir)
            return {"success": True, "results": results, "unified_output": unified, "statistics": {**dict(self.merge_stats), **self.coze_specific_stats}}
        except Exception as e:
            self.logger.error(f"合并Coze插件时出错: {e}")
            return {"success": False, "error": str(e), "statistics": {**dict(self.merge_stats), **self.coze_specific_stats}}

    def _is_coze_plugin_file(self, content: str, ext: str) -> bool:
        patterns = [r'"schema_version"\s*:\s*"v[0-9]', r'"tools"\s*:\s*\[', r'"endpoints"\s*:\s*\[']
        if any(re.search(p, content.lower()) for p in patterns):
            return True
        if ext in ['.yaml','.yml'] and any(re.search(p, content.lower()) for p in [r'schema_version:\s*v[0-9]', r'tools:', r'endpoints:']):
            return True
        return False

    def _is_openapi_file(self, content: str, ext: str) -> bool:
        patterns = [r'"openapi"\s*:\s*"3\.[0-9]+\.[0-9]+"', r'"swagger"\s*:\s*"2\.[0-9]"', r'"info"\s*:\s*{', r'"paths"\s*:\s*{']
        if any(re.search(p, content) for p in patterns):
            return True
        if ext in ['.yaml','.yml'] and any(re.search(p, content) for p in [r'openapi:\s*3\.[0-9]+\.[0-9]+', r'swagger:\s*2\.[0-9]', r'info:', r'paths:']):
            return True
        return False

    def _merge_coze_plugin_files(self, file_paths: List[str], output_dir: str) -> Dict:
        parsed = []
        for fp in file_paths:
            try:
                c = self._read_file_with_detected_encoding(fp)
                ext = Path(fp).suffix.lower()
                if ext == '.json':
                    data = json.loads(self._repair_json_syntax(c))
                elif ext in ['.yaml','.yml']:
                    data = yaml.safe_load(c)
                else:
                    continue
                parsed.append({"file_path": fp, "data": data})
            except Exception as e:
                self.logger.warning(f"解析Coze插件文件失败 {fp}: {e}")
        merged = self._merge_coze_plugin_data(parsed)
        out = Path(output_dir)/"merged_coze_plugin.yaml"
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out,'w',encoding='utf-8') as f:
            yaml.dump(merged, f, default_flow_style=False, allow_unicode=True)
        return {"merged_file": str(out), "plugin_count": len(parsed), "tools_count": len(merged.get("tools", [])), "endpoints_count": len(merged.get("endpoints", [])), "file_size_kb": os.path.getsize(out)//1024}

    def _merge_coze_plugin_data(self, plugins: List[Dict]) -> Dict:
        if not plugins:
            return self._create_default_coze_plugin()
        merged = copy.deepcopy(plugins[0]["data"])
        merged.setdefault("schema_version", "v1")
        merged.setdefault("name", "Merged_Coze_Plugin")
        merged.setdefault("description", "Auto-merged Coze plugin from multiple files")
        all_tools = []
        tool_names = set()
        for p in plugins:
            for tool in p["data"].get("tools", []):
                if isinstance(tool, dict) and tool.get("name"):
                    if tool["name"] not in tool_names:
                        tool_names.add(tool["name"])
                        all_tools.append(tool)
                    else:
                        existing = next((t for t in all_tools if t["name"]==tool["name"]), None)
                        if existing:
                            if tool.get("description"):
                                existing["description"] = existing.get("description", "") + "\nAlso: " + tool["description"]
                            if tool.get("parameters"):
                                existing.setdefault("parameters", [])
                                existing_params = {p.get("name") for p in existing["parameters"] if p.get("name")}
                                for param in tool["parameters"]:
                                    if param.get("name") not in existing_params:
                                        existing["parameters"].append(param)
        merged["tools"] = all_tools
        self.coze_specific_stats["tools_merged"] = len(all_tools)
        all_eps = []
        ep_paths = set()
        for p in plugins:
            for ep in p["data"].get("endpoints", []):
                if isinstance(ep, dict) and ep.get("path") and ep["path"] not in ep_paths:
                    ep_paths.add(ep["path"])
                    all_eps.append(ep)
        if all_eps:
            merged["endpoints"] = all_eps
            self.coze_specific_stats["endpoints_merged"] = len(all_eps)
        merged.setdefault("metadata", {})["merge_info"] = {
            "merged_at": datetime.now().isoformat(),
            "source_files": [p["file_path"] for p in plugins],
            "total_plugins": len(plugins),
            "total_tools": len(all_tools),
            "total_endpoints": len(all_eps)
        }
        return merged

    def _merge_openapi_files(self, file_paths: List[str], output_dir: str) -> Dict:
        parsed = []
        for fp in file_paths:
            try:
                c = self._read_file_with_detected_encoding(fp)
                ext = Path(fp).suffix.lower()
                if ext == '.json':
                    data = json.loads(self._repair_json_syntax(c))
                elif ext in ['.yaml','.yml']:
                    data = yaml.safe_load(c)
                else:
                    continue
                parsed.append({"file_path": fp, "data": data})
            except Exception as e:
                self.logger.warning(f"解析OpenAPI文件失败 {fp}: {e}")
        merged = self._merge_openapi_specs(parsed)
        out = Path(output_dir)/"merged_openapi.yaml"
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out,'w',encoding='utf-8') as f:
            yaml.dump(merged, f, default_flow_style=False, allow_unicode=True)
        return {"merged_file": str(out), "spec_count": len(parsed), "paths_count": len(merged.get("paths", {})), "components_count": len(merged.get("components", {})), "file_size_kb": os.path.getsize(out)//1024}

    def _merge_openapi_specs(self, specs: List[Dict]) -> Dict:
        if not specs:
            return {"openapi": "3.0.0", "info": {"title": "Merged API", "version": "1.0.0", "description": "Auto-merged OpenAPI specification"}, "paths": {}, "components": {}}
        merged = copy.deepcopy(specs[0]["data"])
        merged.setdefault("openapi", "3.0.0")
        merged.setdefault("info", {})
        merged["info"]["title"] = merged["info"].get("title", "Merged API")
        merged["info"]["description"] = "Auto-merged from multiple OpenAPI specifications\n\n" + merged["info"].get("description", "")
        merged.setdefault("paths", {})
        merged.setdefault("components", {})
        for spec in specs[1:]:
            for path, path_item in spec["data"].get("paths", {}).items():
                if path not in merged["paths"]:
                    merged["paths"][path] = path_item
                else:
                    for method, op in path_item.items():
                        if method not in merged["paths"][path]:
                            merged["paths"][path][method] = op
            for comp_type, comps in spec["data"].get("components", {}).items():
                if comp_type not in merged["components"]:
                    merged["components"][comp_type] = {}
                for name, sch in comps.items():
                    if name not in merged["components"][comp_type]:
                        merged["components"][comp_type][name] = sch
        merged["x-merge-metadata"] = {
            "merged_at": datetime.now().isoformat(),
            "source_files": [s["file_path"] for s in specs],
            "total_specs": len(specs),
            "total_paths": len(merged["paths"]),
            "total_components": sum(len(c) for c in merged["components"].values() if isinstance(c, dict))
        }
        return merged

    def _create_default_coze_plugin(self) -> Dict:
        return {"schema_version": "v1", "name": "Default_Merged_Coze_Plugin", "description": "Automatically created Coze plugin from merged files", "version": "1.0.0", "tools": [], "metadata": {"created_by": "CozePluginMerger", "created_at": datetime.now().isoformat(), "auto_generated": True}}

    def _generate_unified_coze_output(self, results: Dict, output_dir: str) -> Dict:
        unified_file = Path(output_dir) / "unified_coze_output.yaml"
        unified = {
            "unified_coze_output": {
                "generated_at": datetime.now().isoformat(),
                "summary": {k: self.coze_specific_stats.get(k, 0) for k in ["plugins_merged", "openapi_specs_merged", "tools_merged", "endpoints_merged"]},
                "output_files": {},
                "recommendation": "Use the merged_coze_plugin.yaml for Coze platform import"
            }
        }
        for res in results.values():
            if isinstance(res, dict) and "merged_file" in res:
                unified["unified_coze_output"]["output_files"][res.get("merged_file", "")] = {"path": res["merged_file"], "size_kb": res.get("file_size_kb", 0)}
        with open(unified_file,'w',encoding='utf-8') as f:
            yaml.dump(unified, f, default_flow_style=False, allow_unicode=True)
        return {"unified_file": str(unified_file), "unified_data": unified}