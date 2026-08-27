def auto_organize_resources():
    workflows = scan_all_workflows()
    abandoned = [w for w in workflows if w.last_updated < days_ago(30)]
    for w in abandoned:
        add_tag(w, "归档-待清理")
        move_to_archive(w)
    duplicates = find_similar_workflows(workflows)
    return generate_report(duplicates)