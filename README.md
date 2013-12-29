## Ruff

*Ruff* basically, exists to do two things:

- Watch for changes in targets.
- If there are changes in target, run build operations.

It also has some convenience 'support' operations that allows it to:

- Run a local webserver if flask is installed
- Run arbitrary commands in sub-processes

### Quickstart:

Dev server module helper in, for example, src/mc/server.py, which you run
as python -m mc.server might do this:

    import ruff as r

    # Paths
    py = r.path(__file__, '..', '..', 'bin', 'py')
    public_html = r.path(__file__, '..', '..', 'client', 'public')
    ts_path = r.path(__file__, '..', '..', 'client', 'public', 'ts')

    # TS build
    def ts_build_config():
      build = r.build()
      build.chdir(ts_path)
      files = build.collect('.*\.ts$')
      cmd = ['tsc', '--out', 'output.ts.js']
      cmd.extend(build.collect('.*\.ts$', recurse=True))
      build.run(*cmd)
      return build

    # Start client server
    def main():
        ts_build = ts_build_config()
        ts_targets = r.target(timeout=15)
        ts_targets.pattern('.*\.ts$', ts_path, recurse=True)
        r.bind(dart_targets, dart_build)

        # Run local servers
        r.command(py, '-m', 'mc.core.main')
        r.serve('0.0.0.0', 3001, public_html)
        r.run()

    if __name__ == '__main__':
        main()

### Watches:

A watch is a set of folder patterns to observe.
If any change we can:

- immediately trigger a build
- trigger a build after at least X from last operation

Use:

    x = ruff.target()
    x.pattern('*.c', 'folder', recurse=True)
    x.pattern('*.h', 'folder', recurse=True)
    x.pattern('blah.cxx', 'folder')

### Builds:

A build operation is something that runs~

Use:

    def final(context):
      print(context)

    x = ruff.build()
    x.chdir('root')
    x.run('rm', 'blah/*.o')
    x.run('cp', 'src.txt', 'blah/target.txt')
    x.command(final)

Build commands are chainable, so if you have a relatively simply command,
you can save space by simply using:

    def setup_blah():
      return ruff.build().chdir(path).run('rm', 'blah.so').run(make)

#### Using collect with builds

One of the useful features supported in ruff is the collect() function,
which lets us collect files to work on, for example a list of .scss files
to compile into .css.

Sometimes we also need to support mass combine command line options like
typescript compiles of 'tsc --out blah.js one.ts two.ts three.ts'.

There's no really great way of supporting all of these options without
making the runner extremely complex; as such the logic for it must be
done on the collect call, so that it works with the build scope (chdir).

For example, to run a command on each collected item:

    def collection(matches, run):
      for path in matches:
        run('lessc', path)

    build.collect('.*\.less$', collection)

Or to combine all the .ts files:

    def collection(matches, run):
      cmd = [tsc_path, '--out', 'output.ts.js'] + list(files)
      run(*cmd)

    build.collect('.*\.ts$', collection)

### Runners:

Sometimes its useful to have a ruff runner that starts a bunch of
things rather than watching them itself. For example, the sass compiler,
or running a local websocket service AND a webserver at the same time.

Use:

    import ruff as r
    r.command(r.path(__file__, 'bin', 'py'), '-m', 'mything.socket.service')
    r.serve('localhost', '8080', r.path(__file__, 'static'))
    r.run()

### Usage:

To use ruff you create a ruff.py somewhere, which sets all of this stuff up.

    import ruff

    scss = ruff.target()
    scss.pattern("regex", "folder", recurse=True)

    rebuild_scss = ruff.build()
    rebuild_scss.run('scss', 'blah.scss', 'output.scss')

    redeploy = ruff.build()
    redeploy.run('rsync', 'here', 'there')

    ruff.bind(scss, rebuild_scss, redeploy)
    ruff.run()

### Server:

For dev purposes ruff comes with a built in webserver.

    import ruff

    ...

    run.serve('localhost', 6001, 'path_to_thing')

Never use this for anything important, obviously.

### Assets and paths:

It's often irritating to resolve paths. Ruff has a built in helper for this:

    import ruff

    # Paths
    scss_src_folder = ruff.path(__file__, 'src', 'css')
    scss_deploy_folder = ruff.path(__file__, 'app', 'static')
    scss_root = ruff.path(src_folder, 'styles.scss')
    scss_root_output = ruff.path(src_folder, 'styles.scss')

    # Deploy to server
    scss_deploy = ruff.build()
    scss_deploy.run('cp', scss_root_output, deploy_folder)

    # Watch css
    scss_target = ruff.target()
    scss_target.pattern('*.scss', src_folder, recurse=True)
    scss_target.pattern('*.css', src_folder, recurse=True)

    # run~
    ruff.bind(scss_target, scss_deploy)
    ruff.run(__file__)

### Testing

Testing ruff is slightly problematic. By nature ruff is a designed to
run until interrupt, but the callback on ruff.run() can be used to run
tests, like this:

    class Test(object):

      def __init__(self):
        self.delta = 0

      def callback(self, context, dt):
        self.delta += dt
        if self.delta > 1.0:
          self.remove_thing()
        elif self.delta > 5.0:
          return False
        return True # <-- Return true to keep running.

      def remove_thing(self):
        if os.path.exists('targets/blah.h'):
          os.unlink('targets/blah.h')

    test = Test()
    ruff.run(__file__, callback=test.callback)

### Dependencies

Ruff is largely stand-alone, but requires Flask to run a local server.
If flask is not installed in the local python context ruff will warn,
and not start the server.

### Api reference:

#### ruff

    - ruff.serve(host, port, folder)
    Set ruff to run local flask static content server for the given folder.
    NB. The server will not actually start until ruff.run() is called.

    - ruff.command(blah, blah, ...)
    Run a local command when ruff.run() is called. The command does not
    block and runs in a background process, which can be long running.
    Notice that sequential commands are run in parallel, not in order.

    - ruff.bind(target, build, build, build)
    Bind a watcher to a set of build operations of arbitrary length.

    - ruff.path(file, segment, segment, ...)
    Given the finite file 'file' (use __file__ typically) this will return
    the absolute path segment/segment/... relative to the given file.

    - ruff.run(file=None, callback=None, poll=0.1)
    Run ruff until it gets an interrupt signal, using dirname(file) as the
    current working context. If the callback is not None it is invoked every
    poll; the poll interval controls how often ruff polls for file changes.
    The default for file is the current working directory.

    - ruff.reset()
    Create a new ruff state object, if for some obscure reason it is required.

    - ruff.target(timeout=0)
    Create a ruff.Target and return it. If timeout is supplied, this target
    will only be invoked at most once every timeout seconds.

    - ruff.build()
    Create a ruff.Build and return it.

    - ruff.ANY
    Constant for any OS

    - ruff.WINDOWS
    Constant for windows based os

    - ruff.MAC
    Constant for mac based os

    - ruff.LINUX
    Constant for linux based os

#### ruff.Target

    - ruff.Target.pattern(regex, folder, recurse=False)
    Adds a target which triggers for any file in folder that matches the
    regex given. If recurse is set to true, the operation is recursive.

#### ruff.Build

    - ruff.Build.chdir(folder)
    Changes the current working folder. At the start of any build
    operation this is reset to the current working path.

    - ruff.Build.run(arg1, arg2, arg3..., os=ruff.ANY)
    Adds a build step that will run the arbitrary command given.
    Ruff provides trivial detection of os and runs build commands
    only for the given platform.

    - ruff.Build.command(function, os=ruff.ANY)
    Hook to allow any arbitrary function to be invoked when the
    build is triggered.

    - ruff.Build.collect(pattern, callback, recurse=False)
    We often need to invoke command operations to compile a group of files,
    like, turn all the .less files into .css files using lessc. An iterator
    of matches is passed to the callback during the build. See the examples;
    this is not the most obvious function to use.
