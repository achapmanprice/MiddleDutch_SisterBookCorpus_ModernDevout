import sublime
import sublime_plugin
import os
import re

class DivideChaptersCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        content = view.substr(sublime.Region(0, view.size()))
        file_path = view.file_name()

        if not file_path:
            sublime.error_message("Please save the file first.")
            return

        base_dir = os.path.dirname(file_path)

        # Match the chapter heading pattern
        chapter_pattern = re.compile(
            r"(¥%@(?P<num>\d{1,2})\. (?P<name>.+?), (?P<title>Pater|Mater|Procuratrix|Schwester) \((?P<death>†[^)]+)\))"
        )

        # Find all chapter start positions
        chapters = list(chapter_pattern.finditer(content))

        if not chapters:
            sublime.error_message("No chapters found.")
            return

        # Save Prolog
        prolog_text = content[:chapters[0].start()].strip()
        if "Prolog" in prolog_text:
            with open(os.path.join(base_dir, "EProlog.txt"), "w", encoding="utf-8") as f:
                f.write(prolog_text)

        # Save each chapter
        for i, match in enumerate(chapters):
            start = match.start()
            end = chapters[i + 1].start() if i + 1 < len(chapters) else len(content)
            chapter_text = content[start:end].strip()

            num = int(match.group("num"))
            name = match.group("name")
            title = match.group("title")
            death = match.group("death")

            num_str = f"{num:02}"
            filename = f"E{num_str}. {name}, {title} ({death}).txt"
            filepath = os.path.join(base_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(chapter_text)

        # Save Epilog
        last_chapter_end = chapters[-1].end()
        epilog_text = content[last_chapter_end:].strip()
        if "Epilog" in epilog_text:
            with open(os.path.join(base_dir, "EEpilog.txt"), "w", encoding="utf-8") as f:
                f.write(epilog_text)

        sublime.message_dialog("Chapters and sections saved.")
