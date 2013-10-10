import subprocess
import sublime
import sublime_plugin
import tempfile
import os
import shutil
import shlex
import re


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
        elif "source.go" in scopes:
            extension = ".go"
            handler = self.go_handler
        else:
            print("[SublimeSnipe] Scope not supported: {}".format(scopes))
            return False

        tf = tempfile.NamedTemporaryFile(
            mode='w',
            suffix=extension,
            prefix="sublime_sniper",
            delete=False
        )
        print('tf.name: {v}'.format(v=tf.name))
        with open(tf.name, 'w') as f:
            f.write(code)

        result = handler(command, tf.name)
        self.report(result)

    def standard_handler(self, command, filepath):
        p = subprocess.Popen(
            [command, filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self.report("[SublimeSnipe: Opening Process {}]".format(p.pid))
        out, err = p.communicate()
        os.remove(filepath)
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

    def go_handler(self, command, filepath):
        gopath = os.environ.get("GOPATH", None)
        if not gopath:
            # Hacky ...
            for rc_file in ['.bashrc', '.zshrc']:
                rc_file = "~/" + rc_file
                rex = re.compile("GOPATH=(\S+)")
                path = os.path.expanduser(rc_file)
                with open(path, 'r') as open_f:
                    contents = open_f.read()
                    matches = rex.search(contents)
                    if matches:
                        gopath = matches.group(1)
                        if "$HOME" in gopath:
                            gopath = os.path.expanduser(
                                gopath.replace("$HOME", "~/")
                            )
                            break
        if not gopath:
            return "Unable to find GOPATH"

        gopath = os.path.realpath(gopath)

        if not 'src' in os.listdir(gopath):
            return "Unable to find src/ directory in GOPATH"

        snipe_dir = os.path.join(gopath, 'src', 'sublimesnipe')
        if os.path.exists(snipe_dir):
            return "Target directory exists! Aborting. ({})".format(snipe_dir)

        os.makedirs(snipe_dir)
        target_file = os.path.join(snipe_dir, "sublimesnipe.go")
        shutil.copy(filepath, target_file)

        os.environ['GOPATH'] = gopath
        p = subprocess.Popen(
            ['/usr/local/go/bin/go', 'run', target_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=snipe_dir
        )
        out, err = p.communicate()
        os.remove(target_file)
        os.remove(filepath)
        os.removedirs(snipe_dir)
        return err.decode('utf-8') + out.decode('utf-8')

    def report(self, results):
        results = "[SublimeSnipe Results]\n" + results
        self.view.run_command('sniper_set_panel_text', {'text': results})
