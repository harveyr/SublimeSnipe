import subprocess
import sublime
import sublime_plugin
import tempfile


class SniperSetPanelText(sublime_plugin.TextCommand):
    def run(self, edit, text):
        window = sublime.active_window()
        panel = window.create_output_panel('snipe')
        panel.insert(edit, 0, text)
        window.run_command('show_panel', {'panel': 'output.snipe'})


class SniperCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        selection = self.view.sel()[0]
        if selection.size() == 0:
            code = self.view.substr(sublime.Region(0, self.view.size()))
        else:
            code = self.view.substr(selection)
        scopes = self.view.scope_name(selection.begin())
        self.execute(code, scopes)

    def execute(self, code, scopes):
        cmd = None
        extension = None
        if "source.python" in scopes:
            cmd = "python"
            extension = ".py"

        handle, path = tempfile.mkstemp(
            prefix="sublime_sniper", suffix=extension, text=True)
        with open(path, 'w') as f:
            f.write(code)

        p = subprocess.Popen(
            [cmd, path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.report("[SublimeSnipe: Opening Process {}".format(p.pid))
        out, err = p.communicate()
        self.report(err.decode('utf-8') + out.decode('utf-8'))

    def report(self, results):
        results = "[SublimeSnipe Results]\n" + results
        self.view.run_command('sniper_set_panel_text', {'text': results})
