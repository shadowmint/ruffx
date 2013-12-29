import ruff as r

# Paths
path = lambda *x: r.path(*[__file__, '..', '..'] + list(x))
py = path('bin', 'py')
public_html = path('client', 'public')
ts_path = path('client', 'public', 'ts')
tsc_path = path('node_modules', 'typescript', 'bin', 'tsc.js')
scss_path = path('client', 'public', 'styles')

# TS build runner
def ts_build_invoke(files, run):
  cmd = ['node', tsc_path, '--out', 'output.ts.js'] + list(files)
  run(*cmd)

# TS build
def ts_build_config():
  return r.build().chdir(ts_path).collect('.*\.ts$', ts_build_invoke, recurse=True)

# SCSS build
def scss_build_config():
  return r.build().chdir(scss_path).run('sass', 'styles.scss', 'styles.css')

# Start client server
def main():

    # Typescript
    ts_build = ts_build_config()
    ts_targets = r.target(timeout=15)
    ts_targets.pattern('.*\.ts$', ts_path, recurse=True)
    r.bind(ts_targets, ts_build)

    # Sass
    scss_build = scss_build_config()
    scss_targets = r.target(timeout=15)
    scss_targets.pattern('.*\.scss$', scss_path, recurse=True)
    r.bind(scss_targets, scss_build)

    # Run local servers
    r.command(py, '-m', 'mc.core.main')
    r.serve('0.0.0.0', 3001, public_html)
    r.run()


if __name__ == '__main__':
    main()
