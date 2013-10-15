import subprocess
import sublime
import sublime_plugin
import tempfile
import os
import shlex


PANEL_NAME = "snipe_panel"


def uncertain_file(func):
    """Decorates access to file that may not exist."""
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except FileNotFoundError as e:
            self.report('{}'.format(e))
    return wrapper


class SniperAddPanelText(sublime_plugin.TextCommand):
    panel = None

    def run(self, edit, text):
        window = sublime.active_window()
        self.panel = window.create_output_panel(PANEL_NAME)
        self.panel.insert(edit, self.panel.size(), text)
        panel_arg = "output.{}".format(PANEL_NAME)
        window.run_command('show_panel', {'panel': panel_arg})


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
        command = None
        extension = None

        handler = self.standard_handler
        if "source.python" in scopes:
            command = "python"
            extension = ".py"
        elif "source.js" in scopes:
            command = "node"
            extension = ".js"
        elif "source.php" in scopes:
            # It doesn't look like Sublime will even let you impose the PHP
            # scope unless there's the opening <?php tag, so we shouldn't
            # have to worry about checking whether it's there.
            command = "php {file}"
            extension = ".php"
        elif "source.haskell" in scopes:
            extension = ".hs"
            command = "runhaskell"
        else:
            self.report("[SublimeSnipe] Scope not supported: {}".format(scopes))
            return False

        tf = tempfile.NamedTemporaryFile(
            mode='w',
            suffix=extension,
            prefix="sublime_sniper",
            delete=False
        )
        with open(tf.name, 'w') as f:
            f.write(code)

        handler(command, tf.name)

    @uncertain_file
    def standard_handler(self, command, filepath):
        p = subprocess.Popen(
            [command, filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self.report("[SublimeSnipe: Opening Process {}]".format(p.pid))
        out, err = p.communicate()
        os.remove(filepath)
        self.report(err.decode('utf-8') + out.decode('utf-8'))

    def report(self, results):
        results = "[SublimeSnipe Results]\n" + results
        self.view.run_command('sniper_add_panel_text', {'text': results})
