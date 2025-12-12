import sublime
import sublime_plugin
import re
import os

class ExtractChaptersCustomCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        content = self.view.substr(sublime.Region(0, self.view.size()))

        # Match chapters using the pattern
        chapter_pattern = re.compile(
            r"(?:\n){3}(I{1,3}|IV|V|VI{0,3}|IX|X{1,3}|XI{0,2}|XII{0,1}|XIII)\.\n{2}(.*?,)",
            re.IGNORECASE
        )

        # Find all matches with start indices
        matches = list(chapter_pattern.finditer(content))
        total_chapters = len(matches)

        if total_chapters != 13:
            sublime.message_dialog(f"Expected 13 chapters, found {total_chapters}. Aborting.")
            return

        # Get path of original file
        file_path = self.view.file_name()
        if not file_path:
            sublime.message_dialog("Please save the file first.")
            return

        folder = os.path.dirname(file_path)

        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
            chapter_text = content[start:end].lstrip('\n')

            roman_numeral = match.group(1)
            title_line = match.group(2)

            # Create filename
            arabic_num = i + 1
            title_words = title_line[:-1].strip().split()  # Remove the trailing comma
            title_lower = [w.lower() for w in title_words]

            keywords = ["mater", "suster", "vrouwen"]
            title_extract = []

            if any(k in title_lower for k in keywords):
                for idx, word in enumerate(title_lower):
                    title_extract.append(title_words[idx])
                    if word in keywords:
                        # Add following words until the end
                        title_extract += title_words[idx+1:]
                        break
            else:
                title_extract = title_words

            short_title = "_".join(title_extract)
            filename = f"D{arabic_num}_{short_title}.txt"
            save_path = os.path.join(folder, filename)

            # Save chapter to file
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(chapter_text)

        sublime.message_dialog("Chapters successfully extracted and saved.")