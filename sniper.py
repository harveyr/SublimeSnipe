import subprocess
import sublime
import sublime_plugin
import tempfile
import os
import shlex


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
            handler = self.haskell_handler
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

        result = handler(command, tf.name)
        self.report(result)
        os.remove(tf.name)

    def standard_handler(self, command, filepath):
        p = subprocess.Popen(
            [command, filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self.report("[SublimeSnipe: Opening Process {}]".format(p.pid))
        out, err = p.communicate()
        return err.decode('utf-8') + out.decode('utf-8')

    def haskell_handler(self, command, filepath):
        head, tail = os.path.split(filepath)
        path_without_extension = os.path.join(head, tail.split('.')[0])
        compile_cmd = shlex.split("ghc -o {compiled} {source}".format(
            compiled=path_without_extension,
            source=filepath
        ))
        p = subprocess.Popen(
            compile_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        out, err = p.communicate()
        result = err.decode('utf-8') + out.decode('utf-8')

        run_command = [path_without_extension]
        print('run_command: {v}'.format(v=run_command))
        p = subprocess.Popen(
            run_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        out, err = p.communicate()
        result += err.decode('utf-8') + out.decode('utf-8')

        os.remove(path_without_extension)
        os.remove(filepath)

        return result

    def report(self, results):
        results = "[SublimeSnipe Results]\n" + results
        self.view.run_command('sniper_set_panel_text', {'text': results})
