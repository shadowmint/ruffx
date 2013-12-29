from mc.server import ts_build_config, scss_build_config, path
import ruff as r

# Paths
bower = path('node_modules', 'bower', 'bin', 'bower')

# Rebuild target
def main():
  # Dependencies
  npm_install = r.build()
  npm_install.run('npm', 'install')
  npm_install.execute()

  # Source packages
  bower_install = r.build()
  bower_install.run('node', bower, 'install')
  bower_install.execute()

  # Typescript
  ts_build = ts_build_config()
  ts_build.execute()

  # Sass
  scss_build = scss_build_config()
  scss_build.execute()


if __name__ == '__main__':
  main()
