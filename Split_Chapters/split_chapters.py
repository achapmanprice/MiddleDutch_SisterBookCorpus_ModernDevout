import sublime
import sublime_plugin
import os
import re

class SplitChaptersCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        text = self.view.substr(sublime.Region(0, self.view.size()))
        pattern = r'\((\d+)\)\s+(.*)'
        matches = list(re.finditer(pattern, text))

        if not matches:
            sublime.message_dialog("No chapters found.")
            return

        file_path = self.view.file_name()
        if not file_path:
            sublime.message_dialog("Please save the file first.")
            return

        folder = os.path.dirname(file_path)

        for i in range(len(matches)):
            chapter_start = matches[i].start()
            chapter_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

            chapter_text = text[chapter_start:chapter_end].strip()

            chapter_number = matches[i].group(1)
            chapter_title = matches[i].group(2).strip()
            safe_title = re.sub(r'[\\/*?:"<>|]', '', chapter_title)

            filename = f"G{chapter_number} {safe_title}.txt"
            filepath = os.path.join(folder, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(chapter_text)

        sublime.message_dialog("Chapters split successfully.")
