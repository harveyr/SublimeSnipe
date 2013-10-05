import subprocess
import sublime
import sublime_plugin
import tempfile
import os


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
        elif "source.js" in scopes:
            cmd = "node"
            extension = ".js"
        elif "source.php" in scopes:
            # It doesn't look like Sublime will even let you impose the PHP
            # scope unless there's the opening <?php tag, so we shouldn't
            # have to worry about checking whether it's there.
            cmd = "php"
            extension = ".php"
        else:
            print("[SublimeSnipe] Scope not supported: {}".format(scopes))
            return False

        tf = tempfile.NamedTemporaryFile(
            mode='w',
            suffix=extension,
            prefix="sublime_sniper",
            delete=False)
        with open(tf.name, 'w') as f:
            f.write(code)

        p = subprocess.Popen(
            [cmd, tf.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.report("[SublimeSnipe: Opening Process {}]".format(p.pid))
        out, err = p.communicate()
        self.report(err.decode('utf-8') + out.decode('utf-8'))
        os.remove(tf.name)

    def report(self, results):
        results = "[SublimeSnipe Results]\n" + results
        self.view.run_command('sniper_set_panel_text', {'text': results})
